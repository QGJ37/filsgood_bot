import time
import random
import datetime
import logging
import sys
import os
import requests
from zoneinfo import ZoneInfo

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logging.handlers import RotatingFileHandler

# === Configuration fuseau horaire ===
PARIS_TZ = ZoneInfo("Europe/Paris")

# === Logging avec rotation ===
log_handler = RotatingFileHandler('/app/filsgood_bot.log', maxBytes=10*1024*1024, backupCount=7)
log_handler.setLevel(logging.INFO)
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        log_handler,
        logging.StreamHandler(sys.stdout)
    ]
)

# === Notifications Telegram ===
def send_telegram_alert(message: str):
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

# === Helpers Selenium ===
def wait_for_element(driver, by, value, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
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

# === Routine principale du bot ===
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

        select_element = wait_for_element(driver, By.TAG_NAME, "select")
        select = Select(select_element)
        select.select_by_visible_text("Brest")
        logging.info("Option 'Brest' sélectionnée.")
        time.sleep(1)

        click_next(driver, "Confirm")
        click_next(driver, "Bien dormi(>8h)")
        click_next(driver, "Aucune")
        click_next(driver, "Aucun")
        click_next(driver, "Aucune")
        click_next(driver, "Aucune")
        click_next(driver, "Aucun")
        click_next(driver, "8h-16h")
        click_next(driver, "En bonne forme")
        click_next(driver, "Envoyer le formulaire")

        logging.info("✅ Questionnaire complété avec succès.")

    except Exception as e:
        logging.error(f"❌ Erreur lors de la connexion ou de l'exécution du bot : {e}")
        send_telegram_alert(f"❌ Erreur dans Filsgood Bot : {e}")
        raise

    finally:
        if driver:
            time.sleep(3)
            driver.quit()
            logging.info("Driver fermé.")

# === Scheduler principal ===
def random_time_execution(run_bot_func):
    success_count = 0
    error_count = 0

    # Exécution immédiate au lancement
    logging.info("Exécution immédiate du bot au démarrage.")
    try:
        run_bot_func()
        success_count += 1
    except Exception as e:
        error_count += 1
        logging.error(f"Run_bot a échoué lors de l'exécution immédiate: {e}")

    while True:
        now = datetime.datetime.now(tz=PARIS_TZ)
        weekday = now.weekday()

        if weekday >= 5:  # Weekend : pause jusqu'à lundi 9h
            days_until_monday = (7 - weekday)
            next_monday = now + datetime.timedelta(days=days_until_monday)
            next_monday = next_monday.replace(hour=9, minute=0, second=0, microsecond=0)
            wait_sec = (next_monday - now).total_seconds()
            logging.info(f"Weekend détecté. Mise en pause jusqu'à lundi 9h ({wait_sec:.0f}s)...")
            # Suppression notification Telegram pendant weekend
            time.sleep(wait_sec)
            continue

        # Génère 4 heures d'exécution aléatoires entre 9h00 et 9h59
        random_minutes = sorted(random.sample(range(60), 4))
        execution_times = [now.replace(hour=9, minute=m, second=0, microsecond=0) for m in random_minutes]
        # Si une heure est passée, on la décale au lendemain
        execution_times = [t if t > now else t + datetime.timedelta(days=1) for t in execution_times]

        readable_times = ", ".join(t.strftime("%H:%M") for t in execution_times)
        logging.info(f"Heures d'exécution aujourd'hui : {readable_times}")

        # Heure du résumé quotidien à 20h
        report_hour = now.replace(hour=20, minute=0, second=0, microsecond=0)
        if now > report_hour:
            report_hour += datetime.timedelta(days=1)

        for exec_time in execution_times:
            now = datetime.datetime.now(tz=PARIS_TZ)
            wait_sec = (exec_time - now).total_seconds()
            if wait_sec > 0:
                logging.info(f"Attente {wait_sec:.0f}s avant exécution à {exec_time.strftime('%H:%M')}")
                time.sleep(wait_sec)

            logging.info(f"--- Lancement du bot à {datetime.datetime.now(tz=PARIS_TZ).strftime('%H:%M:%S')} ---")
            try:
                run_bot_func()
                success_count += 1
            except Exception as e:
                error_count += 1
                logging.error(f"Run_bot a échoué: {e}")

            time.sleep(60)  # Pause après chaque exécution

            # Check si on est passé à l'heure du résumé (20h)
            now = datetime.datetime.now(tz=PARIS_TZ)
            if now >= report_hour:
                message = (
                    f"📊 Résumé quotidien Filsgood Bot - {now.strftime('%Y-%m-%d')} :\n"
                    f"✅ Succès : {success_count}\n"
                    f"❌ Erreurs : {error_count}"
                )
                send_telegram_alert(message)
                # Reset compteurs pour le prochain jour
                success_count = 0
                error_count = 0
                # Calcul attente jusqu'au lendemain 9h
                next_day = now + datetime.timedelta(days=1)
                next_start = next_day.replace(hour=9, minute=0, second=0, microsecond=0)
                wait_sec = (next_start - now).total_seconds()
                logging.info(f"Résumé envoyé. Mise en pause jusqu'à demain 9h ({wait_sec:.0f}s)...")
                time.sleep(wait_sec)
                break

        # Si on n'a pas encore envoyé le résumé, on attend jusqu'au lendemain 9h
        now = datetime.datetime.now(tz=PARIS_TZ)
        if now < report_hour:
            next_day = now + datetime.timedelta(days=1)
            next_start = next_day.replace(hour=9, minute=0, second=0, microsecond=0)
            wait_sec = (next_start - now).total_seconds()
            logging.info(f"Journée terminée. Mise en pause jusqu'à demain 9h ({wait_sec:.0f}s)...")
            time.sleep(wait_sec)


if __name__ == "__main__":
    logging.info("🚀 Démarrage du Filsgood Bot avec scheduler.")
    send_telegram_alert("🚀 Filsgood Bot a démarré avec scheduler.")
    random_time_execution(run_bot)
