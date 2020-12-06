#!/usr/bin/env python3
import discord
import asyncio

async def send_message_test(messenger):
    await messenger.wait_until_ready()
    await messenger.delay(5)
    await messenger.strawberry_message('hello world')

class StrawberryMessenger(discord.Client):
    def __init__(self):
        super().__init__()
        self.strawberry_general = None

    async def delay(self, time_delay):
        await asyncio.sleep(time_delay)

    async def on_ready(self):
        strawberry_guild = [gld for gld in self.guilds if gld.name == 'StrawberryBotSprings'][0]
        self.strawberry_general = strawberry_guild.text_channels[0]
        print('Reporting on Strawberry Automation')

    async def strawberry_message(self, message):
        print(self.strawberry_general)
        await self.strawberry_general.send(message)

messenger = StrawberryMessenger()
messenger.loop.create_task(send_message_test(messenger))
messenger.run('Nzk4MzE4NTMyMTUyMjYyNjc4.X_zSEg.a60hspVCV2KhEsUyd4fpIHkEOQQ')