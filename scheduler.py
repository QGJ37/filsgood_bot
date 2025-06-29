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

        logging.debug("Sélection de la ville 'Brest'")
        select_element = wait_for_element(driver, By.ID, "ville")
        select = Select(select_element)
        select.select_by_visible_text("Brest")
        logging.info("Option 'Brest' sélectionnée.")
        time.sleep(1)

        for btn_text in [
            "Confirm", "Bien dormi(>8h)", "Aucune", "Aucun", "Aucune",
            "Aucune", "Aucun", "8h-16h", "En bonne forme"
        ]:
            click_next(driver, btn_text)

        logging.debug("Recherche du bouton 'Envoyer le formulaire'")
        submit_button = wait_for_element(
            driver, By.XPATH, "//input[@type='submit' and @value='Envoyer le formulaire']"
        )
        submit_button.click()
        logging.info("Clic sur le bouton 'Envoyer le formulaire' effectué.")
        time.sleep(1)

        send_telegram_alert("✅ Formulaire soumis avec succès !")

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
        today = datetime.datetime.now(tz=PARIS_TZ)
        weekday = today.weekday()

        if weekday >= 5:  # Samedi ou dimanche
            days_until_monday = (7 - weekday)
            next_monday = today + datetime.timedelta(days=days_until_monday)
            next_monday = next_monday.replace(hour=9, minute=0, second=0, microsecond=0)
            wait_time = (next_monday - today).total_seconds()
            logging.info(f"Weekend détecté. Attente jusqu'à lundi 9h Paris... (dans {wait_time:.0f} secondes)")
            time.sleep(wait_time)
            continue

        # Jours de semaine : tirage de 4 minutes aléatoires dans l'heure 9h-10h
        random_minutes = sorted(random.sample(range(60), 4))
        now = datetime.datetime.now(tz=PARIS_TZ)
        execution_times = [now.replace(hour=9, minute=m, second=0, microsecond=0) for m in random_minutes]
        execution_times = [t if t > now else t + datetime.timedelta(days=1) for t in execution_times]

        readable_times = [t.strftime("%H:%M") for t in execution_times]
        logging.info(f"Horaires choisis pour aujourd'hui (heure Paris) : {', '.join(readable_times)}")

        for i, exec_time in enumerate(execution_times, 1):
            now = datetime.datetime.now(tz=PARIS_TZ)
            wait_time = (exec_time - now).total_seconds()

            if wait_time > 0:
                logging.info(f"Attente de {wait_time:.0f} secondes avant exécution à {exec_time.strftime('%H:%M')} Paris...")
                time.sleep(wait_time)

            logging.info(f"--- Lancement du bot à {datetime.datetime.now(tz=PARIS_TZ).strftime('%H:%M:%S')} Paris (exécution {i}/4) ---")
            try:
                run_bot()
            except Exception as e:
                logging.error(f"Erreur lors de l'exécution du bot : {e}")
                send_telegram_alert(f"❌ Filsgood Bot : erreur à l'exécution {i} - {e}")

            time.sleep(60)  # Pause après exécution

        send_telegram_alert("✅ Filsgood Bot : les 4 exécutions journalières sont terminées avec succès.")

        # Attente jusqu'au lendemain 9h00
        next_day = datetime.datetime.now(tz=PARIS_TZ) + datetime.timedelta(days=1)
        next_start = next_day.replace(hour=9, minute=0, second=0, microsecond=0)
        wait_time = (next_start - datetime.datetime.now(tz=PARIS_TZ)).total_seconds()
        logging.info(f"Journée terminée. Attente jusqu'à demain 9h Paris... (dans {wait_time:.0f} secondes)")
        time.sleep(wait_time)

if __name__ == "__main__":
    logging.info("🚀 Démarrage du Filsgood Bot avec exécutions planifiées.")
    send_telegram_alert("🚀 Filsgood Bot a démarré.")
    
    try:
        logging.info("Exécution immédiate du bot au démarrage...")
        run_bot()
    except Exception as e:
        logging.error(f"Erreur lors de l'exécution immédiate : {e}")
    
    random_time_execution()

