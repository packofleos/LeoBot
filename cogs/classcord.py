import os
import random
import datetime

import discord
from discord.ext import commands, tasks

from .utils.confighandler import CogConfigHandler

GUILD_ID = int(os.environ.get("CLASSCORD_GUILD_ID"))
NOTIFY_CHANNEL = int(os.environ.get('NOTIFY_CHANNEL'))
cog_conf = CogConfigHandler(os.path.join(os.path.dirname(__file__), 'data', 'reminder.json'))

class ClassCord(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._channel = None
        self._class_at = None

        if not cog_conf.jsodata['cancelled']:
            self.class_reminder.start()

    def cog_unload(self):
        self.class_reminder.cancel()

    async def cog_check(self, ctx):
        return ctx.guild and ctx.guild.id == GUILD_ID 

    @tasks.loop(hours=24)
    async def class_reminder(self):
        """The main reminder task."""
        msg = cog_conf.jsodata['messages'] or [f'Reminder for {self._class_at}!']
        await self._channel.send(random.choice(msg))

    @class_reminder.before_loop
    async def _before_class_reminder(self):
        """The method called before class_reminder task loop.
        
        This is reposible for sleeping until the scheduled time before the loop starts.
        """
        await self.bot.wait_until_ready()
        self._channel = self.bot.get_channel(NOTIFY_CHANNEL)

        class_time = cog_conf.jsodata['time']
        try:
            target = datetime.datetime.strptime(class_time, "%H:%M")
        except ValueError:
            self.class_reminder.cancel()
            return await self._channel.send("No time or invalid time was provided. Reminder cancelled.")

        now = datetime.datetime.utcnow()
        class_at = now.replace(hour=target.hour, minute=target.minute, second=0)

        if now > class_at:
            class_at += datetime.timedelta(days=1)

        self._class_at = class_at
        await discord.utils.sleep_until(class_at)

    @commands.group(name='reminder', invoke_without_command=True)
    async def _reminder(self, ctx):
        """Show when is the class reminder."""
        await ctx.send("Reminder @ " + str(self._class_at))

    @_reminder.command(name='start')
    async def reminder_start(self, ctx):
        """Start the class reminder. Normally, the reminder will start automatically.
        
        This is useful in case the reminder was cancelled before.
        """
        try:
            self.class_reminder.start()
        except RuntimeError as exc:
            # the task is already running
            return await ctx.send(exc)

        cog_conf.jsodata['cancelled'] = False
        cog_conf.dump()
        await ctx.message.add_reaction(ctx.bot.OK_EMOJI)

    @_reminder.command(name='cancel')
    async def reminder_cancel(self, ctx):
        """Cancel the reminder."""
        self.class_reminder.cancel()
        cog_conf.jsodata['cancelled'] = True
        self._class_at = None
        cog_conf.dump()
        await ctx.message.add_reaction(ctx.bot.OK_EMOJI)

    @_reminder.command(name='time')
    async def reminder_time(self, ctx, hour: int, minute: int):
        """Set reminder time.

        The time should in 24-hour format and in UTC.
        """ 
        if hour not in range(24) and minute not in range(60):
            return await ctx.send("Hour and minute should be between (0, 23) and (0, 59) respectively.")
        cog_conf.jsodata['time'] = f"{hour}:{minute}"
        cog_conf.dump()
        self.class_reminder.restart()
        await ctx.message.add_reaction(ctx.bot.OK_EMOJI)


def setup(bot):
    bot.add_cog(ClassCord(bot))
