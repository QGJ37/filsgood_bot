import time
import random
import datetime
import logging
from bot import run_bot  # On importe ici car il n'y a plus d'import croisé

# Configuration du logging vers fichier + stdout (visible dans Portainer)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/filsgood_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def random_time_execution(run_bot):
    logging.info("Exécution immédiate du bot lors du lancement du conteneur...")
    run_bot()
    time.sleep(60)

    while True:
        today = datetime.datetime.now()
        weekday = today.weekday()

        if weekday >= 5:
            days_until_monday = (7 - weekday)
            next_monday = today + datetime.timedelta(days=days_until_monday)
            next_monday = next_monday.replace(hour=9, minute=0, second=0, microsecond=0)
            wait_time = (next_monday - today).total_seconds()
            logging.info("Weekend détecté. Attente jusqu'à lundi 9h...")
            time.sleep(wait_time)
            continue

        random_minutes = sorted(random.sample(range(60), 4))
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
            run_bot()
            time.sleep(60)

        next_day = datetime.datetime.now() + datetime.timedelta(days=1)
        next_start = next_day.replace(hour=9, minute=0, second=0, microsecond=0)
        wait_time = (next_start - datetime.datetime.now()).total_seconds()
        logging.info("Journée terminée. Attente jusqu'à demain 9h...")
        time.sleep(wait_time)

if __name__ == "__main__":
    random_time_execution(run_bot)
