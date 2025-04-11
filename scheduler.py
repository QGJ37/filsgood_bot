import random
import time
import datetime
import logging
import sys  # Ajoutez cette ligne

# Configuration du logging vers fichier + stdout (visible dans Portainer)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/filsgood_bot_scheduler.log'),
        logging.StreamHandler(sys.stdout)  # sys doit être importé
    ]
)

def random_time_execution(run_bot):
    # Exécution immédiate du bot lors du lancement du conteneur
    logging.info("Exécution immédiate du bot lors du lancement du conteneur...")
    run_bot()
    time.sleep(60)  # Petite pause avant de commencer la logique d'exécution

    # Exécution 4 fois entre 9h et 10h, du lundi au vendredi
    while True:
        for _ in range(4):
            # Calcul de l'heure aléatoire
            random_minute = random.randint(0, 59)
            random_hour = 9  # 9h (dans la plage 9h-10h)

            # Calcul du délai jusqu'à l'heure aléatoire
            current_time = datetime.datetime.now()
            target_time = current_time.replace(hour=random_hour, minute=random_minute, second=0, microsecond=0)

            # Si l'heure cible est déjà passée aujourd'hui, fixer l'exécution pour le jour suivant
            if target_time < current_time:
                target_time += datetime.timedelta(days=1)

            # Attente avant d'exécuter le script
            wait_time = (target_time - current_time).total_seconds()
            logging.info(f"Attente de {wait_time} secondes avant d'exécuter le bot...")

            time.sleep(wait_time)

            # Appel à la fonction du bot
            logging.info("Exécution du bot...")
            run_bot()

            # Petite pause entre les exécutions
            time.sleep(60)

        # Attendre jusqu'au lundi suivant
        now = datetime.datetime.now()
        days_until_monday = (7 - now.weekday()) % 7
        next_monday = now + datetime.timedelta(days=days_until_monday)
        next_monday = next_monday.replace(hour=9, minute=0, second=0, microsecond=0)
        wait_time = (next_monday - now).total_seconds()
        logging.info(f"Attente jusqu'au lundi suivant à 9h...")
        time.sleep(wait_time)
