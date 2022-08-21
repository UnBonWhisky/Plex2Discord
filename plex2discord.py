import pprint
from flask import Flask, request, json
import requests
import discord

app = Flask(__name__)
pp = pprint.PrettyPrinter(indent=2)

baseurl = 'http://IP ICI:32400'
token = ''
WEBHOOK_URL = ""

@app.route('/Plex', methods=['GET','POST'])
def foo():
    data = json.loads(request.form['payload'])
    print(data['Metadata']['title'])
    if data['event'] == 'library.new' :
        # Si c'est un épisode :
        if data['Metadata']['type'] == 'episode' :
            DownloadImage(data['Metadata']['parentThumb'])
            Episode_Webhook(
                data['Metadata']['grandparentTitle'], #ShowName
                data['Metadata']['parentTitle'].replace('Season', 'Saison'), #SaisonEpisode
                data['Metadata']['index'], #NumeroEpisode
                data['Metadata']['summary'], #summary
                data['Metadata']['librarySectionTitle'], #Librairie
                data['Metadata']['grandparentRatingKey'], #ratingkeySaison
                data['Server']['uuid'], #serveruuid
                data['Metadata']['ratingKey'] #ratingkey
            )
        # Sinon c'est une saison, une série, ou un film
        else :
            # On vient check auprès des ajouts récents si ce qu'on a récupéré c'est un film ou une série, ou une saison
            export = Get_XML_Infos(data['Metadata']['title'], data['Metadata']['type'])
            # On télécharge le thumbnail
            DownloadImage(data['Metadata']['thumb'])
            # Si c'est une série
            if data['Metadata']['type'] == 'show' :
                # Si c'est une saison et pas une série entière
                if export is not None:
                    Movie_Show_Webhook(
                        data['Metadata']['title'], #Titre
                        export['year'], #year
                        export['summary'], #summary
                        export['videotype'], #videotype
                        data['Metadata']['librarySectionTitle'], #Librairie
                        data['Server']['uuid'], #serveruuid
                        export['ratingKey'], #ratingkey
                        export['title'] #saison
                    )
                # Dans ce cas, c'est une série entière
                else :
                    Movie_Show_Webhook(
                        data['Metadata']['title'], #Titre
                        data['Metadata']['year'], #year
                        data['Metadata']['summary'], #summary
                        data['Metadata']['type'], #videotype
                        data['Metadata']['librarySectionTitle'], #Librairie
                        data['Server']['uuid'], #serveruuid
                        data['Metadata']['ratingKey'], #ratingkey
                        None
                    )
            # Si c'est un film
            else :
                # Si l'export n'est pas vide
                if export is not None:
                    Movie_Show_Webhook(
                        data['Metadata']['title'], #Titre
                        export['year'], #year
                        export['summary'], #summary
                        export['videotype'], #videotype
                        data['Metadata']['librarySectionTitle'], #Librairie
                        data['Server']['uuid'], #serveruuid
                        export['ratingKey'], #ratingkey
                        None
                    )
                else :
                    Movie_Show_Webhook(
                        data['Metadata']['title'], #Titre
                        data['Metadata']['year'], #year
                        data['Metadata']['summary'], #summary
                        data['Metadata']['type'], #videotype
                        data['Metadata']['librarySectionTitle'], #Librairie
                        data['Server']['uuid'], #serveruuid
                        data['Metadata']['ratingKey'], #ratingkey
                        None
                    )

    return "OK"

def Get_XML_Infos(Titre, datatype):

    # On vient interroger le serveur pour avoir des infos sur ce qui a été nouvellement ajouté, puis on enregistre les infos de ce qui nous a été rendu
    url = f'{baseurl}/library/recentlyAdded?X-Plex-Token={token}'
    resp = requests.get(url)
    open('recentlyAdded.xml', 'wb').write(resp.content)

    # On vient lire le fichier et le mettons de façon utilisable et lisible par Python
    tree = ET.parse('recentlyAdded.xml')
    root = tree.getroot()

    number = 0

    # Si Plex nous a envoyé l'info que c'est une série
    if datatype == "show":
        # On vient interroger toutes les séries récemment ajoutées, et cherchons celui qui est intéressant
        DirectoryRoot = root.findall('Directory')
        SerieID = []
        index = 0
        # On vient garder en mémoire ceux dont le nom de la série reçue dans le webhook correspond avec le contenu récemment ajouté
        for directory in DirectoryRoot :
            if directory.get('parentTitle') == Titre :
                number += 1
                SerieID.append(index)
            index += 1

        # Si on a reçu qu'un seul nom de série / saison dans le lot
        if number == 1 :
            export = {
                'year' :  DirectoryRoot[SerieID[0]].attrib['parentYear'],
                'summary' : DirectoryRoot[SerieID[0]].attrib['parentSummary'],
                'videotype' : DirectoryRoot[SerieID[0]].attrib['type'],
                'ratingKey' : DirectoryRoot[SerieID[0]].attrib['ratingKey'],
                'title' : DirectoryRoot[SerieID[0]].attrib['title'].replace('Season', 'Saison')
            }
        # Si on en a reçu plusieurs
        else :
            # Si on a réellement plusieurs saisons qui ont été ajoutées en même temps
            if int(DirectoryRoot[SerieID[0]].attrib['addedAt']) > int(DirectoryRoot[SerieID[1]].attrib['addedAt']) and int(DirectoryRoot[SerieID[0]].attrib['addedAt']) < int(DirectoryRoot[SerieID[1]].attrib['updatedAt']) :
                export = None
            # Sinon c'est que c'était pas en même temps
            else :
                export = {
                    'year' :  DirectoryRoot[SerieID[0]].attrib['parentYear'],
                    'summary' : DirectoryRoot[SerieID[0]].attrib['parentSummary'],
                    'videotype' : DirectoryRoot[SerieID[0]].attrib['type'],
                    'ratingKey' : DirectoryRoot[SerieID[0]].attrib['ratingKey'],
                    'title' : DirectoryRoot[SerieID[0]].attrib['title'].replace('Season', 'Saison')
                }

    # Pareil mais si c'est un film
    elif datatype == "movie" :
        # On vient interroger tous les films récemment ajoutées, et cherchons celui qui est intéressant
        FilmRoot = root.findall('Video')
        SerieID = []
        index = 0
        # On vient garder en mémoire ceux dont le nom du film reçu dans le webhook correspond avec le contenu récemment ajouté
        for film in FilmRoot :
            if film.get('title') == Titre :
                number += 1
                SerieID.append(index)
            index += 1

        # Si on a reçu qu'un seul nom de film dans le lot
        if number == 1 :
            export = {
                'year' :  FilmRoot[SerieID[0]].attrib['year'],
                'summary' : FilmRoot[SerieID[0]].attrib['summary'],
                'videotype' : FilmRoot[SerieID[0]].attrib['type'],
                'ratingKey' : FilmRoot[SerieID[0]].attrib['ratingKey']
            }
        else :
            # Si on en a reçu plusieurs
            export = None
    
    return export
            

