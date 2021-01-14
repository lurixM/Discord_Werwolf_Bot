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
roles = {
        'Dorfbewohner': 'werwolf.dorfbewohner',
        'Hexe': 'werwolf.hexe',
        'Jaeger': 'werwolf.jaeger',
        'Amor': 'werwolf.amor',
        'Seherin': 'werwolf.seherin',
        'Nutte': 'werwolf.nutte',
        'Werwolf': 'werwolf.werwolf'
         }


@bot.command(name='start-game')
@commands.has_role('werwolf.moderator')
async def start(ctx):
    guild_category = ctx.channel.category

    # Not that clean, but it's for use in a close env right now. Also if somebody can teach me lambdas ... ¯\_(ツ)_/¯
    voice_channel_users = guild_category.voice_channels[0].members

    # Append to list of running games. Guild Category is the id, voice_channel_users all users that are part of the game
    game_list[guild_category] = Game.Game(guild_category, voice_channel_users)

    # Lists to iterate over. Since they are going to be modified, they are deepcopied
    roles_to_iterate = copy.copy(roles)
    users_to_iterate = copy.copy(voice_channel_users)

    # Assign 'Dorfbewohner' to every player in game.
    dorfbewohner_role = discord.utils.get(ctx.guild.roles, name=roles['Dorfbewohner'])

    for user in voice_channel_users:
        try:
            await user.add_roles(dorfbewohner_role)
        except discord.Forbidden:
            await ctx.send('Insufficient Permission, contact an admin for help')
            return

    roles_to_iterate.pop('Dorfbewohner')

    # Assign every other role
    if len(roles_to_iterate) <= len(users_to_iterate):
        for game_role in roles_to_iterate:
            game_role_abc = discord.utils.get(ctx.guild.roles, name=roles[game_role])

            # TODO: Check if role is already added or exists
            rand_user = random.choice(users_to_iterate)
            rand_user.add_roles(game_role_abc)

            users_to_iterate.pop(rand_user)
    else:
        await ctx.send('Nicht genug Spieler, um zu starten')
        game_list.pop(guild_category)
        return

    # TODO: Output players playing
    await ctx.send(f'Spiel gestartet!')  # \n ' 'Es spielen: \n' ', '.join(game_list[guild_category].get_user_list()))


@bot.command(name='restart-game')
@commands.has_role('werwolf.moderator')
async def restart(ctx):
    await stop(ctx)
    await start(ctx)


@bot.command(name='stop-game')
@commands.has_role('werwolf.moderator')
async def stop(ctx):
    guild_category = ctx.channel.category
    game = game_list[guild_category]
    user_list = game.get_user_list()

    # TODO: bad style
    if game:
        for user in user_list:
            user_roles = user.roles
            for role in user_roles:
                if ('werwolf.' in role.name) and (role.name != 'werewolf.moderator'):
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
