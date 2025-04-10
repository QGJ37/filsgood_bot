# Utilisation d'une image officielle Python comme base
FROM python:3.9-slim

# Installation des dépendances nécessaires pour Selenium et Chrome
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    libx11-dev \
    libxkbfile-dev \
    libgdk-pixbuf2.0-0 \
    libxcomposite1 \
    libxrandr2 \
    libgdk-pixbuf2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxss1 \
    libappindicator1 \
    libindicator7 \
    git \
    cron \
    --no-install-recommends

# Cloner le dépôt GitHub
RUN git clone https://github.com/QGJ37/filsgood_bot.git /app

# Se positionner dans le répertoire du projet
WORKDIR /app

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installer le ChromeDriver
RUN wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip -d /usr/local/bin
RUN rm chromedriver_linux64.zip

# Copier le fichier cronfile dans le conteneur
COPY cronfile /etc/cron.d/filsgood-cron
RUN chmod 0644 /etc/cron.d/filsgood-cron
RUN crontab /etc/cron.d/filsgood-cron

# Copier ton script bot.py dans le conteneur
COPY bot.py .

# Démarrer le cron à l'exécution du conteneur
CMD ["cron", "-f"]
