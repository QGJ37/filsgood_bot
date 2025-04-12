import time
import random
import datetime
import logging
from bot import run_bot  # On importe ici car il n'y a plus d'import croisé
from logging.handlers import RotatingFileHandler
import sys

# Configuration du logging avec rotation des logs
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

def random_time_execution(run_bot):
    logging.info("Vérification de l'heure et du weekend avant exécution...")

    while True:
        today = datetime.datetime.now()
        weekday = today.weekday()

        if weekday >= 5:  # Si c'est le weekend (samedi ou dimanche)
            days_until_monday = (7 - weekday)
            next_monday = today + datetime.timedelta(days=days_until_monday)
            next_monday = next_monday.replace(hour=9, minute=0, second=0, microsecond=0)
            wait_time = (next_monday - today).total_seconds()
            logging.info(f"Weekend détecté. Attente jusqu'à lundi 9h... (dans {wait_time} secondes)")
            time.sleep(wait_time)  # Attente jusqu'à lundi matin à 9h
            continue  # Reprendre la boucle après le weekend

        # Pendant la semaine (lundi à vendredi)
        random_minutes = sorted(random.sample(range(60), 4))  # Générer des minutes aléatoires pour les exécutions
        now = datetime.datetime.now()
        execution_times = [now.replace(hour=9, minute=m, second=0, microsecond=0) for m in random_minutes]
        execution_times = [t if t > now else t + datetime.timedelta(days=1) for t in execution_times]

        readable_times = [t.strftime("%H:%M") for t in execution_times]
        logging.info(f"Horaires choisis pour aujourd'hui : {', '.join(readable_times)}")

        for exec_time in execution_times:
            now = datetime.datetime.now()
            wait_time = (exec_time - now).total_seconds()

            if wait_time > 0:
                logging.info(f"Attente de {wait_time:.0f} secondes avant exécution à {exec_time.strftime('%H:%M')}...")
                time.sleep(wait_time)

            logging.info(f"--- Lancement du bot à {datetime.datetime.now().strftime('%H:%M:%S')} ---")
            run_bot()  # Exécution du bot à l'heure prévue
            time.sleep(60)

        # Attendre jusqu'au lendemain à 9h pour redémarrer la boucle
        next_day = datetime.datetime.now() + datetime.timedelta(days=1)
        next_start = next_day.replace(hour=9, minute=0, second=0, microsecond=0)
        wait_time = (next_start - datetime.datetime.now()).total_seconds()
        logging.info(f"Journée terminée. Attente jusqu'à demain 9h... (dans {wait_time} secondes)")
        time.sleep(wait_time)

if __name__ == "__main__":
    random_time_execution(run_bot)
