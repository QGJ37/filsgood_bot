import time
import random
import datetime
import logging
import sys
import os
import requests
from logging.handlers import RotatingFileHandler
from zoneinfo import ZoneInfo

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Configuration ---
PARIS_TZ = ZoneInfo("Europe/Paris")

# Utiliser un chemin persisté si volume monté (ex: /app/logs)
LOG_PATH = os.environ.get("FILSGOOD_LOG_PATH", "/app/filsgood_bot.log")

log_handler = RotatingFileHandler(LOG_PATH, maxBytes=10*1024*1024, backupCount=7)
log_handler.setLevel(logging.INFO)
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[log_handler, logging.StreamHandler(sys.stdout)]
)

# --- Helpers date/heure ---
def now_paris():
    return datetime.datetime.now(tz=PARIS_TZ)

def is_weekday_paris(dt=None) -> bool:
    dt = dt or now_paris()
    return dt.weekday() < 5  # Monday=0..Sunday=6, weekend>=5 [14]

def next_monday_9(dt=None) -> datetime.datetime:
    dt = dt or now_paris()
    weekday = dt.weekday()
    days_until_monday = (7 - weekday) % 7
    if days_until_monday == 0 and dt.hour >= 9:
        days_until_monday = 7
    target = dt + datetime.timedelta(days=days_until_monday)
    return target.replace(hour=9, minute=0, second=0, microsecond=0)

def next_weekday_9(dt=None) -> datetime.datetime:
    d = dt or now_paris()
    # avancer jusqu'à un jour ouvré à 09:00
    while d.weekday() >= 5:
        d = d + datetime.timedelta(days=1)
    return d.replace(hour=9, minute=0, second=0, microsecond=0)

def schedule_four_times_for_next_business_day(dt=None):
    base = dt or now_paris()
    # Si jour ouvré et avant 09:00, planifier pour aujourd'hui; sinon, prochain jour ouvré
    if is_weekday_paris(base) and base.hour < 9:
        target_day = base
    else:
        d = base + datetime.timedelta(days=1)
        while d.weekday() >= 5:
            d = d + datetime.timedelta(days=1)
        target_day = d
    random_minutes = sorted(random.sample(range(60), 4))
    execution_times = [
        target_day.replace(hour=9, minute=m, second=0, microsecond=0).astimezone(PARIS_TZ)
        for m in random_minutes
    ]
    return execution_times

