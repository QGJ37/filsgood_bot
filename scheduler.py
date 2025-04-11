import random
import time
import datetime
from bot import run_bot  # Assurez-vous que `run_bot` est correctement importé

def random_time_execution():
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
        print(f"Attente de {wait_time} secondes avant d'exécuter le bot...")
        time.sleep(wait_time)

        # Appel à la fonction du bot
        run_bot()

        # Petite pause entre les exécutions (ajustez si nécessaire)
        time.sleep(60)

# Appeler la fonction pour lancer l'exécution
random_time_execution()
