# Étape 1 : Utiliser une image officielle de Python comme base
FROM python:3.9-slim

# Étape 2 : Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    libnss3 \
    libgdk-pixbuf2.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxrandr2 \
    libgdk-pixbuf2.0-0 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libnspr4 \
    libxtst6 \
    libxss1 \
    libxtst6 \
    libdbus-glib-1-2 \
    libglib2.0-0 \
    libfreetype6 \
    cron \
    && apt-get clean

# Étape 3 : Télécharger et installer Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb || apt-get -f install -y

# Étape 4 : Installer ChromeDriver
RUN CHROME_DRIVER_VERSION=`curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    wget -N https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip -d /usr/local/bin/ && \
    rm chromedriver_linux64.zip

# Étape 5 : Définir le répertoire de travail
WORKDIR /app

# Étape 6 : Copier le fichier requirements.txt et installer les dépendances Python
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Étape 7 : Copier le script du bot dans le conteneur
COPY bot.py /app/bot.py

# Étape 8 : Copier le fichier cron pour la planification
COPY cronfile /etc/cron.d/bot-cron

# Étape 9 : Appliquer les permissions nécessaires
RUN chmod 0644 /etc/cron.d/bot-cron

# Étape 10 : Démarrer cron en arrière-plan
CMD cron && tail -f /var/log/cron.log
