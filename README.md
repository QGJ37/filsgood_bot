
# Filsgood Bot

## Description

Ce projet est un bot automatisé qui remplit un questionnaire sur le site [Filsgood](http://www.filsgoods.iftl-ev.fr/) en utilisant Selenium. Le bot est conçu pour s'exécuter à des heures aléatoires entre 9h et 10h, du lundi au vendredi.

## Prérequis

Avant de commencer, assurez-vous d'avoir les outils suivants installés :

- Docker
- Docker Compose
- Portainer

## Installation

1. **Cloner le dépôt** :
   ```sh
   git clone https://github.com/QGJ37/filsgood_bot.git
   cd filsgood_bot
   ```

2. **Configurer Portainer** :
    - Assurez-vous que Portainer est installé et en cours d'exécution.
    - Connectez-vous à l'interface web de Portainer.

3. **Déployer le stack** :
    - Dans Portainer, allez dans l'onglet **"Stacks"**.
    - Cliquez sur **"Add stack"**.
    - Donnez un nom à votre stack (par exemple, `filsgood_bot`).
    - Dans le champ **"Repository URL"**, entrez l'URL du dépôt GitHub : `https://github.com/QGJ37/filsgood_bot.git`.
    - Cliquez sur **"Deploy the stack"**.

## Configuration

Le fichier `docker-compose.yml` est configuré pour lancer deux services :

- **Selenium** : Un conteneur Selenium avec Chrome.
- **Bot** : Un conteneur Python qui exécute le bot.

### Variables d'environnement

Vous pouvez configurer les variables d'environnement dans le fichier `docker-compose.yml` si nécessaire.

## Utilisation

Une fois le stack déployé, le bot sera exécuté immédiatement et suivra la logique d'exécution planifiée :

- Exécution immédiate lors du lancement du conteneur.
- Exécution 4 fois entre 9h et 10h, du lundi au vendredi.

## Logs

Les logs du bot sont enregistrés dans les fichiers suivants :

- `/app/filsgood_bot.log` : Logs principaux du bot.
- `/app/filsgood_bot_scheduler.log` : Logs du scheduler.

Vous pouvez consulter ces logs via l'interface de Portainer.

## Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le dépôt.
2. Créez une branche pour votre feature (ex : `git checkout -b feature/foo`).
3. Committez vos modifications (ex : `git commit -am 'Add some foo'`).
4. Pushez la branche (ex : `git push origin feature/foo`).
5. Créez une Pull Request.

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Contact

Pour toute question ou suggestion, n'hésitez pas à ouvrir une issue ou à me contacter directement.

Merci d'utiliser **Filsgood Bot** !
