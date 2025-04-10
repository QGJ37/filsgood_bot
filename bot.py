from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def wait_for_element(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))

def click_next(driver, button_text):
    try:
        btn = wait_for_element(driver, By.XPATH, f"//button[contains(text(), '{button_text}')]")
        btn.click()
        time.sleep(1)
    except Exception as e:
        print(f"Erreur lors du clic sur '{button_text}':", e)

def run_bot():
    options = Options()
    options.add_argument("--headless")  # Mode headless pour éviter l'interface graphique
    options.add_argument("--disable-gpu")  # Option pour éviter des erreurs liées au GPU
    options.add_argument("--no-sandbox")  # Utilisé souvent dans des environnements Docker
    # options.add_argument("--start-maximized")  # À supprimer pour headless

    driver = webdriver.Remote(
        command_executor="http://selenium/wd/hub",  # Connexion à Selenium Grid
        desired_capabilities={'browserName': 'chrome'}
    )

    try:
        driver.get("http://www.filgoods.iftl-ev.fr/")
        time.sleep(3)

        # Sélectionner Brest
        select_element = wait_for_element(driver, By.TAG_NAME, "select")
        select = Select(select_element)
        select.select_by_visible_text("Brest")
        time.sleep(1)

        # Étapes successives
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

        print("✅ Questionnaire complété avec succès.")

    except Exception as e:
        print("❌ Erreur :", e)

    finally:
        time.sleep(3)  # Petite pause pour voir le résultat
        driver.quit()
