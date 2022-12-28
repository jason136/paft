import discord
import time, os, asyncio, random
from discord.ext import commands
from discord.utils import find
import resources.connectfour as c4
import chess as chesss
import chess.engine as engine
import tokens

intents = discord.Intents.all()
client = commands.Bot(command_prefix='^', intents=intents)
client.load_extension('cogs.apis')
client.load_extension('cogs.utility')
client.load_extension('cogs.music')

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Streaming(name="near", url="https://www.youtube.com/watch?v=XC1LbLJO6fQ&t=2013s"))
    # await client.change_presence(activity=discord.Streaming(name="near", url="https://www.youtube.com/watch?v=ox2CP5oz61g&t=2013s"))
    # await client.change_presence(activity=discord.Game(name="being but a shadow of his former self"))
    print('We have logged in as {0.user}'.format(client))

@client.command()
async def apis(ctx):
    client.reload_extension('cogs.apis')

@client.command()
async def utility(ctx):
    client.reload_extension('cogs.utility')

@client.command()
async def music(ctx):
    client.reload_extension('cogs.music')

@client.command()
async def cogs(ctx):
    client.reload_extension('cogs.apis')
    client.reload_extension('cogs.utility')
    client.reload_extension('cogs.music')  

@client.event
async def on_guild_join(guild):
    general = find(lambda x: x.name == 'general',  guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send('henlo my prefix is ^')

client.remove_command('help')
@client.command()
async def help(ctx):
    embed = discord.Embed(title="Commands:", color=0x000000)
    embed.add_field(name="pong", value="ping", inline=False)
    embed.add_field(name="ping", value="pong", inline=False)
    embed.add_field(name="DM Shitstorm (try -h as the message)", value="dm", inline=False)
    embed.add_field(name="Urban Dictionary", value="urban", inline=False)
    embed.add_field(name="Rando Meme", value="mem", inline=False)
    embed.add_field(name="Load an image for use (image as attatchment)", value="load", inline=False)
    embed.add_field(name="Print ascii art (image loaded or as attatchment)", value="ascii", inline=False)
    embed.add_field(name="Edit contrast of image (provide positive value, 1 for no change)", value="contrast", inline=False)
    embed.add_field(name="Edit brightness of image (provide positive value, 1 for no change)", value="brightness", inline=False)
    embed.add_field(name="Scale image (provide positive value, must stay under 8mb file size limit)", value="scale", inline=False)
    embed.add_field(name="Add a little touch by Paft", value="watermark", inline=False)
    embed.add_field(name="Connect Four", value="connect4", inline=False)
    embed.add_field(name="Anime Waifu Art", value="safebo", inline=False)
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/750070208248414250/824358236949839872/paft_pfp.jpg')
    await ctx.send(embed=embed)

@client.command()
async def nsfwhelp(ctx):
    embed = discord.Embed(title="Commands:", color=0xff1c64)
    embed.add_field(name="search for something", value="search", inline=False)
    embed.add_field(name="the 6 digits you know what", value="id", inline=False)
    await ctx.send(embed=embed)

@client.command()
async def ping(ctx):
    await ctx.send(f"pong! {client.latency}")

@client.command()
async def pong(ctx):
    await ctx.send(f"ping! {client.latency}")

@client.command()
async def pfp(ctx, user:discord.User):
    embed = discord.Embed(title="", description='', color=0x000000)
    embed.set_image(url=(user.avatar_url))
    await ctx.send(embed=embed)

@client.command()
async def mem(ctx):
    print(random.choice(os.listdir('mem/')))
    await ctx.send(file=discord.File('mem/' + str(random.choice(os.listdir('mem/')))))

stop = False
@client.command()
async def e(ctx, *args):
    global stop
    stop = True
    await ctx.channel.purge(limit=1)

@client.command()
async def dm(ctx, user:discord.User, *args):
    text = open('resources/links.txt', 'r')
    links = text.readlines()
    arguments = list(args)
    try:
        tmp = int(arguments[0])
        loop = int(arguments.pop(0))
    except:
        loop = 1
    message = str(' '.join(arguments)) or 'hello'
    await ctx.send('pinging time')
    x = 0
    while x < loop:
        print('interation ' + str(x) + ' out of ' + str(loop))
        if not message == '-h':
            await user.send(message)
        else:
            await user.send(links[random.randint(0, len(links))])
        x += 1
        await asyncio.sleep(1)
        global stop
        if (stop):
            stop = False
            x = loop
    await ctx.send('it has been done')

NONE = '⚫'
RED = '🔴'
YELLOW = '🟡'

@client.command()
async def connect4(ctx):
    g = ConnectFour()
    turn = RED
    player2 = None
    msg = await ctx.send(embed=g.printBoard(ctx, turn, player2))
    reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '🔁']
    for emoji in reactions:
        await msg.add_reaction(emoji)
    while 1:
        def check(reaction, user):
            return (user == ctx.message.author or user == player2 or (player2 == None and user != msg.author)) and ((str(reaction.emoji) in reactions) or str(reaction.emoji) == '😐') and reaction.message == msg
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=120.0, check=check)
        except asyncio.TimeoutError:
            closeembed = discord.Embed(title='Game has timed out', color=0x808080)
            await msg.edit(embed=closeembed)
            [await msg.remove_reaction(reaction, msg.author) for reaction in reactions]
            return
        await msg.remove_reaction(str(reaction), user)
        if str(reaction) == '😐':
            if not player2: player2 = 'bingus'
            await msg.edit(embed=g.printBoard(ctx, RED if user == ctx.message.author else YELLOW, player2, user))
            [await msg.remove_reaction(reaction, msg.author) for reaction in reactions]
            return
        if str(reaction) == '🔁' and (user == ctx.message.author or user == player2):
                await msg.delete()
                msg = await ctx.send(embed=g.printBoard(ctx, turn, player2))
                for emoji in reactions:
                    await msg.add_reaction(emoji)
                continue
        if player2 == None and user != ctx.message.author and user != msg.author:
            player2 = user
        if user == ctx.message.author and turn == RED or user == player2 and turn == YELLOW:
            row = int(reactions.index(str(reaction)))
            try:
                g.insert(row, turn)
                turn = YELLOW if turn == RED else RED
                await msg.edit(embed=g.printBoard(ctx, turn, player2))
            except Exception as e: 
                print('>>>>>{}<<<<<<'.format(str(e)))
                if str(e) == '🔴 won!' or str(e) == '🟡 won!':
                    await msg.edit(embed=g.printBoard(ctx, turn, player2, ctx.message.author if str(e) == '🔴 won!' else player2))
                    [await msg.remove_reaction(reaction, msg.author) for reaction in reactions]
                    return
                else:
                    await ctx.send('That column is full')

