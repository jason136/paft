import discord, math, os
from discord import *
from discord.ext import commands
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO

class utility(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("utility is initialized")
    
    async def load_img(self, ctx):
        for file in ctx.message.attachments:
            fp = BytesIO()
            await file.save(fp)
            image = Image.open(fp)
            print('load attempting')
            if str(image.format) == 'GIF':
                gif_frames = []
                for frame in range (0, image.n_frames):
                    image.seek(frame)
                    gif_frames.append(image.copy())
                image.save('pictures/{}_gif.gif'.format(ctx.message.author), optimize=True, save_all=True, append_images=gif_frames)
                await ctx.send('gif is loaded')
                if os.path.exists('pictures/{}_image.jpg'.format(ctx.message.author)):
                    os.remove('pictures/{}_image.jpg'.format(ctx.message.author))
                await ctx.send(file=discord.File('pictures/{}_gif.gif'.format(ctx.message.author)))
            else:
                image.convert('RGB').save('pictures/{}_image.jpg'.format(ctx.message.author), optimize=True)
                await ctx.send('image is loaded')
                if os.path.exists('pictures/{}_gif.gif'.format(ctx.message.author)):
                    os.remove('pictures/{}_gif.gif'.format(ctx.message.author))
            print(image.format)

    async def complex_load(self, ctx):
        if ctx.message.attachments:
            await self.load_img(ctx)
        try:
            return Image.open('pictures/{}_image.jpg'.format(ctx.message.author))
        except:
            try: 
                return Image.open('pictures/{}_gif.gif'.format(ctx.message.author))
            except:
                await ctx.send('no image loaded')
                return

    @commands.command()
    async def load(self, ctx):
        await self.load_img(ctx)

    async def pixel_to_ascii(self, image):
        chars = ["@", "#", "$", "%", "?", "*", "+", ";", ":", ",", "."]
        pixels = image.getdata()
        ascii_str = ""
        for pixel in pixels:
            ascii_str += chars[pixel//24]
        return ascii_str

    @commands.command()
    async def ascii(self, ctx):
        image = await self.complex_load(ctx)
        contraster = ImageEnhance.Contrast(image)
        image = contraster.enhance(2)
        height, width = image.size
        x = (1 / (height / width))
        print('original aspect ratio: {}'.format(x))
        print(height)
        print(width)
        print('ze number: {}'.format(((2 ** (-5 * x + 5.5)) + 3) / (2 * x)))
        height = height // (((2 ** (-5 * x + 5.5)) + 3) / (2 * x))
        ratio = (height / width)
        print('ratio: {}'.format(ratio))
        height = int(44 * math.sqrt(ratio))
        width = int(44 / math.sqrt(ratio))
        if (width * height) > 1920:
            width -= 1
            height -= 1
        image = image.resize((width, height), Image.ANTIALIAS)
        image = image.convert('L')
        ascii_str = await self.pixel_to_ascii(image)
        ascii_str_len = len(ascii_str)
        ascii_img = ''
        img_width = image.width
        for i in range(0, ascii_str_len, img_width):
            ascii_img += ascii_str[i:i+img_width] + "\n"
        with open("resources/ascii_image.txt", "w") as f:
            f.write(ascii_img)
        await ctx.send('```{}```'.format(ascii_img))

    @commands.command()
    async def contrast(self, ctx, arg:float=226):
        if arg == 226:
            raise commands.BadArgument
        image = await self.complex_load(ctx)
        if str(image.format) == 'GIF':
            gif_frames = []
            for frame in range (0, image.n_frames):
                image.seek(frame)
                output = image.copy()
                #contraster = ImageEnhance.Contrast(image)
                #image = contraster.enhance(arg)
                gif_frames.append(output)
            image.save('pictures/{}_gif.gif'.format(ctx.message.author), optimize=True, save_all=True, append_images=gif_frames)
            await ctx.send(file=discord.File('pictures/{}_gif.gif'.format(ctx.message.author)))
        else:
            contraster = ImageEnhance.Contrast(image)
            contraster.enhance(arg).save('pictures/{}_image.jpg'.format(ctx.message.author), optimize=True)
            await ctx.send(file=discord.File('pictures/{}_image.jpg'.format(ctx.message.author)))
        

    @commands.command()
    async def brightness(self, ctx, arg:float=226):
        if arg == 226 or arg < 0:
            raise commands.BadArgument
        image = await self.complex_load(ctx)
        brightness = ImageEnhance.Brightness(image)
        brightness.enhance(arg).save('pictures/{}_image.jpg'.format(ctx.message.author), optimize=True)
        await ctx.send(file=discord.File('pictures/{}_image.jpg'.format(ctx.message.author)))

    @commands.command()
    async def scale(self, ctx, arg:float=226):
        if arg < 0:
            raise commands.BadArgument
        image = await self.complex_load(ctx)
        width, height = image.size
        new_width = int(width * arg)
        new_height = int(height * arg)
        if str(image.format) == 'GIF':
            gif_frames = []
            for frame in range (0, image.n_frames):
                image.seek(0)
                print('resize')
                image = image.resize((new_width, new_height), Image.ANTIALIAS)
                print('append')
                gif_frames.append(image.copy())
                print(gif_frames)
                print('end of loop, head on up')
            image.save('pictures/{}_gif.gif'.format(ctx.message.author), optimize=True, save_all=True, append_images=gif_frames)
            await ctx.send(file=discord.File('pictures/{}_gif.gif'.format(ctx.message.author)))
        else:
            if new_width * new_height > 89478485:
                raise commands.BadArgument
            image.resize((new_width, new_height), Image.ANTIALIAS).save('pictures/{}_image.jpg'.format(ctx.message.author))
            await ctx.send(file=discord.File('pictures/{}_image.jpg'.format(ctx.message.author)))
            await ctx.send('old size: {}, {} new size: {}, {}'.format(width, height, new_width, new_height))

    @commands.command()
    async def greyscale(self, ctx, arg:float=226):
        image = await self.complex_load(ctx)
        image.convert('L').save('pictures/{}_image.jpg'.format(ctx.message.author), optimize=True)
        await ctx.send(file=discord.File('pictures/{}_image.jpg'.format(ctx.message.author)))

    @commands.command()
    async def swapchannels(self, ctx, arg:float=226):
        image = await self.complex_load(ctx)
        print('attempt split')
        red, green, blue = image.split()
        print('attemp merge and save')
        image = Image.merge('RGB', (green, red, blue))
        image.save('pictures/{}_image.jpg'.format(ctx.message.author), optimize=True)
        await ctx.send(file=discord.File('pictures/{}_image.jpg'.format(ctx.message.author)))

    @commands.command()
    async def watermark(self, ctx):
        image = await self.complex_load(ctx)
        watermark = Image.open('resources/watermark.png')
        width, height = image.size
        background = Image.new('RGB', (width, int(height * 1.1)), 'black')
        background.paste(image, (0, 0))
        watermark_height = int(0.1 * height)
        watermark_width = int(watermark_height * 5.3376)
        watermark = watermark.resize((watermark_width, watermark_height), Image.ANTIALIAS)
        background.paste(watermark, ((width - watermark_width), height))
        background.save('pictures/{}_image.jpg'.format(ctx.message.author), optimize=True)
        await ctx.send(file=discord.File('pictures/{}_image.jpg'.format(ctx.message.author)))

    async def worholify(self, image, c1, c2, c3):
        pixels = list(image.getdata())
        new_pixels = []
        for pixel in pixels:
            average = (pixel[0] + pixel[1] + pixel[2]) / 3
            if average <= 75:
                pixel = c1
            elif average <= 150:
                pixel = c2
            else:
                pixel = c3
            new_pixels.append(pixel)
        print('worholify complete')
        worhol_base = Image.new('RGB', image.size) 
        worhol_base.putdata(new_pixels)
        return worhol_base

    @commands.command()
    async def worhol(self, ctx):
        image = await self.complex_load(ctx)
        image.thumbnail((1000, 1000))
        image = image.filter(ImageFilter.GaussianBlur(1))
        contraster = ImageEnhance.Contrast(image)
        image = contraster.enhance(2)
        worhol1 = await self.worholify(image, (239, 245, 66), (66, 245, 182), (10, 17, 204))
        worhol2 = await self.worholify(image, (247, 5, 255), (255, 198, 13), (17, 242, 250))
        worhol3 = await self.worholify(image, (7, 0, 222), (199, 166, 245), (255, 20, 71))
        worhol4 = await self.worholify(image, (47, 42, 105), (133, 198, 255), (255, 162, 0))
        worhol5 = await self.worholify(image, (66, 66, 66), (214, 214, 214), (255, 0, 0))
        worhol6 = await self.worholify(image, (219, 139, 0), (255, 244, 120), (172, 255, 71))
        worhol7 = await self.worholify(image, (236, 66, 255), (191, 191, 191), (11, 79, 67))
        worhol8 = await self.worholify(image, (242, 73, 0), (10, 138, 48), (255, 222, 59))
        worhol9 = await self.worholify(image, (93, 0, 255), (255, 174, 87), (230, 0, 255))
        width, height = image.size
        worhol_final = Image.new('RGB', (width * 3, height * 3))
        worhol_final.paste(worhol1, (0, 0))
        worhol_final.paste(worhol2, (width, 0))
        worhol_final.paste(worhol3, (width * 2, 0))
        worhol_final.paste(worhol4, (0, height))
        worhol_final.paste(worhol5, (width, height))
        worhol_final.paste(worhol6, (width * 2, height))
        worhol_final.paste(worhol7, (0, height * 2))
        worhol_final.paste(worhol8, (width, height * 2))
        worhol_final.paste(worhol9, (width * 2, height * 2))
        worhol_final.save('pictures/{}_image.jpg'.format(ctx.author), optimize=True)
        await ctx.send(file=discord.File('pictures/{}_image.jpg'.format(ctx.author)))
        
def setup(client):
    client.add_cog(utility(client))
    print('utility being loaded!')

def teardown(client):
    print('utility being unloaded!')