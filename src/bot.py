#!/usr/bin/python3

import os
from dotenv import load_dotenv
import flockutil as fu
import discord
import logging


def mention(user_id):
    """Generate a mention string for a given user ID."""
    return '<@{}>'.format(user_id)


class FlockClient(discord.Client):
    """Client for Discord API event handling."""

    def __init__(self):
        self._guilds = []
        self._uid = ""
        self._trigger_phrase = "!q"
        self._queue_manager = fu.QueueManager()
        self._commands = {
            "help": {
                "name": "help",
                "method": self.help,
                "trigger": [
                    "help",
                    "h"
                ],
                "response": "Available commands:\n{}",
                "description": {
                    "short": "Command usage information",
                    "long": "Provide information for a particular command. Pass the name of a command as the first positional argument. If none is provided a list of available commands will be displayed."
                },
                "usage": "{} {} <command_name>"
            },
            "add": {
                "name": "add",
                "method": self.add,
                "trigger": [
                    "join",
                    "j",
                    "add",
                    "a"
                ],
                "response": "Added {} to {} queue.",
                "description": {
                    "short": "Add a user to a queue",
                    "long": "Add a user to an existing queue. If no queue name specified then user will be added to most recent/only queue if one exists. If no user is specified then the message sender will be added."
                },
                "usage": "{} {} <queue_name> <user>"
            },
            "create": {
                "name": "create",
                "method": self.create,
                "trigger": [
                    "create",
                    "c"
                ],
                "response": "Created queue {}.",
                "description": {
                    "short": "Create a new queue",
                    "long": "Create a new queue. Pass a name for the queue as the first positional argument, otherwise one will be randomly generated."
                },
                "usage": "{} {} <queue_name>"
            },
            "show": {
                "name": "show",
                "method": self.show,
                "trigger": [
                    "show",
                    "s"
                ],
                "response": "{} you are in {}.",
                "description": {
                    "short": "Show queues that a user is in",
                    "long": "Show queues that a specified user is in. Pass a username/ID as the first positional argument."
                },
                "usage": "{} {} *<user>"
            },
            "leave": {
                "name": "leave",
                "method": self.leave,
                "trigger": [
                    "leave",
                    "l",
                    "remove",
                    "r"
                ],
                "response": "{} removed from {}",
                "description": {
                    "short": "Remove a user from a queue",
                    "long": "Remove a user from a queue. If no user is specified then the message sender will be removed."
                },
                "usage": "{} {} *<queue_name> <user>"
            },
            "status": {
                "name": "status",
                "method": self.status,
                "trigger": [
                    "status",
                    "t",
                    "list",
                    "ls"
                ],
                "response": "Current members of the {} queue:\n{}",
                "description": {
                    "short": "Show queue information",
                    "long": "Show information for a specified queue. Provide queue name as the first positional argument. If no queue name is provided then it will show a list of existing queues."
                },
                "usage": "{} {} <queue_name>"
            },
            "delete": {
                "name": "delete",
                "method": self.delete,
                "trigger": [
                    "delete",
                    "del",
                    "d"
                ],
                "response": "Deleted {} queue.",
                "description": {
                    "short": "Delete an existing queue",
                    "long": "Delete an existing queue. Provide a queue name as the first positional argument."
                },
                "usage": "{} {} *<queue_name>"
            }
        }

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

    def get_command_from_trigger(self, user_command):
        """Returns a command reference from self._commands for a given user input trigger."""

        # Check if the trigger is associated with a command
        for command in self._commands:
            if user_command in self._commands.get(command).get("trigger"):
                return self._commands.get(command)
            
        # Raise an exception if the trigger could not be found
        raise KeyError(f"Command '{user_command}' does not exist.")

    async def on_message(self, message):
        """Parses Discord message checking for Bot trigger phrase."""

        # Break if message sender is Flock
        author = message.author
        if author == client.user:
            return

        # Check message content for trigger phrase and parse command and arguments if present
        if self._trigger_phrase in message.content:
            user_command = ""
            args = []

            command_msg_split = message.content[message.content.index(
                self._trigger_phrase):].split(' ')

            # Extract command and arguments (if any)
            if len(command_msg_split[1:]) > 1:
                user_command, args = command_msg_split[1], command_msg_split[2:]
            else:
                user_command = command_msg_split[1]
             
            print("Received command '{}' with args {}.".format(user_command, args))
        else:
            return 

        # Run the command associated with user_command
        try:
            await self.get_command_from_trigger(user_command).get("method")(message, args)
        except KeyError as ke:
            print(ke)
            await message.channel.send("`{}` not recognised as a command. Use `help` for a list of available commands.".format(
                user_command, '\n- '.join(self._commands.keys())))
            
    async def help(self, message, args):
        """Prints help information for the given command or shows a list of commands if command not provided."""
        
        # Generate a string containing information for each available command 
        command_help_string = '\n'.join(
            [f"**{command.get('name')}** - {command.get('description').get('short')}" for command in dict(sorted(self._commands.items())).values()])

        # If no command query was provided, show a list of available commands
        if len(args) == 0:
            await message.channel.send(self._commands.get("help").get("response").format(command_help_string))
            return

        try:
            command = self.get_command_from_trigger(args[0])

            # Command exists - show help message for the command
            trigger_usage_string = f"{{ {' | '.join(command.get('trigger'))} }}"
            help_message = f"**{', '.join(command.get('trigger'))}**\n```{command.get('usage').format(self._trigger_phrase, trigger_usage_string)}```\n> {command.get('description').get('long')}"

            # Add information on required arguments if there are any in the command usage information string
            if '*' in command.get('usage'):
                help_message += "\n*Note: parameters preceded by a '\*' are required.*"

            await message.channel.send(help_message)

        except KeyError:
            # Command doesn't exist - show a general list of commands and associated triggers
            await message.channel.send(f"`{args[0]}` not recognised. {self._commands.get('help').get('response').format(command_help_string)}")
    
    async def create(self, message, args):
        # Get the user-specified queue name, if provided
        name = ""
        if len(args) > 0:
            name = args[0]

        # Create the queue
        try:
            q = self._queue_manager.create_queue(author=message.author, name=name)
            await message.channel.send(self._commands['create']['response'].format(q.get_name()))
        except ValueError as value_error:
            print(value_error)
            await message.channel.send(value_error)

    async def add(self, message, args):
            # Add a user to the specified queue
            q = self._queue_manager.find_queue_by_name(args[0])

            try:
                # Add user to the queue
                q.add_member(message.author.id)

                # Reply to user indicating that they have been added.
                await message.channel.send(self._commands['add']['response'].format(message.author.mention, q.get_name()))

            except ValueError as ve:
                # Send error message
                await message.channel.send(str(ve).format(message.author.mention))

    async def show(self, message, args):
        # Show the queues a user is currently in
        user_queues = self._queue_manager.get_user_queues(message.author)

        if len(user_queues) == 0:
            await message.channel.send(f"{message.author.mention} you are not currently in any queues.")
        else:
            await message.channel.send(self._commands['show']['response'].format(message.author.mention, ', '.join([queue.get_name() for queue in user_queues])))

    async def leave(self, message, args):
        # Removes a user from a specified queue
        q_name = args[0]
        q = self._queue_manager.find_queue_by_name(q_name)
        q.remove_member(message.author.id)
        await message.channel.send(self._commands['leave']['response'].format(message.author.mention, q_name))

    async def status(self, message, args):
        q_name = args[0]
        q = self._queue_manager.find_queue_by_name(q_name)
        members = q.get_members()
        await message.channel.send(self._commands['status']['response'].format(q_name, '\n'.join([mention(member) for member in members])))

    async def delete(self, message, args):
        q_name = args[0]
        q = self._queue_manager.delete_queue(q_name)

        # TODO check if returned queue was None or not. Send response message based on that
        await message.channel.send(self._commands['delete']['response'].format(q_name))


if __name__ == "__main__":
    # Enable Discord API logging
    logging.basicConfig(level=logging.INFO)

    # Load environment variables and load API token
    load_dotenv()
    TOKEN = os.environ.get("api-token")

    # Start the client
    client = FlockClient()
    client.run(TOKEN)
