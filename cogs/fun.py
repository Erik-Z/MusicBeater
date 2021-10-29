import discord
from discord.ext import commands
import random


class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='randInt', help='Generates a random number between x and y.')
    async def random(self, ctx, x, y):
        await ctx.send(f"{random.randint(int(x), int(y))}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.send("Missing required arguments")
        else:
            print(error)


def setup(client):
    client.add_cog(Fun(client))
