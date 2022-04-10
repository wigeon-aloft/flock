#!/usr/bin/python3

import os
from dotenv import load_dotenv
import flockutil
import discord
import json


class FlockClient(discord.Client):
    """Client for Discord API event handling."""

    def __init__(self):
        self._guilds = []
        self._uid = ""
        self._trigger_phrase = "!q"
        self._queue_manager = flockutil.QueueManager()
        
        # Load commands from file
        with open("./data/command.json", 'r') as command_file:
            self._commands = json.load(command_file)

        # Call Client super init
        discord.Client.__init__(self)

    async def on_ready(self):
        """Does some initialisation once the Bot is connected to Discord."""

        # Set client user ID
        self._uid = client.user
        print(f'{client.user} has connected to Discord')

        # Get bot's guild list
        print('Guild list:')
        for guild in client.guilds:
            self._guilds.append(guild.id)
            print(f'\t{guild.name} {guild.id}')

    def set_trigger_char(self, trigger_phrase):
        """Set the phrase that will trigger the bot from a discord message."""
        if len(trigger_phrase) <= 3 and isinstance(trigger_phrase, str):
            self._trigger_phrase = trigger_phrase



    async def on_message(self, message):
        """Parses Discord message checking for Bot trigger phrase."""

        print(f"parsing message {message.id}")

        # Break if message sender is Flock
        if message.author == client.user:
            return

        # Check message content for trigger phrase
        if self._trigger_phrase in message.content:
            print("trigger phrase found")
            command = message.content[message.content.index(self._trigger_phrase):].split(' ')[1]
        else:
            return 

        print("guess we're sending a message")

        # Check if the command exists
        if command in self._commands.keys():
            await message.channel.send(self._commands[command]['response'])
        else:
            await message.channel.send("`{}` not recognised. Available commands are:\n- {}".format(command, '\n- '.join(self._commands.keys())))



if __name__ == "__main__":

    # Load environment variables and load API token
    load_dotenv()
    TOKEN = os.environ.get("api-token")

    # Start the client
    client = FlockClient()
    client.run(TOKEN)
