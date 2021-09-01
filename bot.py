import discord
from discord import player
from discord.channel import VoiceChannel
from discord.ext import commands,  tasks
import youtube_dl
from random import choice
from youtube_dl import YoutubeDL

# start

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

# end


client = commands.Bot(command_prefix='!')

status = ['Jamming out music!', 'Eating!', 'Sleeping!']

@client.event
async def on_ready():
    change_status.start()
    print('Bot is online!')

@client.command(name='ping', help='this command returns the latnecy')
async def ping(ctx):
    await ctx.send(f'**pong!** latnecy: {round(client.latency * 1000)}ms')

@client.command(name='hello', help='this command returns the hello message')
async def hello(ctx):
    responses  = ['***grumble*** Why did you wake me up?', 'fuck you!', 'Hello, how are you?', 'love being here!', 'Hi', '**Wasssuup!**']
    await ctx.send(choice(responses))

@client.command(name='die', help='this command returns the die message')
async def hello(ctx):
    responses  = ['Nooooo1', 'Fuck you!', 'Don\'t do that to me!', 'Hate you!', 'Good bye!']
    await ctx.send(choice(responses))

@client.command(name='play', help='this command plays a song')
async def play(ctx, url):
    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel")
        return

    else:
        channel = ctx.message.author.voice.channel

    await channel.connect()
    server = ctx.message.guild 
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=client.loop)
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    await ctx.send('**Now playing:** {}'.format(player.title))

@client.command(name='stop', help='this command stops a song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()
  
@client.command(name='pause', help='this command pause a song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.pause()

@client.command(name='resume', help='this command resume a song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.resume()


@tasks.loop(seconds=20)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(status)))

client.run('ODgyMjYyODA3ODI2MDM4ODU0.YS41RQ.jEfxDuj6IQ2GkMNdOpjdhKF-bOc')