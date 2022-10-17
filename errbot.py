# https://discord.com/api/oauth2/authorize?client_id=1031394414569996421&permissions=2147871744&scope=bot
import csv
import re
import discord
from dotenv import load_dotenv
import os

load_dotenv()

def normalise_code(code):
    # uppercase!
    code = code.upper()

    # convert spaces to dashes
    code = code.replace(' ', '-')

    return code


# load up the error codes to respond to
# yeah it's messy, whatever it works
files = ['PS4']
codes = {
    'PS4': {
        'pattern': '([a-zA-Z]{2}[\- ][0-9]{5}[\- ][0-9])',
        'codes': [],
        'names': [],
        'notes': [],
    }
}
for file in files:
    with open(f"{file}.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            codes[file]['codes'].append(row[0])
            name = f"{row[1]} ({row[2]})" if row[1] and row[2] else row[1]
            codes[file]['names'].append(name)
            codes[file]['notes'].append(row[3])


# setup the discord client
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # every single message the bot sees will run through the list of code to try to match a regex
    # if we match on one, dig out the actual code and respond with a message
    for system in codes:
        sd = codes[system]
        match = re.search(sd['pattern'], message.content)
        if match is not None:
            ec = match.group(0)
            code = normalise_code(ec)
            if code not in sd['codes']:
                return

            print(f"#{message.channel.name} <{message.author.name}> {system}:{code} - {message.content}")

            i = sd['codes'].index(code)
            response = f"Detected {system} error code {code}, here's some info:\nName: {sd['names'][i] or 'Unnamed Error'}\nRemarks: {sd['notes'][i]}"
            await message.channel.send(response)


# start up the discord client
client.run(os.getenv('DISCORD_TOKEN'))