class ConnectFour(c4.Game):
    def printBoard(self, ctx, turn, player2, winner=None):
        board = '```⠀🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦'
        for y in range(self.rows):
            board += ('\n🟦')
            board += ('  '.join(str(self.board[x][y]) for x in range(self.cols)))
            board += ('🟦')
        board += '\n⠀🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦```'
        win_message = '{} has won!'.format(winner)
        embed = discord.Embed(title=('{}\'s turn'.format('Red' if turn == RED else 'Yellow')) if winner == None else win_message, description=board, color=(0xff0000 if turn == RED else 0xffff00), rich=True)
        embed.set_footer(text='{} is Red, {}'.format(ctx.message.author, '{} is Yellow'.format(player2) if player2 != None else ''))
        return embed
#⠀
#🔴🟡⚫


@client.command()
async def chess(ctx, *args):
    player2 = None
    firstmove = ' '
    secondmove = ' '
    firstmove2 = ' '
    secondmove2 = ' '
    lastmove = ''
    turn = 'white'
    board = chesss.Board()
    try:
        arg = args[0] if args else None
        startembed = discord.Embed(title='White\'s turn\nMove:    ->   ', color=0xfefefe, rich=True)
        if arg == 'ai':
            transport, engine = await chesss.engine.popen_uci('resources/stockfish.exe')
            startembed.set_footer(text='{} is White, Paft is Black'.format(ctx.message.author))
        else:
            startembed.set_footer(text='{} is White'.format(ctx.message.author))
        startembed.set_image(url='https://backscattering.de/web-boardimage/board.png?fen={}8&coordinates=true'.format(board.fen()).replace(" ", "%20"))
        print('https://backscattering.de/web-boardimage/board.png?fen={}8&coordinates=true'.format(board.fen()).replace(" ", "%20"))
        msg = await ctx.send(embed=startembed)
    except Exception as e:
        print(e)
    reactions = ['🇦', '🇧', '🇨',  '🇩',  '🇪',  '🇫',  '🇬',  '🇭', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣']
    indexes = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', '1', '2', '3', '4', '5', '6', '7', '8']
    for emoji in reactions:
        await msg.add_reaction(emoji)
    await msg.add_reaction('❌')
    await msg.add_reaction('🔁')
    while 1:
        def check(reaction, user):
            return user != msg.author and ((str(reaction.emoji) in reactions) or str(reaction.emoji) == '😐' or str(reaction.emoji) == '❌' or str(reaction.emoji) == '🔁') and reaction.message == msg
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=300.0, check=check)
        except asyncio.TimeoutError:
            closeembed = discord.Embed(title='Game has timed out', color=0x808080)
            await msg.edit(embed=closeembed)
            [await msg.remove_reaction(reaction, msg.author) for reaction in reactions]
            await msg.remove_reaction('❌', msg.author)
            await msg.remove_reaction('🔁', msg.author)
            return
        await msg.remove_reaction(str(reaction), user)
        if arg == 'ai':
            player2 = 'Paft'
        elif player2 == None and user != ctx.message.author:
            player2 = user
        try:
            if str(reaction) == '🔁' and (user == ctx.message.author or user == player2):
                    await msg.delete()
                    move = firstmove + secondmove + ' -> ' + firstmove2 + secondmove2
                    embed = discord.Embed(title=('{}\'s turn \nMove: {}'.format('White' if turn == 'white' else 'Black', move)), color=(0xfefefe if turn == 'white' else 0x000000), rich=True)
                    embed.set_image(url='https://backscattering.de/web-boardimage/board.png?fen={}8&orientation={}&{}coordinates=true'.format(board.fen(), turn, 'lastMove=' + lastmove  + '&' if lastmove != '' else '').replace(" ", "%20"))
                    embed.set_footer(text='{} is White, {}'.format(ctx.message.author, '{} is Black'.format(player2) if player2 != None else ''))
                    msg = await ctx.send(embed=embed)
                    for emoji in reactions:
                        await msg.add_reaction(emoji)
                    await msg.add_reaction('❌')
                    await msg.add_reaction('🔁')
                    continue
            if (user == ctx.message.author and turn == 'white') or (user == player2 and turn == 'black'): 
                if str(reaction) == '❌':
                    firstmove = ' '
                    secondmove = ' '
                    firstmove2 = ' '
                    secondmove2 = ' '
                if firstmove == ' ':
                    if str(reaction) in reactions[:8]:
                        firstmove = indexes[reactions.index(str(reaction))]
                elif secondmove == ' ':
                    if str(reaction) in reactions[-8:]:
                        secondmove = indexes[reactions.index(str(reaction))]
                elif firstmove2 == ' ':
                    if str(reaction) in reactions[:8]:
                        firstmove2 = indexes[reactions.index(str(reaction))]
                elif secondmove2 == ' ':
                    if str(reaction) in reactions[-8:]:
                        secondmove2 = indexes[reactions.index(str(reaction))]
                        if chesss.Move.from_uci(firstmove + secondmove + firstmove2 + secondmove2) in board.legal_moves:
                            print('move valid')
                            board.push_san(firstmove + secondmove + firstmove2 + secondmove2)
                            lastmove = firstmove + secondmove + firstmove2 + secondmove2
                            turn = 'black' if turn == 'white' else 'white'
                            if arg == 'ai':
                                result = await engine.play(board, chesss.engine.Limit(time=0.1))
                                board.push(result.move)
                                turn = 'white'
                                lastmove = str(result.move)
                        else:
                            print('move invalid')
                        firstmove = ' '
                        secondmove = ' '
                        firstmove2 = ' '
                        secondmove2 = ' '
                print(firstmove + secondmove + firstmove2 + secondmove2)
            if board.is_game_over(): 
                if board.is_checkmate():
                    print('win by checkmate')
                    endembed = discord.Embed(title=('{}\'s win by checkmate'.format(ctx.message.author if turn == 'black' else player2)), color=(0xfefefe if turn == 'black' else 0x000000), rich=True)
                elif board.is_stalemate():
                    endembed = discord.Embed(title='stalemate', color=0x808080, rich=True)
                    print('stalemate')
                elif board.is_insufficient_material():
                    endembed = discord.Embed(title=('{}\'s win by opponent insufficient material'.format(ctx.message.author if turn == 'black' else player2)), color=(0xfefefe if turn == 'black' else 0x000000), rich=True)
                    print('insufficient material')
                endembed.set_image(url='https://backscattering.de/web-boardimage/board.png?fen={}8&orientation={}&{}coordinates=true'.format(board.fen(), 'white' if (turn == 'black' or arg == 'ai') else 'black', 'lastMove=' + lastmove  + '&').replace(" ", "%20"))
                await msg.edit(embed=endembed)
                [await msg.remove_reaction(reaction, msg.author) for reaction in reactions]
                await msg.remove_reaction('❌', msg.author)
                await msg.remove_reaction('🔁', msg.author)
                return
            ischeck = turn if board.is_check() else None
        except Exception as e:
            print('error' + e)
        move = firstmove + secondmove + ' -> ' + firstmove2 + secondmove2
        embed = discord.Embed(title=('{}\'s turn \nMove: {}{}'.format('White' if turn == 'white' else 'Black', move, '\n' + ischeck + ' is in check' if ischeck else '')), color=(0xfefefe if turn == 'white' else 0x000000), rich=True)
        embed.set_image(url='https://backscattering.de/web-boardimage/board.png?fen={}8&orientation={}&{}coordinates=true'.format(board.fen(), turn, 'lastMove=' + lastmove  + '&' if lastmove != '' else '').replace(" ", "%20"))
        embed.set_footer(text='{} is White, {}'.format(ctx.message.author, '{} is Black'.format(player2) if player2 != None else ''))
        await msg.edit(embed=embed)

