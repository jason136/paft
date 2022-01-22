import discord, math, os, youtube_dl, asyncio
from discord import *
from discord.ext import commands
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO
from gtts import gTTS

working_directory = os.getcwd()

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'outtmpl': '%(title)s.%(ext)s',
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
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
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

class utility(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("music is initialized")
    
    async def verify_voice(self, ctx):
        if not ctx.author.voice:
            await ctx.send('You are not in a voice channel')
            return False
        else:
            return True

    @commands.command(pass_content=True)
    async def join(self, ctx):
        if not await self.verify_voice(ctx): return
        channel = ctx.author.voice.channel
        await channel.connect()
        
    @commands.command(pass_content=True)
    async def leave(self, ctx):
        if not await self.verify_voice(ctx): return
        vc = ctx.message.guild.voice_client
        try:
            tmp = vc.is_connected()
            self.looping = False
            await vc.disconnect()
        except Exception as e:
            print(e)
            await ctx.send("The bot is not connected to a voice channel.")

    queue_dict = {}
    skip = False
    looping = False
    player_active = False

    async def player(self, ctx, vc):
        self.player_active = True
        while self.queue_dict.keys():
            if len(self.queue_dict) > 1:
                await ctx.send('**Queued:** ``{}``'.format(list(self.queue_dict.keys())[-1]))
                print(self.queue_dict, 'returning')
                return
            await ctx.send('**Now playing:** ``{}``'.format(list(self.queue_dict.keys())[0]))
            print('pre play')
            try:
                os.chdir(working_directory + '/music/')
                vc.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=list(self.queue_dict.values())[0]))
                os.chdir(working_directory)
            except Exception as e:
                print(e)
            print('post play ')
            self.skip = False
            while vc.is_playing():
                await asyncio.sleep(1)
                print('playing music, skip: {}, looping: {}, queue: {}, song: {}'.format(self.skip, self.looping, len(list(self.queue_dict.keys())), list(self.queue_dict.keys())[0]))
                if self.skip:
                    vc.stop()
                    self.skip = False
                    print('skip executed')
            if self.looping:
                temp = list(self.queue_dict.values())[0]
                key = list(self.queue_dict.keys())[0]
                self.queue_dict.pop(key)
                self.queue_dict[key] = temp
            else:
                self.queue_dict.pop(list(self.queue_dict.keys())[0])
        print('music complete')
        self.player_active = False

    async def play_music(self, ctx, args): 
        try:
            arg = ' '.join(args)
            if not await self.verify_voice(ctx): return
            print('attemp play')
            vc = ctx.message.guild.voice_client
            try:
                tmp = ctx.message.guild.voice_client.is_connected()
            except:
                await ctx.invoke(self.join)
            server = ctx.message.guild
            vc = server.voice_client
            try:
                async with ctx.typing():
                    url = arg
                    os.chdir(working_directory + '/music/')
                    try:
                        dupe = False
                        try:
                            filename = await YTDLSource.from_url(url)
                        except WindowsError as winerror:
                            filename = str(winerror)[:-19].replace('\'', '')
                            dupe = True
                        if filename[-4:] == 'webm':
                            name = filename[:-5]
                        else:
                            name = filename[:-4]
                        name = name.replace('_', ' ')
                        if not dupe:
                            self.queue_dict[name] = filename
                        else:
                            self.queue_dict[str('{} v={}'.format(name, str(self.queue_dict.values()).count(filename)) + 1)] = filename
                    except Exception as e:
                        print(e)
                    os.chdir(working_directory)
                if not self.player_active: await self.player(ctx, vc)
                print('exit')
                print(self.queue_dict.keys())
            except Exception as e:
                print("error here", e)
        except Exception as e:
            print(e)

    @commands.command()
    async def play(self, ctx, *args):
        print('attempt play')
        await self.play_music(ctx, args)

    @commands.command()
    async def p(self, ctx, *args):
        print('attempt p')
        await self.play_music(ctx, args)

    @commands.command()
    async def pause(self, ctx):
        if not await self.verify_voice(ctx): return
        vc = ctx.message.guild.voice_client
        if vc.is_playing():
            await vc.pause()
        else:
            await ctx.send("paft is not playing anything")
    
    @commands.command()
    async def resume(self, ctx):
        if not await self.verify_voice(ctx): return
        vc = ctx.message.guild.voice_client
        if vc.is_paused():
            await vc.resume()
        else:
            await ctx.send("paft is not playing anything")

    @commands.command()
    async def stop(self, ctx):
        if not await self.verify_voice(ctx): return
        vc = ctx.message.guild.voice_client
        if vc.is_playing():
            self.queue_dict = {}
            self.looping = False
            vc.stop()
        else:
            await ctx.send("paft is not playing anything")

    @commands.command()
    async def skip(self, ctx):
        if not await self.verify_voice(ctx): return
        self.skip = True

    @commands.command()
    async def s(self, ctx):
        self.skip = True

    @commands.command()
    async def queue(self, ctx):
        await ctx.send(str('``' + ', '.join(self.queue_dict.keys()) + '``'))

    @commands.command()
    async def q(self, ctx):
        await ctx.send(str('``' + ', '.join(self.queue_dict.keys()) + '``'))

    @commands.command()
    async def loop(self, ctx):
        if self.looping:
            self.looping = False
            await ctx.send('looping is now off')
        else:
            self.looping = True
            await ctx.send('looping is now on')
        
    @commands.command()
    async def l(self, ctx):
        await ctx.invoke(self.loop)
    
    @commands.command()
    async def speak(self, ctx, *args):
        if not await self.verify_voice(ctx): return
        try:
            vc = ctx.message.guild.voice_client
            try:
                tmp = vc.is_connected()
            except Exception as e:
                print(e)
                await ctx.invoke(self.join)
            server = ctx.message.guild
            vc = server.voice_client
            tts = gTTS(' '.join(args), lang='en', tld='ie', slow=False)
            tts.save('music/voice.mp3')
            print('save attempted')
            try:
                self.queue_dict.append('voice.mp3')
            except Exception as e:
                print(e)
            await self.player(ctx, vc)
        except Exception as e:
            print(e)

def setup(client):
    client.add_cog(utility(client))
    print('music being loaded!')

def teardown(client):
    print('music being unloaded!')