def DownloadImage(thumb):
    # On vient taper sur le lien du poster de notre film / série / saison, et la téléchargeons
    url = f"{baseurl}{thumb}/posters?X-Plex-Token={token}"
    img_data = requests.get(url).content
    with open('image.jpg', 'wb') as handler :
        handler.write(img_data)
        handler.close()
    return

# Bon bah là flemme d'expliquer mais on fait juste la mise en forme pour envoyer le webhook
def Movie_Show_Webhook(Titre, year, summary, videotype, Librairie, serveruuid, ratingkey, saison) :

    global WEBHOOK_URL

    # Et ça c'est en fonction de la version installée de discord.py
    if '2.0' in discord.__version__ :
        webhook = discord.SyncWebhook.from_url(WEBHOOK_URL)
    else :
        webhook = discord.Webhook.from_url(url=WEBHOOK_URL, adapter = discord.RequestsWebhookAdapter())

    if videotype == "season" :
        AddedEmbed = discord.Embed(
            title= f'{Titre} - {saison} ({year})',
            description= f'{summary}',
            colour=discord.Color.from_rgb(229, 160, 13)
        )
    else :
        AddedEmbed = discord.Embed(
            title= f'{Titre} ({year})',
            description= f'{summary}',
            colour=discord.Color.from_rgb(229, 160, 13)
        )

    AddedEmbed.add_field(
        name= 'Type :',
        value= f'{videotype.capitalize()}',
        inline=True
    )
    AddedEmbed.add_field(
        name= 'Librairie :',
        value= f'{Librairie}',
        inline=True
    )
    AddedEmbed.add_field(
            name= 'Regarder sur Plex ?',
            value= f'[Cliques ici](https://app.plex.tv/desktop/#!/server/{serveruuid}/details?key=%2Flibrary%2Fmetadata%2F{ratingkey})',
            inline=True
        )


    AddedEmbed.set_image(url="attachment://image.jpg")

    webhook.send(
        embed = AddedEmbed,
        username = 'Plex',
        avatar_url = "https://img.utdstc.com/icon/3e6/f69/3e6f6913435fcdd3a378463b5214ecfe87736052132890b8f9447a5ec7640d09",
        file = discord.File('./image.jpg')
    )
    return

# Bah là, pareil mais pour les épisodes seuls
def Episode_Webhook(ShowName, SaisonEpisode, NumeroEpisode, summary, Librairie, ratingkeySaison, serveruuid, ratingkey) :

    global WEBHOOK_URL

    if '2.0' in discord.__version__ :
        webhook = discord.SyncWebhook.from_url(WEBHOOK_URL)
    else :
        webhook = discord.Webhook.from_url(url=WEBHOOK_URL, adapter = discord.RequestsWebhookAdapter())

    AddedEmbed = discord.Embed(
        title= f'{ShowName} - {SaisonEpisode} Episode {NumeroEpisode}',
        description= f'{summary}',
        colour=discord.Color.from_rgb(229, 160, 13)
    )

    AddedEmbed.add_field(
        name= 'Type :',
        value= 'Episode',
        inline=True
    )
    AddedEmbed.add_field(
        name= 'Librairie :',
        value= f'{Librairie}',
        inline=True
    )
    AddedEmbed.add_field(
        name= 'Regarder cet épisode sur Plex ?',
        value= f'[Cliques ici](https://app.plex.tv/desktop/#!/server/{serveruuid}/details?key=%2Flibrary%2Fmetadata%2F{ratingkey})',
        inline=True
    )
    AddedEmbed.add_field(
        name= 'Regarder cette série sur Plex ?',
        value= f'[Cliques ici](https://app.plex.tv/desktop/#!/server/{serveruuid}/details?key=%2Flibrary%2Fmetadata%2F{ratingkeySaison})',
        inline=True
    )


    AddedEmbed.set_image(url="attachment://image.jpg")

    webhook.send(
        embed = AddedEmbed,
        username = 'Plex',
        avatar_url = "https://img.utdstc.com/icon/3e6/f69/3e6f6913435fcdd3a378463b5214ecfe87736052132890b8f9447a5ec7640d09",
        file = discord.File('./image.jpg')
    )
    return

if __name__ == "__main__":
    app.run(host='0.0.0.0')
