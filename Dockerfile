# Utiliser une image de base Python légère
FROM python:3.9-slim

# Mettre à jour le package manager et installer les dépendances nécessaires
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg2 \
    ca-certificates \
    libx11-dev \
    libxext6 \
    libxi6 \
    libgdk-pixbuf2.0-0 \
    libgconf-2-4 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libasound2 \
    libdbus-glib-1-2 \
    libxtst6 \
    libpng16-16 \
    libglib2.0-0 \
    fonts-liberation \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Télécharger Google Chrome
RUN curl -sSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o google-chrome-stable_current_amd64.deb

# Vérifier si le fichier a bien été téléchargé
RUN ls -l google-chrome-stable_current_amd64.deb

# Installer Google Chrome stable
RUN dpkg -i google-chrome-stable_current_amd64.deb || apt-get install -y -f

# Vérifier que l'exécutable de Chrome est bien installé et dans le PATH
RUN which google-chrome-stable
RUN google-chrome-stable --version || echo "Google Chrome n'est pas installé correctement."

# Télécharger et installer ChromeDriver
RUN CHROME_VERSION=$(google-chrome-stable --version | sed 's/Google Chrome //') \
    && CHROME_DRIVER_VERSION=$(curl -sSL https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION%.*}) \
    && wget https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip -d /usr/local/bin/ \
    && rm chromedriver_linux64.zip

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt et installer les dépendances Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copier tous les fichiers du projet dans le conteneur
COPY . /app/

# Copier le fichier cronfile et ajouter les tâches cron
COPY cronfile /etc/cron.d/filsgood-cron

# Donner les bonnes permissions au fichier cron et appliquer les tâches cron
RUN chmod 0644 /etc/cron.d/filsgood-cron \
    && crontab /etc/cron.d/filsgood-cron

# Exécuter cron en mode foreground
CMD ["cron", "-f"]
