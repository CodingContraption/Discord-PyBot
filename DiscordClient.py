import discord
import asyncio
import logging

# Logging and stuff.
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Create a discord client instance.
client = discord.Client()
# Load in opus for voice.
discord.opus.load_opus
command_prefix = '!'
player = None
volume = 0.5


# Check if the var is a number.
def is_num(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def player_finished():
    # Fucking asyncio won't let me change my game name.
    # loop = asyncio.get_event_loop()
    # loop.create_task(client.change_presence(game=discord.Game(name='Type !help for commands')))
    print('The end')
    global player
    player = None


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    # Check if opus is loaded.
    print('Opus loaded: {}'.format(discord.opus.is_loaded()))
    print('------')
    # Set game to useful info title.
    await client.change_presence(game=discord.Game(name='Type !help for commands'))


@client.event
async def on_message(message):
    if message.content.startswith(command_prefix):
        global player, volume
        args = message.content.split()
        command = args.pop(0).lstrip(command_prefix)
        # Show help message for all commands.
        if command == 'help':
            msg = [
                'Available commands:\n',
                '**- !help** Displays this help message.\n',
                '**- !count** Displays your message count in this channel.\n',
                '**- !sleep** Sleep for 5 seconds.\n',
            ]
            await client.send_message(message.channel, "".join(msg))
        # Count messages by user.
        elif command == 'count':
            counter = 0
            tmp = await client.send_message(message.channel, 'Calculating messages...')

            async for log in client.logs_from(message.channel, limit=100):
                if log.author == message.author:
                    counter += 1
            await client.edit_message(tmp, 'You have {} messages.'.format(counter))
        # Make the bot sleep for 5 seconds.
        elif command == 'sleep':
            await asyncio.sleep(5)
            await client.send_message(message.channel, 'Done sleeping.')
        # Join a voice channel.
        elif command == 'join':
            # Check if client is already connected to a channel.
            if client.voice_client_in(message.server) is not None:
                cur_client = client.voice_client_in(message.server)
                # Check if the current channel is equal to the author's channel.
                if cur_client.channel.name == message.author.voice.voice_channel.name:
                    await client.send_message(message.channel, 'Already in a voice channel.')
                    return
                # Else move to his/her channel.
                else:
                    await cur_client.move_to(message.author.voice.voice_channel)
                    await client.send_message(message.channel, 'Moved to \'{}\''.format(cur_client.channel.name))
            voice_channel = message.author.voice.voice_channel
            # If the user is in a voice channel join his channel.
            if voice_channel is not None:
                voice_client = await client.join_voice_channel(voice_channel)
                await client.send_message(message.channel, 'Joined voice channel \'{}\'.'
                                          .format(voice_client.channel.name))
            # Else give error message.
            else:
                await client.send_message(message.channel, 'Failed to join voice channel. ' +
                                          'You have to be in a voice channel to let me join!')
        # Leave a voice channel.
        elif command == 'leave':
            voice = client.voice_client_in(message.server)
            # If client is connected, disconnect.
            if voice is not None:
                await voice.disconnect()
                await client.send_message(message.channel, 'Left the voice channel.')
            # Else notify user client is not connected.
            else:
                await client.send_message(message.channel, 'Not in a voice channel.')
        # Play a youtube video.
        elif command == 'yt':
            voice = client.voice_client_in(message.server)
            # If client is connected, disconnect.
            if len(args) < 1:
                await client.send_message(message.channel, 'Invalid command. Usage: `!yt <url>`')
            if voice is not None:
                await client.delete_message(message)
                # player_args = {'after': player_finished()}
                player = await voice.create_ytdl_player(args[0], after=player_finished)
                player.start()
                player.volume = volume if volume is not None else 1
                # player.start()
                await client.send_message(message.channel, 'Playing song: `{}`.'.format(player.title))
                await client.change_presence(game=discord.Game(name=player.title))
            # Else notify user client is not connected.
            else:
                await client.send_message(message.channel, 'Not in a voice channel.')
        elif command == 'volume':
            if len(args) > 0:
                volume = float(args[0])
                if player is not None:
                    player.volume = volume
                await client.send_message(message.channel, 'Volume set to {}.'.format(volume))
            else:
                await client.send_message(message.channel, 'No volume provided. Use the format `!volume <0-2>`')
        elif command == 'stop':
            if player is not None:
                player.stop()
                await client.change_presence(game=discord.Game(name='Type !help for commands'))

f = open('token.txt', 'r')
client.run(f.read())
