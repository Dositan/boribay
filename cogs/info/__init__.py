import collections
import glob
import platform
from datetime import datetime, timedelta
from time import time
from typing import Optional

import discord
import humanize
import psutil as p
from discord.ext.commands import command, guild_only
from utils.CustomCog import Cog


class Info(Cog):
	'''Info extension. A module that contains commands that show
	different kinds of information. Host info, code count etc.'''

	def __init__(self, bot):
		self.bot = bot
		self.name = 'ℹ Info'
		self.status_emojis = {
			'online': '<:online:800050433207828550>',
			'idle': '<:idle:800050433141637130>',
			'dnd': '<:dnd:800050432478281738>',
			'offline': '<:offline:800051781228167249>'
		}

	@command(aliases=['modules', 'exts'])
	async def extensions(self, ctx):
		"""List of modules that work at a current time."""
		exts = []
		for ext in self.bot.cogs.keys():
			if ext is None:
				continue
			if (not await self.bot.is_owner(ctx.author) and ext in self.bot.owner_exts):
				continue
			exts.append(ext)
		exts = [exts[i: i + 3] for i in range(0, len(exts), 3)]
		length = [len(element) for row in exts for element in row]
		rows = []
		for row in exts:
			rows.append(''.join(e.ljust(max(length) + 2) for e in row))
		await ctx.send(embed=self.bot.embed(title='Modules that are working rn', description='```%s```' % '\n'.join(rows)))

	@command()
	async def uptime(self, ctx):
		"""Uptime command.
		Returns: uptime: How much time bot is online."""
		h, r = divmod((await self.bot.uptime), 3600)
		m, s = divmod(r, 60)
		d, h = divmod(h, 24)
		embed = self.bot.embed().add_field(name='Uptime', value=f'{d}d {h}h {m}m {s}s')
		return await ctx.send(embed=embed)

	@command(aliases=['sys'])
	async def system(self, ctx):
		"""Information of the system that is running the bot."""
		embed = self.bot.embed(title='System Info').set_thumbnail(url='https://cdn.discordapp.com/attachments/735725378433187901/776524927708692490/data-server.png')
		pr = p.Process()
		info = {
			'System': {
				'Username': pr.as_dict(attrs=["username"])['username'],
				'Host OS': platform.platform(),
				'Uptime': timedelta(seconds=time() - p.boot_time()),
				'Boot time': datetime.fromtimestamp(p.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
			},
			'CPU': {
				'Frequency': f"{p.cpu_freq(percpu=True)[0][0]} MHz",
				'CPU Used': f"{p.cpu_percent(interval=1)}%",
				'Time on CPU': timedelta(seconds=p.cpu_times().system + p.cpu_times().user),
			},
			'Memory': {
				'RAM Used': f"{p.virtual_memory().percent}%",
				'RAM Available': f"{p.virtual_memory().available/(1024**3):,.3f} GB",
				'Disk Used': f"{p.disk_usage('/').percent}%",
				'Disk Free': f"{p.disk_usage('/').free/(1024**3):,.3f} GB",
			}
		}
		for key in info:
			embed.add_field(name=f'**> {key}**', value='\n'.join([f'**{k}:** {v}' for k, v in info[key].items()]), inline=False)
		await ctx.send(embed=embed)

	@command(aliases=['cs'])
	async def codestats(self, ctx):
		"""Code statistic of the bot."""
		ctr: collections.Counter[str] = collections.Counter()
		for ctr['files'], f in enumerate(glob.glob('./**/*.py', recursive=True)):
			with open(f, encoding='UTF-8') as fp:
				for ctr['lines'], line in enumerate(fp, ctr['lines']):
					line = line.lstrip()
					ctr['comments (#)'] += '#' in line
					ctr['classes'] += line.startswith('class')
					ctr['functions (def)'] += line.startswith('def')
					ctr['coroutines (async def)'] += line.startswith('async def')
					ctr['docstrings'] += line.startswith('"""') + line.startswith("'''")
		await ctx.send(embed=self.bot.embed(description='\n'.join(f'**{key.capitalize()}:** {value}' for key, value in ctr.items())))

	@command(aliases=['bi', 'about'])
	async def info(self, ctx):
		"""See some kind of information about me (such as command usage, links etc.)"""
		servers = self.bot.guilds
		embed = self.bot.embed().set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url_as(size=64))
		fields = {
			'General': {
				('Owner', f'{self.bot.dosek}'),
				('Currently in', f'{len(servers)} servers'),
				('Commands working', f'{len(self.bot.commands)}'),
				('Commands usage (last restart)', self.bot.command_usage)
			},
			'Links': {
				('Invite link', f'[Here]({self.bot.invite_url})'),
				('GitHub', f'[Here]({self.bot.github_url})'),
				('Support', f'[Here]({self.bot.support_url})'),
			},
		}
		for key in fields:
			embed.add_field(name=key, value='\n'.join([f'**{name}:** {value}' for name, value in fields[key]]), inline=False)
		await ctx.send(embed=embed)

	@command(aliases=['memberinfo', 'ui', 'mi'])
	@guild_only()
	async def userinfo(self, ctx, member: Optional[discord.Member]):
		"""See some general information about mentioned user."""
		member = member or ctx.author
		embed = self.bot.embed().set_author(name=str(member), icon_url=ctx.guild.icon_url_as(size=64))
		embed.set_thumbnail(url=member.avatar_url)
		fields = [
			('Top role', member.top_role.mention),
			('Boosted server', bool(member.premium_since)),
			('Account created', humanize.naturaldate(member.created_at)),
			('Here since', humanize.naturaldate(member.joined_at))
		]
		embed.description = '\n'.join([f'**{name}:** {value}' for name, value in fields])
		await ctx.send(embed=embed)

	@command(aliases=['guildinfo', 'si', 'gi'])
	@guild_only()
	async def serverinfo(self, ctx):
		"""See some general information about current guild."""
		embed = self.bot.embed().set_author(
			name=ctx.guild.name,
			icon_url=ctx.guild.icon_url_as(size=64),
			url=ctx.guild.icon_url
		)
		embed.set_thumbnail(url=ctx.guild.banner_url_as(size=256))
		fields = [
			('Region', ctx.guild.region),
			('Created', humanize.time.naturaltime(ctx.guild.created_at)),
			('Members', ctx.guild.member_count),
			('Boosts', ctx.guild.premium_subscription_count),
			('Roles', len(ctx.guild.roles)),
			('Text channels', len(ctx.guild.text_channels)),
			('Voice channels', len(ctx.guild.voice_channels)),
			('Categories', len(ctx.guild.categories)),
		]
		embed.description = '\n'.join([f'**{n}:** {v}' for n, v in fields])
		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(Info(bot))