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

log_handler = RotatingFileHandler('/app/filsgood_bot.log', maxBytes=10*1024*1024, backupCount=7)
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
    # Monday=0 .. Sunday=6 ; weekend si >=5
    return dt.weekday() < 5  # True = lundi..vendredi
    # Réf: datetime.weekday() mapping Monday=0..Sunday=6 [1]

def next_weekday(dt=None) -> datetime.datetime:
    """Retourne le prochain datetime (Paris) qui est un jour de semaine à 09:00."""
    dt = dt or now_paris()
    d = dt
    # avancer au prochain jour ouvré si weekend
    while d.weekday() >= 5:
        d = d + datetime.timedelta(days=1)
    return d.replace(hour=9, minute=0, second=0, microsecond=0)

def next_monday_9(dt=None) -> datetime.datetime:
    dt = dt or now_paris()
    weekday = dt.weekday()
    # jours à ajouter jusqu'au lundi
    days_until_monday = (7 - weekday) % 7
    if days_until_monday == 0 and dt.hour >= 9:
        days_until_monday = 7
    target = dt + datetime.timedelta(days=days_until_monday)
    return target.replace(hour=9, minute=0, second=0, microsecond=0)

def schedule_four_times_for_next_business_day(dt=None):
    """
    Tire 4 minutes aléatoires dans [0..59] pour le prochain jour ouvré (Paris) à l'heure 9h,
    et renvoie la liste des datetime d'exécution ce jour-là entre 09:00 et 10:00.
    Ne pousse jamais au 'lendemain' si cela tomberait samedi/dimanche.
    """
    base = dt or now_paris()
    # jour cible = aujourd'hui si c'est un jour ouvré et avant 9h, sinon prochain jour ouvré
    if is_weekday_paris(base) and base.hour < 9:
        target_day = base
    else:
        # si on est après 9h un jour ouvré OU un weekend, viser prochain jour ouvré
        d = base
        while d.weekday() >= 5 or (d.weekday() < 5 and d.hour >= 9):
            d = d + datetime.timedelta(days=1)
        target_day = d

    # S'assurer que c'est bien un jour ouvré
    while target_day.weekday() >= 5:
        target_day = target_day + datetime.timedelta(days=1)

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
def wait_for_element(driver, by, value, timeout=10):
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

def click_next(driver, button_text):
    try:
        btn = wait_for_element(driver, By.XPATH, f"//button[contains(text(), '{button_text}')]")
        btn.click()
        logging.info(f"Clic sur le bouton '{button_text}' effectué.")
        time.sleep(1)
    except Exception as e:
        logging.error(f"Erreur lors du clic sur '{button_text}' : {e}")
        send_telegram_alert(f"❌ Erreur lors du clic sur '{button_text}' : {e}")
        raise

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

        select_element = wait_for_element(driver, By.ID, "ville")
        select = Select(select_element)
        select.select_by_visible_text("Brest")
        logging.info("Option 'Brest' sélectionnée.")
        time.sleep(1)

        for btn_text in [
            "Confirm", "Bien dormi(&gt;8h)", "Aucune", "Aucun", "Aucune",
            "Aucune", "Aucun", "8h-16h", "En bonne forme"
        ]:
            click_next(driver, btn_text)

        submit_button = wait_for_element(
            driver, By.XPATH, "//input[@type='submit' and @value='Envoyer le formulaire']"
        )
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

        # Si week-end: dormir jusqu'à lundi 9h
        if not is_weekday_paris(now):
            next_start = next_monday_9(now)
            wait_time = (next_start - now).total_seconds()
            logging.info(f"Weekend détecté. Attente jusqu'à lundi 9h Paris... (dans {wait_time:.0f} secondes)")
            time.sleep(max(wait_time, 0))
            continue

        # Génère les 4 créneaux pour le prochain jour ouvré entre 09:00 et 10:00
        execution_times = schedule_four_times_for_next_business_day(now)
        readable_times = [t.strftime("%H:%M") for t in execution_times]
        logging.info(f"Horaires choisis (heure Paris) : {', '.join(readable_times)}")

        for i, exec_time in enumerate(execution_times, 1):
            # Attente jusqu'au créneau
            now = now_paris()
            wait_time = (exec_time - now).total_seconds()
            if wait_time > 0:
                logging.info(f"Attente de {wait_time:.0f} secondes avant exécution à {exec_time.strftime('%H:%M')} Paris...")
                time.sleep(wait_time)

            # Double garde: ne jamais exécuter si c'est week-end au moment T
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
        start_next = next_weekday(now)
        if start_next <= now:
            # si déjà passé 9h aujourd'hui, passer au prochain jour ouvré
            start_next = next_weekday(now + datetime.timedelta(days=1))
        wait_time = (start_next - now).total_seconds()
        logging.info(f"Journée terminée. Attente jusqu'au prochain jour ouvré 9h Paris... (dans {wait_time:.0f} secondes)")
        time.sleep(max(wait_time, 0))

if __name__ == "__main__":
    logging.info("🚀 Démarrage du Filsgood Bot avec exécutions planifiées.")
    send_telegram_alert("🚀 Filsgood Bot a démarré.")

    try:
        # Garde: ne pas exécuter immédiatement si weekend
        if is_weekday_paris():
            logging.info("Exécution immédiate du bot au démarrage...")
            run_bot()
        else:
            logging.info("Démarrage un week-end: exécution immédiate ignorée.")
    except Exception as e:
        logging.error(f"Erreur lors de l'exécution immédiate : {e}")

    random_time_execution()
