import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import telegram

# --- CONFIG ---
TELEGRAM_TOKEN = "TON_BOT_TOKEN"
TELEGRAM_CHAT_ID = "TON_CHAT_ID"
REMOTE_URL = "http://localhost:4444/wd/hub"
URL_FORMULAIRE = "http://ton_site/formulaire"

# --- LOGGER ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- FONCTIONS UTILES ---
def send_telegram(message):
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.info("📲 Notification Telegram envoyée.")
    except Exception as e:
        logging.error(f"Erreur lors de l'envoi Telegram : {e}")

def find_element_safe(driver, by, value, timeout=10):
    try:
        elem = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
        logging.info(f"Élément trouvé : {value}")
        return elem
    except Exception as e:
        logging.error(f"Erreur lors de la recherche de l'élément {value} : {e}")
        return None

def clic_element(driver, by, value, label):
    elem = find_element_safe(driver, by, value)
    if elem:
        try:
            elem.click()
            logging.info(f"Clic sur le bouton '{label}' effectué.")
        except Exception as e:
            logging.error(f"Erreur lors du clic sur '{label}' : {e}")
    else:
        logging.error(f"Bouton '{label}' non trouvé.")

# --- SCRIPT PRINCIPAL ---
def run_bot():
    send_telegram("🚀 Lancement du bot en cours...")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # optionnel : pour ne pas afficher le navigateur
    try:
        driver = webdriver.Remote(command_executor=REMOTE_URL, options=options)
        driver.get(URL_FORMULAIRE)
        time.sleep(2)  # ajuster si besoin

        # Étapes du formulaire
        clic_element(driver, By.XPATH, "//button[contains(text(), '8h-16h')]", "8h-16h")
        clic_element(driver, By.XPATH, "//button[contains(text(), 'En bonne forme')]", "En bonne forme")

        # ✅ Nouvelle cible pour le bouton "Envoyer le formulaire"
        clic_element(driver, By.XPATH, "//input[@type='submit' and @value='Envoyer le formulaire']", "Envoyer le formulaire")

        send_telegram("✅ Formulaire soumis avec succès !")

    except Exception as e:
        logging.error(f"❌ Erreur lors de la connexion ou de l'exécution du bot : {e}")
        send_telegram(f"❌ Erreur pendant l'exécution du bot : {e}")
    finally:
        driver.quit()
        logging.info("Driver fermé.")

# --- LANCEMENT ---
if __name__ == "__main__":
    try:
        run_bot()
    except Exception as e:
        logging.error(f"Run_bot a échoué lors de l'exécution immédiate: {e}")
