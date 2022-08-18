# PlexToDiscord
---
Ce script nécessite un Plex Pass car il utilise la fonction des webhooks incluse avec cet abonnement.

Vous devrez peut-être isntaller les librairies `flask` et `discord` avec pip pour que le script fonctionne. Dans ce cas, ouvrez un terminal / cmd puis tapez cette commande :  
Windows : `py -3 -m pip install flask discord.py`  
Linux : `python3 -m pip install flask discord.py`

PlexToDiscord est un petit script Python utilisant l'API discord.py ainsi que les webhooks Plex Media Server, il permet de rendre un affichage d'ajout de film ou de série sur Plex.

Problème connu :
- Impossible de différencier l'ajout de plusieurs épisodes, d'une saison, ou d'une série complète. Tout sera reconnu comme étant considéré comme une série complète. Je ne peux malheureusement rien y faire (du moins, avec les webhooks) car c'est Plex directement qui gère ceci.

-----
## Préparation des infos nécessaires à l'emploi :
---
### 1. Créer un Webhook sur discord :
  
Cliquez sur `Modifier le salon`  
![image](https://user-images.githubusercontent.com/65244389/184926967-6c7ddb5e-6b5a-4a8d-9ff0-531a5707d3c9.png)  
  
Puis sur `Intégrations` suivi de `Créer un webhook`  
![image](https://user-images.githubusercontent.com/65244389/184927035-0b8205d5-7713-4801-9d0e-60d6db15bb5a.png)  
![image](https://user-images.githubusercontent.com/65244389/184927089-584a7b47-f908-430e-8aeb-d2da191d3d1e.png)  
  
Puis sur `Copier l'URL du webhook`. Nous aurons besoin de ça  
![image](https://user-images.githubusercontent.com/65244389/184927120-2a591eb4-f4f4-4d9a-a14d-2af629c678f2.png)  
  
---
### 2. Récupérer un token Plex ainsi que créer le webhook

Cliquez sur les ... puis sur "Voir les informations"  
![image](https://user-images.githubusercontent.com/65244389/185386956-fd2d1e82-bfeb-4f7b-99ea-0cfc68544bb4.png)  

Maintenant sur "Voir le XML"  
![image](https://user-images.githubusercontent.com/65244389/185387531-2cc6a743-084a-489e-9635-f2fb7751238b.png)  

Maintenant, dans la barre URL, vous aurez en toute fin votre token, l'affichage ressemble à `X-Plex-Token=......`  
![image](https://user-images.githubusercontent.com/65244389/185387940-d7cc7790-afb2-4db6-9399-78a9c1015adc.png)  

Votre Token Plex est important pour récupérer les thumbnails (les posters) des images, donc gardez-le.
  
--- 
### 3. Ajouter les accès nécessaires à Plex pour envoyer les bons webhooks :
  
Allez dans les réglages de Plex, puis dans les paramètres généraux de votre serveur. Il faut activer les notifications Push (ne vous inquiétez pas, vous n'aurez aucune notification Push qui vous sera envoyée. C'est simplement pour activer l'evenement d'ajout de contenu sur le serveur)   
![image](https://user-images.githubusercontent.com/65244389/185389549-c335cfe5-42ee-4073-af35-d4818d1df591.png)  

Il faut également activer les Webhooks dans les réglages du serveur (toujours), mais dans la catégorie "Réseau"  
![image](https://user-images.githubusercontent.com/65244389/185390640-fc55057c-23cf-45a0-b911-b66077bc45d1.png)  
  
---
### 4. Ajouter votre lien webhook sur votre PC :

Allez maintenant sur les paramètres de votre compte puis ajoutez un nouveau webhook  
![image](https://user-images.githubusercontent.com/65244389/185391158-9655a5c5-4d71-4198-ab1c-7d4e9392d605.png)  

Le format du webhook doit être le suivant : `http://IP.De.La.Machine:5000/Plex`. L'IP de la machine étant celle qui recevra le webhook. Si c'est le serveur étant votre serveur Plex, ce sera `http://127.0.0.1:5000/Plex`, dans le cas contraire, si la machine qui réceptionnera le webhook est différente, il faudra mettre son adresse IP (exemple : votre serveur Plex a une IP `192.168.1.10`, et le PC contenant le script qui tournera a pour IP `192.168.1.11`, alors il faudra taper sur le site web `http://192.168.1.11/Plex`).
  
-----
## Modification du script pour chaque utilisateur :

Dans le script, vous devriez trouver aux lignes **9 à 11** les variables `baseurl`, `token`, `WEBHOOK_URL`.
Pour chaque variable, voici l'information que vous devrez entrer :  
- **baseurl** : lien du serveur Plex avec le port, si c'est la même machine qui fera tout, ce sera `http://127.0.0.1:32400`, dans le cas contraire, ce sera l'IP du serveur détenant PMS d'installé du style `http://192.168.1.10:32400`.
- **token** : le token Plex récupéré sur l'URL lors du point 2.
- **WEBHOOK_URL** : le lien du webhook récupéré sur votre channel discord

Une fois que vous avez entré toutes ces informations dans le script, vous pouvez le lancer et attendre, lors de l'ajout de contenu media, Plex enverra une requête à votre script puis lui s'occupera de renvoyer les informations sur votre serveur Discord.  

L'affichage ressemblera à ça :  
![image](https://user-images.githubusercontent.com/65244389/185395187-93b4121f-39ac-4636-be52-ee386cd1fb08.png)  

À vous de jouer !!
