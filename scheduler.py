import time
import logging
import random
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import telegram
import os
from zoneinfo import ZoneInfo

print(">>> Démarrage du bot <<<")  # Trace de démarrage

# Configuration Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Fuseau horaire Paris
PARIS_TZ = ZoneInfo("Europe/Paris")

# Configuration logging
log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
log_handler = RotatingFileHandler("bot.log", maxBytes=2000000, backupCount=3)
log_handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

def send_telegram_alert(message):
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.info("📲 Notification Telegram envoyée.")
    except Exception as e:
        logging.error(f"Erreur d'envoi Telegram : {e}")

def wait_for_element(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))

def click_next(driver, button_text):
    try:
        button = wait_for_element(driver, By.XPATH, f"//button[contains(text(), '{button_text}')]")
        button.click()
        logging.info(f"Clic sur le bouton '{button_text}' effectué.")
        time.sleep(1)
    except Exception as e:
        logging.error(f"Erreur lors du clic sur '{button_text}' : {e}")
        send_telegram_alert(f"❌ Erreur lors du clic sur '{button_text}' : {e}")
        raise

def run_bot():
    print(">>> Entrée dans run_bot <<<")  # Trace run_bot
    send_telegram_alert("🚀 Lancement du bot en cours...")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = None

    try:
        driver = webdriver.Remote(
            command_executor="http://filsgood_bot-selenium:4444/wd/hub",
            options=options
        )

        driver.get("http://www.filgoods.iftl-ev.fr/")
        time.sleep(3)

        select_element = wait_for_element(driver, By.ID, "ville")
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

        try:
            submit_button = wait_for_element(
                driver, By.XPATH, "//input[@type='submit' and @value='Envoyer le formulaire']"
            )
            submit_button.click()
            logging.info("Clic sur le bouton 'Envoyer le formulaire' effectué.")
            time.sleep(1)
        except Exception as e:
            logging.error(f"Erreur lors du clic sur 'Envoyer le formulaire' : {e}")
            send_telegram_alert(f"❌ Erreur lors du clic final : {e}")
            raise

        send_telegram_alert("✅ Formulaire soumis avec succès !")

    except Exception as e:
        logging.error(f"❌ Erreur lors de la connexion ou de l'exécution du bot : {e}")
        send_telegram_alert(f"❌ Erreur générale du bot : {e}")
    finally:
        if driver:
            driver.quit()
            logging.info("Driver fermé.")

def scheduler_loop():
    logging.info("Démarrage du scheduler avec exécution immédiate et planifications.")

    # Exécution immédiate au lancement du script
    logging.info("--- Exécution immédiate du bot au lancement du script ---")
    run_bot()

    while True:
        now = datetime.now(tz=PARIS_TZ)
        weekday = now.weekday()

        # Gestion weekend : on attend jusqu'à lundi 9h
        if weekday >= 5:  # samedi=5, dimanche=6
            days_until_monday = (7 - weekday)
            next_monday = now + timedelta(days=days_until_monday)
            next_monday = next_monday.replace(hour=9, minute=0, second=0, microsecond=0)
            wait_seconds = (next_monday - now).total_seconds()
            logging.info(f"Weekend détecté, attente jusqu'à lundi 9h Paris ({wait_seconds:.0f}s)...")
            time.sleep(wait_seconds)
            continue

        # En semaine : planification 4 fois entre 9h00-9h59 (minutes aléatoires)
        random_minutes = sorted(random.sample(range(60), 4))
        exec_times = [now.replace(hour=9, minute=m, second=0, microsecond=0) for m in random_minutes]
        exec_times = [t if t > now else t + timedelta(days=1) for t in exec_times]

        readable_times = ", ".join(t.strftime("%H:%M") for t in exec_times)
        logging.info(f"Horaires d'exécution planifiés aujourd'hui (heure Paris) : {readable_times}")

        for i, exec_time in enumerate(exec_times, start=1):
            now = datetime.now(tz=PARIS_TZ)
            wait_seconds = (exec_time - now).total_seconds()

            if wait_seconds > 0:
                logging.info(f"Attente {wait_seconds:.0f}s avant exécution à {exec_time.strftime('%H:%M')} Paris...")
                time.sleep(wait_seconds)

            logging.info(f"--- Exécution {i} du bot à {datetime.now(tz=PARIS_TZ).strftime('%H:%M:%S')} Paris ---")
            run_bot()
            time.sleep(60)  # Pause post-exécution

        # Après les 4 exécutions, envoi d’un message Telegram de récapitulatif
        send_telegram_alert("✅ Toutes les exécutions du jour ont été réalisées avec succès !")

        # Fin de journée : attendre jusqu'au lendemain 9h
        next_day = datetime.now(tz=PARIS_TZ) + timedelta(days=1)
        next_start = next_day.replace(hour=9, minute=0, second=0, microsecond=0)
        wait_seconds = (next_start - datetime.now(tz=PARIS_TZ)).total_seconds()
        logging.info(f"Journée terminée. Attente jusqu'à demain 9h Paris ({wait_seconds:.0f}s)...")
        time.sleep(wait_seconds)

if __name__ == "__main__":
    print(">>> Entrée dans main <<<")  # Trace main
    try:
        scheduler_loop()
    except Exception as e:
        logging.error(f"Erreur fatale dans scheduler_loop : {e}")
