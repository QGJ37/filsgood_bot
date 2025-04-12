import logging
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration du logging vers fichier + stdout (visible dans Portainer)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/filsgood_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def wait_for_element(driver, by, value, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
        logging.info(f"Élément trouvé : {value}")
        return element
    except Exception as e:
        logging.error(f"Erreur lors de la recherche de l'élément {value} : {e}")
        raise

def click_next(driver, button_text):
    try:
        btn = wait_for_element(driver, By.XPATH, f"//button[contains(text(), '{button_text}')]")
        btn.click()
        logging.info(f"Clic sur le bouton '{button_text}' effectué.")
        time.sleep(1)
    except Exception as e:
        logging.error(f"Erreur lors du clic sur '{button_text}' : {e}")

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
        click_next(driver, "Voir resultat")

        logging.info("✅ Questionnaire complété avec succès.")

    except Exception as e:
        logging.error(f"❌ Erreur lors de la connexion ou de l'exécution du bot : {e}")

    finally:
        if driver:
            time.sleep(3)
            driver.quit()
            logging.info("Driver fermé.")
            
# Retirer cette ligne qui lance le bot immédiatement
# if __name__ == "__main__":
#     run_bot()  # Lancement immédiat du bot (pour le test)

