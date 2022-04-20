#!/usr/bin/python3

import os
from dotenv import load_dotenv
import flockutil as fu
import discord
import json
import logging


class FlockClient(discord.Client):
    """Client for Discord API event handling."""

    def __init__(self):
        self._guilds = []
        self._uid = ""
        self._trigger_phrase = "!q"
        self._queue_manager = fu.QueueManager()
        
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
        print("Ready to go!")

    def set_trigger_char(self, trigger_phrase):
        """Set the phrase that will trigger the bot from a discord message."""
        if len(trigger_phrase) <= 3 and isinstance(trigger_phrase, str):
            self._trigger_phrase = trigger_phrase

    async def on_message(self, message):
        """Parses Discord message checking for Bot trigger phrase."""

        # Break if message sender is Flock
        author = message.author
        if author == client.user:
            return

        # Check message content for trigger phrase and parse command and arguments if present
        if self._trigger_phrase in message.content:
            command = ""
            args = []

            command_msg_split = message.content[message.content.index(
                self._trigger_phrase):].split(' ')

            # Extract command and arguments (if any)
            if len(command_msg_split[1:]) > 1:
                command, args = command_msg_split[1], command_msg_split[2:]
            else:
                command = command_msg_split[1]
            
            print("Received comand '{}' with args {}.".format(command, args))
        else:
            return 

        # Run code based on the command
        if command in self._commands.keys():
            if command in ["create", "c"]:

                # Get the user-specified queue name, if provided
                name = ""
                if len(args) > 0:
                    name = args[0]
                
                # Create the queue
                q = self._queue_manager.create_queue(author=author, name=name)
                await message.channel.send(self._commands['create']['response'].format(q.get_name()))

            if command in ["join", "j", "add", "a"]:
                q = self._queue_manager.find_queue_by_name(args[0])
                q.add_member(author.id)

                # Reply to user indicating that they have been added.
                await message.channel.send(self._commands['add']['response'].format(author.mention, q.get_name()))

        else:
            # Send message indicating that the command was not recognised with a list of available commands
            await message.channel.send("`{}` not recognised. Available commands are:\n- {}".format(
                command, '\n- '.join(self._commands.keys())))


if __name__ == "__main__":
    # Enable Discord API logging
    logging.basicConfig(level=logging.INFO)

    # Load environment variables and load API token
    load_dotenv()
    TOKEN = os.environ.get("api-token")

    # Start the client
    client = FlockClient()
    client.run(TOKEN)