# --- Telegram notifications ---
def send_telegram_alert(message):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        logging.error("❌ Variables TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID manquantes.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            logging.info("📲 Notification Telegram envoyée.")
        else:
            logging.error(f"Erreur Telegram : {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Erreur lors de l'envoi Telegram : {e}")

# --- Selenium helpers ---
def wait_presence(driver, by, value, timeout=20):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        logging.info(f"Élément trouvé : {value}")
        return element
    except Exception as e:
        logging.error(f"Erreur lors de la recherche de l'élément {value} : {e}")
        send_telegram_alert(f"❌ Erreur lors de la recherche de l'élément {value} : {e}")
        raise

def wait_clickable(driver, by, value, timeout=30):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        logging.info(f"Élément cliquable : {value}")
        return element
    except Exception as e:
        logging.error(f"Erreur sur élément cliquable {value} : {e}")
        send_telegram_alert(f"❌ Erreur sur élément cliquable {value} : {e}")
        raise

def click_by_xpath(driver, xpath, timeout=30, post_sleep=1.0):
    try:
        btn = wait_clickable(driver, By.XPATH, xpath, timeout=timeout)
        btn.click()
        logging.info(f"Clic sur le bouton XPath='{xpath}' effectué.")
        time.sleep(post_sleep)
    except Exception as e:
        logging.error(f"Erreur lors du clic XPath='{xpath}' : {e}")
        send_telegram_alert(f"❌ Erreur lors du clic XPath='{xpath}' : {e}")
        raise

# --- Sélecteurs robustes pour les boutons (texte normalisé) ---
X_CONFIRM = "//button[contains(normalize-space(.), 'Confirm')]"
# Tolérant aux variations d'encodage de '>' et espaces
X_BIEN_DORMI = ("//button[@name='id_button' and "
                "contains(normalize-space(.), 'Bien dormi') and contains(normalize-space(.), '8h')]")
X_AUCUNE = "//button[contains(normalize-space(.), 'Aucune')]"
X_AUCUN = "//button[contains(normalize-space(.), 'Aucun')]"
X_8H_16H = "//button[contains(normalize-space(.), '8h-16h')]"
X_EN_BONNE_FORME = "//button[contains(normalize-space(.), 'En bonne forme')]"
X_SUBMIT = "//input[@type='submit' and @value='Envoyer le formulaire']"

# --- Fonction principale du bot ---
def run_bot():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    logging.info("Tentative de connexion à Selenium Grid...")
    driver = None
    try:
        time.sleep(5)
        driver = webdriver.Remote(
            command_executor="http://filsgood_bot-selenium:4444/wd/hub",
            options=options
        )
        logging.info("Connexion réussie à Selenium.")

        driver.get("http://www.filgoods.iftl-ev.fr/")
        time.sleep(3)

        # Sélection ville
        select_element = wait_presence(driver, By.ID, "ville", timeout=30)
        select = Select(select_element)
        select.select_by_visible_text("Brest")
        logging.info("Option 'Brest' sélectionnée.")
        time.sleep(1)

        # Confirm
        click_by_xpath(driver, X_CONFIRM, timeout=30, post_sleep=0.8)

        # Synchronisation: attendre que le bouton de l'étape suivante soit cliquable
        # plutôt que de supposer qu'il est déjà là
        wait_clickable(driver, By.XPATH, X_BIEN_DORMI, timeout=30)

        # Chaîne de clics robustes
        click_by_xpath(driver, X_BIEN_DORMI, timeout=30)
        click_by_xpath(driver, X_AUCUNE, timeout=20)
        click_by_xpath(driver, X_AUCUN, timeout=20)
        click_by_xpath(driver, X_AUCUNE, timeout=20)
        click_by_xpath(driver, X_AUCUNE, timeout=20)
        click_by_xpath(driver, X_AUCUN, timeout=20)
        click_by_xpath(driver, X_8H_16H, timeout=20)
        click_by_xpath(driver, X_EN_BONNE_FORME, timeout=20)

        # Submit
        submit_button = wait_clickable(driver, By.XPATH, X_SUBMIT, timeout=30)
        submit_button.click()
        logging.info("Clic sur le bouton 'Envoyer le formulaire' effectué.")
        time.sleep(1)

    except Exception as e:
        logging.error(f"❌ Erreur lors de l'exécution du bot : {e}")
        send_telegram_alert(f"❌ Erreur dans Filsgood Bot : {e}")
        raise
    finally:
        if driver:
            time.sleep(3)
            driver.quit()
            logging.info("Driver fermé.")

# --- Gestion des horaires et exécutions ---
def random_time_execution():
    logging.info("Vérification de l'heure et du weekend avant exécution...")

    while True:
        now = now_paris()

        if not is_weekday_paris(now):
            next_start = next_monday_9(now)
            wait_time = (next_start - now).total_seconds()
            logging.info(f"Weekend détecté. Attente jusqu'à lundi 9h Paris... (dans {wait_time:.0f} secondes)")
            time.sleep(max(wait_time, 0))
            continue

        execution_times = schedule_four_times_for_next_business_day(now)
        readable_times = [t.strftime("%H:%M") for t in execution_times]
        logging.info(f"Horaires choisis (heure Paris) : {', '.join(readable_times)}")

        for i, exec_time in enumerate(execution_times, 1):
            now = now_paris()
            wait_time = (exec_time - now).total_seconds()
            if wait_time > 0:
                logging.info(f"Attente de {wait_time:.0f} secondes avant exécution à {exec_time.strftime('%H:%M')} Paris...")
                time.sleep(wait_time)

            if not is_weekday_paris(now_paris()):
                logging.info("Créneau atteint un week-end: exécution sautée.")
                continue

            logging.info(f"--- Lancement du bot à {now_paris().strftime('%H:%M:%S')} Paris (exécution {i}/4) ---")
            try:
                run_bot()
            except Exception as e:
                logging.error(f"Erreur lors de l'exécution du bot : {e}")
                send_telegram_alert(f"❌ Filsgood Bot : erreur à l'exécution {i} - {e}")

            time.sleep(60)  # Pause après exécution

        # Attendre jusqu'au prochain jour ouvré 9h
        now = now_paris()
        start_next = next_weekday_9(now)
        wait_time = (start_next - now).total_seconds()
        logging.info(f"Journée terminée. Attente jusqu'au prochain jour ouvré 9h Paris... (dans {wait_time:.0f} secondes)")
        time.sleep(max(wait_time, 0))

if __name__ == "__main__":
    logging.info("🚀 Démarrage du Filsgood Bot avec exécutions planifiées.")
    send_telegram_alert("🚀 Filsgood Bot a démarré.")

    try:
        if is_weekday_paris():
            logging.info("Exécution immédiate du bot au démarrage...")
            run_bot()
        else:
            logging.info("Démarrage un week-end: exécution immédiate ignorée.")
    except Exception as e:
        logging.error(f"Erreur lors de l'exécution immédiate : {e}")

    random_time_execution()

