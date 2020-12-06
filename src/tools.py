from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
import time
import multiprocessing
import discord
import asyncio

class urls:
    reservations = 'https://www.adventurecentral.com/user/web/m/wfCalendar.aspx?AID=23177&SELDT=6/4/2020&CLUID=63f51fca-9713-4114-b4d4-84a4eb769589'
    checkout = 'https://www.adventurecentral.com/user/web/m/wfSummary.aspx?TCID=17863714&CLUID=63f51fca-9713-4114-b4d4-84a4eb769589'

class StrawberryBot(discord.Client):
    def __init__(self, userCreds, test=False):
        self.userCreds = userCreds
        self.max_reservations = 2
        chrome_options = Options()
        chrome_options.add_argument('--incognito')
        chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.actions = ActionChains(self.driver)
        self.nReservations = userCreds.nReservations
        self.greenObservations = 0
        self.test = test
        self.strawberry_general = None
        super().__init__()

    # _______
    # DISCORD
    async def delay(self, time_delay):
        await asyncio.sleep(time_delay)

    async def on_ready(self):
        strawberry_guild = [gld for gld in self.guilds if gld.name == self.userCreds.discordGuild][0]
        self.strawberry_general = strawberry_guild.text_channels[0]
        print('Reporting on Strawberry Automation')

    def _get_stats(self):
        stats_dict = {
            'User': self.userCreds.email,
            'green time observations': str(self.greenObservations),
            'reservations remaining': str(self.nReservations),
        }
        stats_list = []
        for key, val in stats_dict.items():
            stats_list += [key, ': ', val, '\n']
        return ''.join(stats_list)

    async def on_message(self, message):
        if message.content.lower() == 'status':
            await message.channel.send(self._get_stats())

    async def message(self, text):
        await self.strawberry_general.send(text)

    # ________
    # SELENIUM

    def get_reservation_page(self):
        self.driver.get(urls.reservations)

    async def dismiss_unfortunate_unavailable(self):
        floating_error = self.driver.find_element_by_id('ctl00_leftNav_wcFloatingError1_divFloatingError')
        floating_error_style = floating_error.get_attribute('style')
        if floating_error_style == 'display: block;':
            print('dismissing unavailable banner')
            x_buttons = self.driver.find_elements_by_class_name('fa-times-circle')
            if x_buttons:
                x_button = x_buttons[0]
                x_button.click()
            await self.delay(1)

    def choose_day(self):
        link_day = self.driver.find_element_by_link_text(self.userCreds.day)
        link_day.click()

    async def _select_quantity_dropdown(self, number):
        await self.delay(1)
        print('selecting dropdown quantity')
        dropdown_elements = self.driver.find_elements_by_name('ctl00$leftNav$gvRates$ctl02$ddlQuantity')
        if dropdown_elements:
            dropdown_element = dropdown_elements[0]
            options = dropdown_element.find_elements_by_tag_name('option')
            options[number].click()

    async def time_button_is_green(self):
        time_text = self.userCreds.resTime
        green_buttons = self.driver.find_elements_by_class_name('acCartButtonGreen')
        green_button_texts = [btn.text for btn in green_buttons]
        button_is_green = time_text in green_button_texts
        if button_is_green:
            self.greenObservations += 1
            print(f'{time_text} button is green')
            await self.message(f'{time_text} button is green')
        else: print(f'{time_text} not in green buttons: {green_button_texts}')
        return button_is_green

    async def _choose_if_time(self, time_text):
        await self.delay(1)
        print('choose time if exists')
        link_times = self.driver.find_elements_by_link_text(time_text)
        if link_times:
            link_time = link_times[0]
            link_time.click()

    def _check_for_checkout_button(self):
        time.sleep(1)
        print('checking for checkout button')
        checkout_buttons = self.driver.find_elements_by_id('ctl00_leftNav_btnCheckout')
        button_exists = bool(checkout_buttons)
        return button_exists, checkout_buttons[0] if button_exists else None

    def _single_form(self, id, text):
        user_elem = self.driver.find_element_by_id(id)
        user_elem.send_keys(text)

    async def _fill_out_user_information(self):
        await self.delay(2)
        self._single_form('ctl00_leftNav_txtFirstName', self.userCreds.first_name)
        self._single_form('ctl00_leftNav_txtLastName', self.userCreds.last_name)
        self._single_form('ctl00_leftNav_txtEmail', self.userCreds.email)
        self._single_form('ctl00_leftNav_txtPhone', self.userCreds.phone)

    async def _continue_checkout(self):
        await self.delay(2)
        continue_buttons = self.driver.find_elements_by_id('ctl00_leftNav_btnContinue')
        if continue_buttons:
            continue_button = continue_buttons[0]
            continue_button.click()

    async def _agree_to_terms_and_submit(self, attempt_number):
        check_boxes = self.driver.find_elements_by_class_name('form-check')
        for box in check_boxes:
            box.click()
        print('tried to check boxes')
        await self.delay(2)
        continue_buttons = self.driver.find_elements_by_id('ctl00_leftNav_btnContinue')
        if continue_buttons:
            continue_button = continue_buttons[0]
            self.nReservations -= attempt_number
            await self.message(f'making a reservation for {attempt_number}')
            if not self.test:
                continue_button.click()

    async def _checkout_process(self, checkout_button, attempt_number):
        await self.delay(1)
        checkout_button.click()
        await self._fill_out_user_information()
        await self._continue_checkout()
        await self.delay(10)
        await self._agree_to_terms_and_submit(attempt_number)

    async def try_quantities_of_people(self):
        time_text = self.userCreds.resTime
        attempts = list(range(1, self.max_reservations + 1))
        attempts.reverse()
        if self.nReservations < self.max_reservations:
            attempts = list(range(1, self.nReservations + 1))
            attempts.reverse()
        for attempt_number in attempts:
            print(f'### Trying Number of people {attempt_number}')
            await self.delay(2)
            await self._select_quantity_dropdown(attempt_number)
            await self._choose_if_time(time_text)
            await self.delay(3)
            worked, checkout_button = self._check_for_checkout_button()
            if worked:
                await self._checkout_process(checkout_button, attempt_number)
                break

    def close(self):
        self.driver.close()
