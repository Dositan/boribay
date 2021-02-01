from discord import File
import textwrap
from io import BytesIO
from wand.image import Image as WI
from PIL import Image, ImageDraw, ImageFont
from utils.Converters import ImageConverter, ImageURLConverter


async def welcome_card(member):
    font = ImageFont.truetype('./data/fonts/arial_bold.ttf', size=20)
    join_text, member_text = (f'{member} just spawned in the server.', f'Member #{member.guild.member_count}')
    (join_w, _), (member_w, _) = font.getsize(join_text), font.getsize(member_text)
    buffer = BytesIO()
    data = BytesIO(await member.avatar_url.read())
    pfp = Image.open(data).resize((263, 263))
    with Image.new('RGB', (600, 400)) as card:
        card.paste(pfp, (170, 32))
        draw = ImageDraw.Draw(card)
        draw.text(((600 - join_w) / 2, 309), join_text, (255, 255, 255), font=font)
        draw.text(((600 - member_w) / 2, 1), member_text, (169, 169, 169), font=font)
        card.save(buffer, 'png', optimize=True)
    buffer.seek(0)
    file = File(buffer, 'welcomer.png')
    return file


async def make_image_url(ctx, arg: str):
    c = ImageURLConverter()
    image = await c.convert(ctx, arg)
    if not image:
        if ctx.message.attachments:
            image = ctx.message.attachments[0].url
            return image
        else:
            image = str(ctx.author.avatar_url_as(static_format='png', format='png', size=512))
            return image
    else:
        return image


async def make_image(ctx, argument: str):
    converter = ImageConverter()
    image = await converter.convert(ctx, argument)
    if not image:
        if ctx.message.attachments:
            layout = ctx.message.attachments[0]
            image = await layout.read()
            return image
        else:
            layout = ctx.author.avatar_url_as(static_format='png', format='png', size=128)
            image = await layout.read()
            return image
    else:
        return image


class Manip:

    @staticmethod
    def clyde(txt: str):
        with Image.open('./data/layouts/clyde.png') as img:
            font = ImageFont.truetype('./data/fonts/whitneybook.otf', 18)
            draw = ImageDraw.Draw(img)
            draw.text((72, 33), txt, (255, 255, 255), font=font)
            buffer = BytesIO()
            img.save(buffer, 'png')
        buffer.seek(0)
        return buffer

    @staticmethod
    def theory(txt: str):
        with Image.open('./data/layouts/lisa.jpg') as img:
            wrapped = textwrap.wrap(txt, 24)
            font = ImageFont.truetype('./data/fonts/impact.ttf', 30)
            draw = ImageDraw.Draw(img)
            draw.text((161, 72), '\n'.join(wrapped), (0, 0, 0), font=font)
            buffer = BytesIO()
            img.save(buffer, 'png')
        buffer.seek(0)
        return buffer

    @staticmethod
    def drake(no: str, yes: str):
        with Image.open('./data/layouts/drake.jpg') as img:
            no_wrapped = textwrap.wrap(text=no, width=13)
            yes_wrapped = textwrap.wrap(text=yes, width=13)
            font = ImageFont.truetype('./data/fonts/arial_bold.ttf', size=28)
            draw = ImageDraw.Draw(img)
            draw.text((270, 10), '\n'.join(no_wrapped), (0, 0, 0), font=font)
            draw.text((270, 267), '\n'.join(yes_wrapped), (0, 0, 0), font=font)
            buffer = BytesIO()
            img.save(buffer, 'png')
        buffer.seek(0)
        return buffer

    @staticmethod
    def press_f(image: BytesIO):
        image = Image.open(image).resize((47, 87))
        image = image.convert(mode='RGBA').rotate(14)
        with Image.open('./data/layouts/f.jpg') as img:
            img.paste(image, (315, 72))
            buffer = BytesIO()
            img.save(buffer, 'png')
        buffer.seek(0)
        return buffer

    @staticmethod
    def swirl(image: BytesIO, degree: int = 90):
        with WI(file=image) as img:
            if int(degree) > 360:
                degree = 360
            elif int(degree) < -360:
                degree = -360
            else:
                degree = degree
            img.swirl(degree=degree)
            buffer = BytesIO()
            img.save(file=buffer)

        buffer.seek(0)
        return buffer
