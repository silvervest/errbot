# https://discord.com/api/oauth2/authorize?client_id=1031394414569996421&permissions=2147871744&scope=bot
import csv
import re
import discord
from dotenv import load_dotenv
import os
import logging


def normalise_code(code):
    # uppercase!
    code = code.upper()

    # convert spaces to dashes
    code = code.replace(' ', '-')

    return code


def fetch_code_response(system, code):
    code = normalise_code(code)
    if system not in codes:
        raise Exception(f"Invalid system called - {system}")

    response = (
        f"Detected {system} error code {code}, but unfortunately it's not fully known:\n"
        f"If you have any info on it, please get in touch with admins!"
    )
    if code in codes[system]['codes'] and codes[system]['codes'][code]['name'] != '':
        error = codes[system]['codes'][code]
        notes = error['notes'].replace("\\n", "\n")
        if notes == '':
            notes = 'Not much known on this error - if you have any info on it, please get in touch with admins!'
        response = (
            f"Detected {system} error code {code}, here's some info:\n"
            f"Name: {error['name'] or 'Unnamed Error'}\n"
            f"Remarks: {notes}"
        )

    return response


def load_codes():
    # load up the error codes to respond to
    # yeah it's messy, whatever it works
    codes = {
        'PS4': {
            'pattern': '((?:CE|NP|NW|SU|WB|WC|WS|WV)[\- ][0-9]{5}[\- ][0-9])',
            'codes': {},
            'channel': 'ps4',
        },
        'PS5': {
            'pattern': '((?:CE|NP|NW|SU|WB|WS|WV)[\- ][0-9]{6}[\- ][0-9])',
            'codes': {},
            'channel': 'ps5',
        }
    }
    for system in codes:
        with open(f"{system}.csv", newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            names = reader.fieldnames
            for row in reader:
                code = row['code']
                del row['code']
                codes[system]['codes'][code] = row

    return codes


def boot_discord(codes):
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
            if codes[system]['channel'] != message.channel.name:
                continue

            sd = codes[system]
            matches = re.findall(sd['pattern'], message.content, re.IGNORECASE)
            for code in matches:
                logging.info(f"#{message.channel.name} <{message.author.name}> {message.content}")
                try:
                    response = fetch_code_response(system, code)
                    logging.info(response)
                    await message.channel.send(response)
                except Exception as err:
                    logging.warning(err)

    # start up the discord client
    client.run(os.getenv('DISCORD_TOKEN'))


if __name__ == "__main__":
    load_dotenv()

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    codes = load_codes()
    boot_discord(codes)