@client.command()
async def clean(ctx, limit: int):
    await ctx.channel.purge(limit=limit)

text = open('resources/faces.txt', encoding="utf8")
faces = text.readlines()

@client.command()
async def spool(ctx, *args):
    try:
        if ctx.channel == client.get_guild(755573870789918780).get_channel(858974762655285249):
            channel = client.get_guild(762103433325969408).get_channel(762103433325969411)
            await channel.send(str(' '.join(args)))
    except Exception as e:
        print(e)

@client.command()
async def invite(ctx):
    link = await ctx.channel.create_invite(max_age = 3000)
    print(link)

@client.event
async def on_message(message):
    #print(message.guild.id)
    try: 
        print('{} - {}: {}: {} '.format(time.strftime('%a %H:%M:%S'), message.author.guild.name, str(message.author), message.content))
    except AttributeError:
        print('{} - In DM: {}: {} '.format(time.strftime('%a %H:%M:%S'), str(message.author), message.content))
    if 'paft' in message.content.lower():
        await message.channel.send(str(faces[random.randint(0, len(faces))]))            
    await client.process_commands(message)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.UserNotFound):
        await ctx.send('the correct syntax is ^dm *number* *@user* *message*') 
    elif isinstance(error, commands.BadArgument):
        await ctx.send('please provide a valid number')

client.run(tokens.token)