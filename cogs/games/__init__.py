import json
import html
import discord
import asyncio
import random
import textwrap
from time import time
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands
from utils.CustomCog import Cog
from utils import Paginators


class Games(Cog):
    '''The Games extension. A collection of very simple games,
    that might make users smile.'''

    def __init__(self, bot):
        self.bot = bot
        self.name = '🕹 Games'

    async def question(self, difficulty: str):
        if difficulty not in ('easy', 'medium', 'hard'):
            raise ValueError('Invalid difficulty specified.')
        async with self.bot.session.get(f"{self.bot.config['API']['trivia_api']}&difficulty={difficulty}") as r:
            js = await r.json()
        js = js['results'][0]
        js['incorrect_answers'] = [html.unescape(x) for x in js['incorrect_answers']]
        js['question'] = html.unescape(js['question'])
        js['correct_answer'] = html.unescape(js['correct_answer'])
        return js

    async def answer(self, ctx, q):
        """Takes a question parameter."""
        entr = q['incorrect_answers'] + [q['correct_answer']]
        entr = random.sample(entr, len(entr))
        ans = await Paginators.Poll(title=q['question'], entries=entr).pagination(ctx)
        return ans == q['correct_answer']

    @commands.command()
    async def trivia(self, ctx, difficulty: str = 'medium'):
        """Trivia game! Has 3 difficulties: `easy`, `medium` and `hard`.
        Args: difficulty (optional): Questions difficulty in the game. Defaults to "easy".
        Returns: A correct answer."""
        try:
            q = await self.question(difficulty.lower())
        except ValueError:
            return await ctx.send('Invalid difficulty specified.')
        if await self.answer(ctx, q):
            await ctx.send(f'**{ctx.author}** answered correct.')
        else:
            await ctx.send(f'**{ctx.author}** was a bit wrong\nThe answer is: `{q["correct_answer"]}`.')

    @commands.command(aliases=['tr'])
    @commands.max_concurrency(1, per=commands.BucketType.channel)
    async def typeracer(self, ctx):
        """Typeracer Command. Compete with others!
        Returns: Average WPM of the winner, time spent to type and the original text."""
        cs = self.bot.session
        r = await cs.get(self.bot.config['API']['quote_api'])
        buffer = BytesIO()
        to_wrap = random.choice(json.loads(await r.read()))['text']
        text = '\n'.join(textwrap.wrap(to_wrap, 30))
        font = ImageFont.truetype('./data/fonts/monoid.ttf', size=30)
        w, h = font.getsize_multiline(text)
        with Image.new('RGB', (w + 10, h + 10)) as base:
            canvas = ImageDraw.Draw(base)
            canvas.multiline_text((5, 5), text, font=font)
            base.save(buffer, 'png', optimize=True)
        buffer.seek(0)
        race = await ctx.send(
            file=discord.File(buffer, 'typeracer.png'),
            embed=self.bot.embed.default(
                ctx, title='Typeracer', description='see who is fastest at typing.'
            ).set_image(url='attachment://typeracer.png'))
        start = time()
        try:
            msg = await self.bot.wait_for('message', check=lambda m: m.content == to_wrap, timeout=60.0)
            if not msg:
                return
            end = time()
            final = round(end - start, 2)
            await ctx.send(embed=self.bot.embed(
                title=f'{msg.author.display_name} won!',
                description=f'**Done in**: {final}s\n**Average WPM**: {round(len(to_wrap.split()) * (60.0 / final))} words\n**Original text:**```diff\n+ {to_wrap}```',
            ))
        except asyncio.TimeoutError:
            try:
                await race.delete()
            except discord.errors.NotFound:
                pass

    @commands.command(aliases=['rps'])
    async def rockpaperscissors(self, ctx):
        """The Rock | Paper | Scissors game.
        There are three different reactions, depending on your choice
        random will find did you win, lose or made draw."""
        rps_dict = {
            "🪨": {"🪨": "draw", "📄": "lose", "✂": "win"},
            "📄": {"🪨": "win", "📄": "draw", "✂": "lose"},
            "✂": {"🪨": "lose", "📄": "win", "✂": "draw"}
        }
        choice = random.choice([*rps_dict.keys()])
        msg = await ctx.send(embed=self.bot.embed(description="**Choose one 👇**").set_footer(text="10 seconds left⏰"))
        for r in rps_dict.keys():
            await msg.add_reaction(r)
        try:
            r, u = await self.bot.wait_for(
                'reaction_add',
                timeout=10,
                check=lambda re, us: us == ctx.author and str(re) in rps_dict.keys() and re.message.id == msg.id
            )
            game = rps_dict.get(str(r.emoji))
            await msg.edit(embed=self.bot.embed(description=f'''Result: **{game[choice].upper()}**\nMy choice: **{choice}**\nYour choice: **{str(r.emoji)}**'''))
        except asyncio.TimeoutError:
            await msg.delete()

    @commands.command(aliases=['slots', 'bet'])
    async def slot(self, ctx):
        """Play the game on a slot machine!"""
        emojis = '🍎🍊🍐🍋🍉🍇🍓🍒'
        a = random.choice(emojis)
        b = random.choice(emojis)
        c = random.choice(emojis)
        slotmachine = f'{a} | {b} | {c}\n{ctx.author.display_name},'
        if (a == b == c):
            await ctx.send(f'{slotmachine} All 3 match, you are a big winner! 🎉')
        elif (a == b) or (a == c) or (b == c):
            await ctx.send(f'{slotmachine} 2 match, you won! 🎉')
        else:
            await ctx.send(f'{slotmachine} No matches, you have to buy me a VPS 😳')


def setup(bot):
    bot.add_cog(Games(bot))