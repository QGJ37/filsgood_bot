import time
import random
import datetime
import logging
from bot import run_bot
from logging.handlers import RotatingFileHandler
import sys
from zoneinfo import ZoneInfo  # Import pour timezone

# Fuseau horaire Paris
PARIS_TZ = ZoneInfo("Europe/Paris")

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
        today = datetime.datetime.now(tz=PARIS_TZ)
        weekday = today.weekday()

        if weekday >= 5:  # Weekend
            days_until_monday = (7 - weekday)
            next_monday = today + datetime.timedelta(days=days_until_monday)
            next_monday = next_monday.replace(hour=9, minute=0, second=0, microsecond=0)
            wait_time = (next_monday - today).total_seconds()
            logging.info(f"Weekend détecté. Attente jusqu'à lundi 9h Paris... (dans {wait_time:.0f} secondes)")
            time.sleep(wait_time)
            continue

        # Semaine
        random_minutes = sorted(random.sample(range(60), 4))
        now = datetime.datetime.now(tz=PARIS_TZ)
        execution_times = [now.replace(hour=9, minute=m, second=0, microsecond=0) for m in random_minutes]
        execution_times = [t if t > now else t + datetime.timedelta(days=1) for t in execution_times]

        readable_times = [t.strftime("%H:%M") for t in execution_times]
        logging.info(f"Horaires choisis pour aujourd'hui (heure Paris) : {', '.join(readable_times)}")

        for exec_time in execution_times:
            now = datetime.datetime.now(tz=PARIS_TZ)
            wait_time = (exec_time - now).total_seconds()

            if wait_time > 0:
                logging.info(f"Attente de {wait_time:.0f} secondes avant exécution à {exec_time.strftime('%H:%M')} Paris...")
                time.sleep(wait_time)

            logging.info(f"--- Lancement du bot à {datetime.datetime.now(tz=PARIS_TZ).strftime('%H:%M:%S')} Paris ---")
            run_bot()
            time.sleep(60)

        next_day = datetime.datetime.now(tz=PARIS_TZ) + datetime.timedelta(days=1)
        next_start = next_day.replace(hour=9, minute=0, second=0, microsecond=0)
        wait_time = (next_start - datetime.datetime.now(tz=PARIS_TZ)).total_seconds()
        logging.info(f"Journée terminée. Attente jusqu'à demain 9h Paris... (dans {wait_time:.0f} secondes)")
        time.sleep(wait_time)

if __name__ == "__main__":
    random_time_execution(run_bot)
