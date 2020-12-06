#!/usr/bin/env python3

import time
from src.tools import StrawberryBot

short_interval = 2
long_interval = 45

async def getHotspringReservations(strawberrybot):
    try:
        await strawberrybot.delay(4)
        await strawberrybot.message(f'[Started StrawberryBot]\n\tfor {strawberrybot.userCreds.email}\n\t@{strawberrybot.userCreds.resTime}, {strawberrybot.userCreds.day}\n\tfor {strawberrybot.userCreds.nReservations}\n\tgoing for max of {strawberrybot.max_reservations} at a time')
        while strawberrybot.nReservations > 0:
            strawberrybot.get_reservation_page()
            await strawberrybot.delay(4)
            await strawberrybot.dismiss_unfortunate_unavailable()
            strawberrybot.choose_day()
            await strawberrybot.delay(4)
            await strawberrybot.dismiss_unfortunate_unavailable()
            button_is_green = await strawberrybot.time_button_is_green()
            if button_is_green:
                await strawberrybot.try_quantities_of_people()
                await strawberrybot.delay(long_interval)
            else:
                await strawberrybot.delay(short_interval)
    except Exception as e:
        await strawberrybot.message('[StrawberryBot Failed]')
        print(e)
        await getHotspringReservations(
            strawberrybot,
        )
        # raise e
    await strawberrybot.message('[Obtained all Reservations]')
    strawberrybot.close()

async def runBot(strawberrybot):
    await strawberrybot.wait_until_ready()
    await getHotspringReservations(
        strawberrybot,
    )

bot = StrawberryBot(user, test=False)
bot.loop.create_task(runBot(bot))
bot.run(user.discordToken)
