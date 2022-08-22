import pprint
from flask import Flask, request, json
import requests
import discord
import xml.etree.ElementTree as ET

app = Flask(__name__)
pp = pprint.PrettyPrinter(indent=2)

baseurl = 'http://IP ICI:32400'
token = ''
WEBHOOK_URL = ""

minutes = 2

@app.route('/Plex', methods=['GET','POST'])
def p2d():
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
                    for x in range(len(export)):
                        Movie_Show_Webhook(
                            data['Metadata']['title'], #Titre
                            export[x]['year'], #year
                            export[x]['summary'], #summary
                            export[x]['videotype'], #videotype
                            data['Metadata']['librarySectionTitle'], #Librairie
                            data['Server']['uuid'], #serveruuid
                            export[x]['ratingKey'], #ratingkey
                            export[x]['title'] #saison
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
                        None #saison
                    )
            # Si c'est un film
            else :
                # Si l'export n'est pas vide
                if export is not None:
                    Movie_Show_Webhook(
                        data['Metadata']['title'], #Titre
                        export[0]['year'], #year
                        export[0]['summary'], #summary
                        export[0]['videotype'], #videotype
                        data['Metadata']['librarySectionTitle'], #Librairie
                        data['Server']['uuid'], #serveruuid
                        export[0]['ratingKey'], #ratingkey
                        None #saison
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
                        None #saison
                    )

    return "OK"

def Get_XML_Infos(Titre, datatype):

    global minutes

    # On vient interroger le serveur pour avoir des infos sur ce qui a été nouvellement ajouté, puis on enregistre les infos de ce qui nous a été rendu
    url = f'{baseurl}/library/recentlyAdded?X-Plex-Token={token}'
    resp = requests.get(url)
    open('recentlyAdded.xml', 'wb').write(resp.content)

    # On vient lire le fichier et le mettons de façon utilisable et lisible par Python
    tree = ET.parse('recentlyAdded.xml')
    root = tree.getroot()

    number = 0

    # Cette fonction sert a déterminer si les saisons ont été ajoutées à la suite ou non
    def isSerie(suite):
        lastOccurence = ""
        for x in range(len(suite)):
            if x != 0 :
                if suite[x] == suite[x-1]+1:
                    continue
                else :
                    lastOccurence = x
                    break
        if lastOccurence == "":
            lastOccurence = len(suite)
        return lastOccurence

    # Si Plex nous a envoyé l'info que c'est une série
    if datatype == "show":

        # On vient interroger toutes les séries récemment ajoutées, et cherchons celles qui sont intéressantes
        DirectoryRoot = root.findall('Directory')
        SerieID = []
        index = 0

        # On vient garder en mémoire ceux dont le nom de la série reçue dans le webhook correspond avec le contenu récemment ajouté
        for directory in DirectoryRoot :
            if directory.get('parentTitle') == Titre :
                number += 1
                SerieID.append(index)
            index += 1

        # Si on a reçu qu'une seule fois ou + la série dans le lot
        if number >= 1 :
            export = []

            # Si on a pas reçu qu'une seule fois la série dans le lot, on lance la fonction isSerie
            if number != 1 :
                serie = isSerie(SerieID)
            else:
                serie = 1

            # On vient checker combien on a de saison dans notre série
            url = f'{baseurl}/library/metadata/{DirectoryRoot[SerieID[0]].attrib["parentRatingKey"]}/children?X-Plex-Token={token}'
            resp = requests.get(url)
            open('childrens.xml', 'wb').write(resp.content)

            childrentree = ET.parse('childrens.xml')
            childrenroot = childrentree.getroot().findall('Directory')

            # Afin d'être sûr que c'est une nouvelle série et pas une nouvelle saison, on vient checker le temps entre les sorties de chaque saison
            # Si le temps est supérieur à 5 minutes, alors c'est une nouvelle saison uniquement et pas une nouvelle série
            if serie != 1 :
                SaisonsALaSuite = 1
                for x in range(serie):
                    if x != 0:
                        if int((int(DirectoryRoot[SerieID[x-1]].attrib['addedAt']) - int(DirectoryRoot[SerieID[x]].attrib['addedAt'])) / 60) <= minutes :
                            SaisonsALaSuite += 1
                            continue
                        else :
                            break
                serie = SaisonsALaSuite

            # Si on a autant d'ajouts à la suite qu'il y a de saisons dans notre série, alors on a une nouvelle série
            if (len(childrenroot)-1) == serie:
                export = None
            else :
            
                for x in range(serie):
                    export.append({
                        'year' :  DirectoryRoot[SerieID[x]].attrib['parentYear'],
                        'summary' : DirectoryRoot[SerieID[x]].attrib['parentSummary'],
                        'videotype' : DirectoryRoot[SerieID[x]].attrib['type'],
                        'ratingKey' : DirectoryRoot[SerieID[x]].attrib['ratingKey'],
                        'title' : DirectoryRoot[SerieID[x]].attrib['title'].replace('Season', 'Saison')
                    })
        
        else:
            export = None

    elif datatype == "movie" :
        FilmRoot = root.findall('Video')
        SerieID = []
        index = 0
        for film in FilmRoot :
            if film.get('title') == Titre :
                number += 1

        if number == 1 :
            export = [{
                'year' :  FilmRoot[SerieID[0]].attrib['parentYear'],
                'summary' : FilmRoot[SerieID[0]].attrib['parentSummary'],
                'videotype' : FilmRoot[SerieID[0]].attrib['type'],
                'ratingKey' : FilmRoot[SerieID[0]].attrib['ratingKey'],
                'title' : FilmRoot[SerieID[0]].attrib['ratingKey'].replace('Season', 'Saison')
            }]
        else :
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
