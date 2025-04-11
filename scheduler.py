import random
import time
import datetime
import logging

# Configuration du logging vers fichier + stdout (visible dans Portainer)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/filsgood_bot_scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def random_time_execution(run_bot):
    # Exécution 4 fois entre 9h et 10h, du lundi au vendredi
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
