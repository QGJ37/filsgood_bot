import time
import logging
import random
from datetime import datetime
from logging.handlers import RotatingFileHandler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import telegram

# Configuration Telegram
TELEGRAM_TOKEN = "TON_BOT_TOKEN"
TELEGRAM_CHAT_ID = "TON_CHAT_ID"

# Configuration logging
log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
log_handler = RotatingFileHandler("bot.log", maxBytes=2000000, backupCount=3)
log_handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

# Envoie une notification Telegram
def send_telegram_alert(message):
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.info("📲 Notification Telegram envoyée.")
    except Exception as e:
        logging.error(f"Erreur d'envoi Telegram : {e}")

# Attente explicite d’un élément
def wait_for_element(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))

# Fonction de clic générique sur un bouton (avec le texte affiché)
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

# Fonction principale
def run_bot():
    send_telegram_alert("🚀 Lancement du bot en cours...")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # à retirer si tu veux voir le navigateur
    driver = None

    try:
        driver = webdriver.Remote(
            command_executor="http://localhost:4444/wd/hub",
            options=options
        )

        driver.get("http://ton_site/formulaire")
        time.sleep(1)

        click_next(driver, "8h-16h")
        click_next(driver, "En bonne forme")

        # Clic spécifique sur le bouton "Envoyer le formulaire"
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

# Pour exécuter immédiatement sans scheduler
if __name__ == "__main__":
    try:
        run_bot()
    except Exception as e:
        logging.error(f"Run_bot a échoué lors de l'exécution immédiate: {e}")
