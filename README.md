[![forthebadge](https://forthebadge.com/images/badges/cc-0.svg)](https://forthebadge.com) [!
[forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)]
(https://forthebadge.com) [![forthebadge](https://forthebadge.com/images/badges/uses-css.svg)]
(https://forthebadge.com)

# LitReview

![LITRevu](utilities/static/img/logo_black.png)

## Objectif
Ce programme est un exercice proposé par [OpenClassRooms](https://openclassrooms.com/fr/) dans le cadre de la formation :
Développeur d'applications Python. L'objectif est de développer une application web permettant aux utilisateurs de consulter ou de solliciter une critique de livres à la demande.

Cette application utilise Python, Django et Bootstrap.

## Fonctionnalités
L'application MVP LitReview permet de :
* -> s'inscrire en tant que nouvel utilisateur
* -> se connecter
* -> creer une demande de critique de livre ou d'article.
* -> publier une critique liée à une demande ou spontannée.
* -> modifier ou supprimer ses publications
* -> suivre les autres utilisateurs via un système d'abonnement.

## Technologie utilisée
* Le projet est développé avec le framework Django. 
* Les données sont sauvegardées dans une base de données sqlite3.

## Creation d'un environnement virtuel
* -> Télécharger le package de l'application depuis github : git clone https://github.com/Matthiiews/Project_9_LITRevu.git
* -> Creer un environnement virtuel : python -m venv .venv
* -> Activer l'environnement virtuel : .venv\Scripts\activate.bat
* -> Installer la dernière version de pip: python -m pip install --upgrade pip
* -> Installer les bibliothèques externes de Python: pip install -r requirements.txt

## Installation 
Ouvrir le terminal et exécutez les actions suivantes:

1. `git clone https://github.com/Matthiiews/Project_9_LITRevu.git
2. `cd LITRevu-project`
3. `python3 -m venv venv`
4. `. venv/bin/activate` on MacOS and Linux `venv\Scripts\activate` on Windows
5. `pip install -r requirements.txt`
6. `python manage.py runserver`

* -> Depuis votre navigateur, vous accédez à l'application via : http:/127.0.0.1:8000
* -> Créez un compte pour pouvoir vous connecter et accéder au site.
* -> Le mot de passe doit avoir au moins 8 caractères, des chiffres dans le désordre et des lettres. Il ne doit pas être commun.
* -> Pour accéder à l'administration de django: http://127.0.0.1:8000/admin
* -> Pour créer un nouvel administrateur dans le terminal: python manage.py createsuperuser

## Visualisation du projet
1. Page d'accueil avec lien pour s'inscrire et se connecter: <br>
![login](/README_images/login.png)

2. Après vous être inscrit ou connecté, vous serez redirigé vers les flux des données: <br>
![feeds](/README_images/feeds.png)

3. L'onglet suivant est : posts, où vous trouverez vos billets et vos commentaires: <br>
![posts](/README_images/posts.png)

4. Enfin, la page de l'abo, où se déroule la partie "Suivre" et "Ne plus suivre": <br>
![abo](/README_images/abo.png)

Si vous ne souhaitez pas vous inscrire, essayez les codes ci-dessous:<br>
username: Little <br>
password: S3cret01*