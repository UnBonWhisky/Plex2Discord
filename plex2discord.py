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
    if data['event'] == 'library.new' :
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
        else :
            DownloadImage(data['Metadata']['thumb'])
            Movie_Show_Webhook(
                data['Metadata']['title'], #Titre
                data['Metadata']['year'], #year
                data['Metadata']['summary'], #summary
                data['Metadata']['type'], #videotype
                data['Metadata']['librarySectionTitle'], #Librairie
                data['Server']['uuid'], #serveruuid
                data['Metadata']['ratingKey'] #ratingkey
            )
    return "OK"

def DownloadImage(thumb):
    url = f"{baseurl}{thumb}/posters?X-Plex-Token={token}"
    img_data = requests.get(url).content
    with open('image.jpg', 'wb') as handler :
        handler.write(img_data)
        handler.close()
    return

def Movie_Show_Webhook(Titre, year, summary, videotype, Librairie, serveruuid, ratingkey) :

    global WEBHOOK_URL

    if '2.0' in discord.__version__ :
        webhook = discord.SyncWebhook.from_url(WEBHOOK_URL)
    else :
        webhook = discord.Webhook.from_url(url=WEBHOOK_URL, adapter = discord.RequestsWebhookAdapter())

    AddedEmbed = discord.Embed(
        title= f'{Titre} ({year})',
        description= f'{summary}',
        colour=discord.Color.from_rgb(229, 160, 13)
    )

    AddedEmbed.add_field(
        name= 'Type :',
        #value= f'{videotype.capitalize()}',
        value= 'Film' if videotype == 'movie' else 'Série',
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
