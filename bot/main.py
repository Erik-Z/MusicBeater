import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
from ytdl import YTDLSource
from utils import *

load_dotenv()
DISCORD_TOKEN = os.getenv("discord_token")

intents = discord.Intents().default()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

url_queue = {}
queue = {}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn', 'executable': "./bot/ffmpeg.exe"}


def play_queue(voice_client):
    server_id = voice_client.guild.id
    print(url_queue[server_id])
    if len(queue[server_id]) != 0:
        url_queue[server_id].pop(0)
        voice_client.play(discord.FFmpegPCMAudio(queue[server_id].pop(0), **FFMPEG_OPTIONS),
                          after=lambda x: play_queue(voice_client))
    else:
        return


@bot.command(name='play', help='Joins author voice channel and plays song')
async def play(ctx, *urls: str):
    if ctx.message.author.voice:
        voice_channel = ctx.message.author.voice.channel
        voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        server_id = ctx.guild.id
        if server_id not in queue:
            queue[server_id] = []
            url_queue[server_id] = []
        if not voice_client:
            await voice_channel.connect()
            voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if len(urls) == 1:
            if voice_client.is_playing():
                url_queue[server_id].append(urls[0])
                queue[server_id].append(await YTDLSource.from_url(urls[0], loop=bot.loop))
                await ctx.send(f"Queued #{len(queue[server_id])}")
            else:
                filename = await YTDLSource.from_url(urls[0], loop=bot.loop)
                voice_client.play(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS),
                                  after=lambda x: play_queue(voice_client))
        else:
            if voice_client.is_playing():
                for url in urls:
                    url_queue[server_id].append(url)
                    queue[server_id].append(await YTDLSource.from_url(url, loop=bot.loop))
                await ctx.send(f"Queued #{len(queue[server_id])}")
            else:
                filename = await YTDLSource.from_url(urls[0], loop=bot.loop)
                voice_client.play(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS),
                                  after=lambda x: play_queue(voice_client))
                for url in urls[1:]:
                    url_queue[server_id].append(url)
                    queue[server_id].append(await YTDLSource.from_url(url, loop=bot.loop))
                await ctx.send(f"Queued #{len(queue[server_id])}")
    else:
        await ctx.send(f"You need to be in a voice channel.")


@bot.command(name='nplay', help='Plays a song by name')
async def nplay(ctx, *title):
    if ctx.message.author.voice:
        voice_channel = ctx.message.author.voice.channel
        voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        server_id = ctx.guild.id
        if not server_id in queue:
            queue[server_id] = []
            url_queue[server_id] = []
        if not voice_client:
            await voice_channel.connect()
            voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        url = "https://www.youtube.com/watch?v=" + get_url_from_title("+".join(title))
        if voice_client.is_playing():
            url_queue[server_id].append(url)
            queue[server_id].append(await YTDLSource.from_url(url, loop=bot.loop))
            await ctx.send(f"Queued #{len(queue[server_id])}")
        else:
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            voice_client.play(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS),
                              after=lambda x: play_queue(voice_client))
    else:
        await ctx.send(f"You need to be in a voice channel.")


@bot.command(name='queued', help='Shows list of songs currently queued')
async def queued(ctx):
    server_id = ctx.guild.id
    if len(url_queue[server_id]) != 0:
        queued_list = discord.Embed(title="Queued Songs",
                                    color=discord.Color.blue())
        for index, video_url in enumerate(url_queue[server_id]):
            queued_list.add_field(name=f"{index + 1}.", value=f"{get_title_from_yt_url(video_url)}", inline=False)
        await ctx.send(embed=queued_list)
        return
    await ctx.send(embed=discord.Embed(description="No songs currently queued."))


@bot.command(name='skip', help='Skips song to next one in queue')
async def skip(ctx):
    if ctx.message.author.voice:
        voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        voice_client.stop()
    else:
        await ctx.send(f"You need to be in a voice channel.")


@bot.command(name='clear', help='Clears the queue')
async def clear_queue(ctx):
    if ctx.message.author.voice:
        server_id = ctx.guild.id
        queue[server_id] = []
        url_queue[server_id] = []
        await ctx.send(f"Queued Cleared.")
    else:
        await ctx.send(f"You need to be in a voice channel.")


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


if __name__ == '__main__':
    print(os.listdir('.'))
    print(os.listdir('./bot'))
    # Production
    for cog in os.listdir('./bot/cogs'):
    # Local
    # for cog in os.listdir('./cogs'):
        if cog.endswith('.py'):
            bot.load_extension(f'cogs.{cog[:-3]}')
    bot.run(DISCORD_TOKEN)
