import logging
import sys
import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logging.handlers import RotatingFileHandler

# Logging avec rotation (10 Mo, 7 backups)
log_handler = RotatingFileHandler('/app/filsgood_bot.log', maxBytes=10*1024*1024, backupCount=7)
log_handler.setLevel(logging.DEBUG)  # Niveau DEBUG pour log détaillé
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        log_handler,
        logging.StreamHandler(sys.stdout)
    ]
)

# Notification Telegram
def send_telegram_alert(message):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        logging.error("❌ Variables TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID manquantes.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message
    }

    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            logging.info("📲 Notification Telegram envoyée.")
        else:
            logging.error(f"Erreur Telegram : {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Erreur lors de l'envoi Telegram : {e}")

# Attente d'un élément
def wait_for_element(driver, by, value, timeout=10):
    try:
        logging.debug(f"Attente élément {value} par {by} (timeout {timeout}s)")
        element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
        logging.info(f"Élément trouvé : {value}")
        return element
    except Exception as e:
        logging.error(f"Erreur lors de la recherche de l'élément {value} : {e}")
        send_telegram_alert(f"❌ Erreur lors de la recherche de l'élément {value} : {e}")
        raise

# Clic sur un bouton
def click_next(driver, button_text):
    try:
        logging.debug(f"Tentative clic sur bouton contenant '{button_text}'")
        btn = wait_for_element(driver, By.XPATH, f"//button[contains(text(), '{button_text}')]")
        btn.click()
        logging.info(f"Clic sur le bouton '{button_text}' effectué.")
        time.sleep(1)
    except Exception as e:
        logging.error(f"Erreur lors du clic sur '{button_text}' : {e}")
        send_telegram_alert(f"❌ Erreur lors du clic sur '{button_text}' : {e}")

# Routine principale du bot
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

    finally:
        if driver:
            time.sleep(3)
            driver.quit()
            logging.info("Driver fermé.")

# Lancement
if __name__ == "__main__":
    logging.info("🚀 Démarrage du Filsgood Bot.")
    send_telegram_alert("🚀 Filsgood Bot a démarré.")  # Test notification démarrage
    run_bot()
