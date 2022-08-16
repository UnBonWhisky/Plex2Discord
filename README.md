# PlexToDiscord
---
Ce script nécessite un Plex Pass car il utilise la fonction des webhooks incluse avec cette abonnement.

PlexToDiscord est un petit script Python utilisant l'API discord.py ainsi que les webhooks Plex Media Server, il permet de rendre un affichage d'ajout de film ou de série sur Plex.

Problème connu :
- Impossible de différencier l'ajout de plusieurs épisodes, d'une saison, ou d'une série complète. Tout sera reconnu comme étant considéré comme une série complète. Je ne peux malheureusement rien y faire (du moins, avec les webhooks) car c'est Plex directement qui gère ceci.

---
## Comment configurer le script ainsi que les webhooks :

### 1. Créer un Webhook sur discord :
  
Cliquez sur `Modifier le salon`  
![image](https://user-images.githubusercontent.com/65244389/184926967-6c7ddb5e-6b5a-4a8d-9ff0-531a5707d3c9.png)  
  
Puis sur `Intégrations` suivi de `Créer un webhook`  
![image](https://user-images.githubusercontent.com/65244389/184927035-0b8205d5-7713-4801-9d0e-60d6db15bb5a.png)  
![image](https://user-images.githubusercontent.com/65244389/184927089-584a7b47-f908-430e-8aeb-d2da191d3d1e.png)  
  
Puis sur `Copier l'URL du webhook`. Nous aurons besoin de ça  
![image](https://user-images.githubusercontent.com/65244389/184927120-2a591eb4-f4f4-4d9a-a14d-2af629c678f2.png)  
  
  
### 2. Récupérer un token Plex ainsi que créer le webhook
