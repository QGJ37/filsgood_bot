# Projet Bot Selenium

Ce projet permet d'automatiser le remplissage d'un questionnaire en ligne à l'aide de Selenium et Docker.

## Prérequis

- Docker
- Docker Compose

## Installation

1. Clonez ce projet depuis GitHub :

    ```bash
    git clone https://github.com/ton-utilisateur/mon-projet.git
    cd mon-projet
    ```

2. Construisez l'image Docker :

    ```bash
    docker-compose build
    ```

3. Démarrez le bot :

    ```bash
    docker-compose up
    ```

Le bot s'exécutera 4 fois par jour entre 9h et 10h (heure de Paris) selon le planning défini dans le fichier `scheduler.py`.

## Déploiement avec Docker

1. Créez une image Docker pour le projet :
    ```bash
    docker build -t selenium-bot .
    ```

2. Lancez le conteneur Docker :
    ```bash
    docker run selenium-bot
    ```
