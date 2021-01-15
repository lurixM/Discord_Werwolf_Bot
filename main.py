import os
import copy
import random
import discord
from discord.ext import commands
from dotenv import load_dotenv

import Game

# In order for this bot to run, there has to be a '.env' file in the directory, where the bot script is located
# At the moment the .env file needs to contain 2 variables:
# TOKEN: Token of the discord bot, there's a good tutorial for this on realpython:
#   https://realpython.com/how-to-make-a-discord-bot-python/
# GUILD: Name of Discord Server, see realpython tutorial
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD_NAME ')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='-wer ', intents=intents)

game_list = {}
roles = [
        'werwolf.hexe',
        'werwolf.jaeger',
        'werwolf.amor',
        'werwolf.seherin',
        'werwolf.nutte',
        'werwolf.werwolf',
        'werwolf.dorfdepp',
        'werwolf.psychowolf'
         ]


@bot.command(name='start')
@commands.has_role('werwolf.moderator')
async def start(ctx):
    guild_category = ctx.channel.category

    # Not that clean, but it's for use in a close env right now. Also if somebody can teach me lambdas ... ¯\_(ツ)_/¯
    voice_channel_users = guild_category.voice_channels[0].members

    # Append to list of running games. Guild Category is the id, voice_channel_users all users that are part of the game
    game_list[guild_category] = Game.Game(guild_category, voice_channel_users)

    # TODO: List that contains correct number of wolfes
    # Lists to iterate over. Since they are going to be modified, they are deepcopied
    roles_to_iterate = copy.copy(roles)
    users_to_iterate = copy.copy(voice_channel_users)

    user_role_dict = {}

    # TODO: Check formula
    # It's ugly! But time pressure and stuff. Didn't think about to implement this last night. I'll eventually rewrite
    # this to not use dicts, that was a bad idea.
    additional_wolf_count = int((len(users_to_iterate) - 7) / 4)
    for i in range(0, additional_wolf_count):
        roles_to_iterate.append('werwolf.werwolf')

    while len(roles_to_iterate) < len(users_to_iterate):
        roles_to_iterate.append('werwolf.dorfbewohner')

    # Assign 'Dorfbewohner' to every player in game.
    # dorfbewohner_role = discord.utils.get(ctx.guild.roles, name="werwolf.dorfbewohner")

    # Assign every other role
    if len(roles_to_iterate) - 1 <= len(users_to_iterate) - 1:
        for user in voice_channel_users:
            user_roles = user.roles
            user_roles_name = []

            # List of all roles a use has
            for role in user_roles:
                user_roles_name.append(role.name)
            # TODO: cleanup
            '''if not ('werwolf.moderator' in user_roles_name):
                #try:
                 #   await user.add_roles(dorfbewohner_role)
                except discord.Forbidden:
                    await ctx.send('Insufficient Permission, contact an admin for help')
                    return '''

        # roles_to_iterate.remove("werwolf.dorfbewohner")

        for rand_user in users_to_iterate:
            rand_role = random.choice(roles_to_iterate)
            game_role_abc = discord.utils.get(ctx.guild.roles, name=rand_role)

            # TODO: Check if role is already added or exists
            rand_user_roles = rand_user.roles
            rand_user_roles_name = []

            # List of all roles a use has
            for role in rand_user_roles:
                rand_user_roles_name.append(role.name)

            if not ('werwolf.moderator' in rand_user_roles_name):
                await rand_user.add_roles(game_role_abc)
                user_role_dict[rand_user.name] = rand_role
                roles_to_iterate.remove(rand_role)

    else:
        await ctx.send('Nicht genug Spieler, um zu starten')
        game_list.pop(guild_category)
        return

    # Implies that a mod is in channel. Also Moderator is declared the last person found. For controllability
    # only one mod can be in a channel for now
    # TODO: Implement game config.
    for user in voice_channel_users:
        user_roles = user.roles
        for role in user_roles:
            if role.name == "werwolf.moderator":
                # Bad style. Also generally dumb
                moderator = user
                print(moderator)

    # Also bad style.
    if moderator:
        await moderator.create_dm()
        message = f"Neues Spiel: \n"
        for user_role_pair in user_role_dict:
            message += user_role_pair + ": " + user_role_dict[user_role_pair] + ", \n"
        await moderator.dm_channel.send(message)

    await ctx.send(f'Spiel gestartet!')  # \n ' 'Es spielen: \n' ', '.join(game_list[guild_category].get_user_list()))


@bot.command(name='restart')
@commands.has_role('werwolf.moderator')
async def restart(ctx):
    await stop(ctx)
    await start(ctx)


@bot.command(name='stop')
@commands.has_role('werwolf.moderator')
async def stop(ctx):
    guild_category = ctx.channel.category

    # TODO: bad style
    if guild_category in game_list:
        game = game_list[guild_category]
        user_list = game.get_user_list()

        for user in user_list:
            user_roles = user.roles
            for role in user_roles:
                # TODO: moderator gets removed
                if ('werwolf.' in role.name) and (role.name != 'werwolf.moderator'):
                    await user.remove_roles(role)
    else:
        await ctx.send('Spiel wurde bereits beendet, oder existiert nicht!')
        return

    game_list.pop(guild_category)

    await ctx.send('Spiel gestoppt!')


@bot.event
async def on_ready():

    print(
        f'{bot.user} has connected to Discord!'
    )


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send('Command does not exist: \n'
                       'Type -wer help to get a list of all commands')

    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('Insufficient Permission: Only werwolf.moderator can use this command.')

bot.run(TOKEN)

# TODO: Whispering by chance? To emulate missing real life element.
# TODO: VoteCount
