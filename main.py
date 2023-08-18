import asyncio
import atexit
import json
import math
import threading

import datetime
from typing import Union

import discord
from discord import ButtonStyle, ActionRow, utils
from discord.ext import commands
from discord.ui import Button, View

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='?', intents=intents, case_insensitive=True)

emoji = ":dollar:"
emoji2 = ":euro:"

invest_profit = 2  # доход от инвестиций/коллект (в %)

import time

infoColor = discord.Color.blue()
badColor = discord.Color.red()
goodColor = discord.Color.green()

help_channel = 1099041433752715375
country_role = 1100419395655843920
mars_role = 1101938281236680764
moon_role = 1101938199699406888
science_role =1101937514807304402
medicine_role =1101937641051672638
high_violence =1102289740092408009
medium_violence =1101940230203899944
low_violence =1101940369299624097
high_infrastructure =1101935709595648002
medium_infrastructure =1101935620198244474
low_infrastructure =1101935470960721980
no_infrastructure =1126185282102886490
high_tourism =1101936111124762735
medium_tourism =1101936017583374336
low_tourism =1101935895579480215
high_economy =1101935342770204733
medium_economy =1101935271265714396
low_economy =1101935082094215199
no_energy =1124777201506717806
eco_energy =1124777466502860831
coal_energy =1124777699517415474
atom_energy =1124777931097505864
news_channel =1119553428474052669
server_id =1099027980556185612
rich_channel =1116803742034042930
creator_role =1099790203863969942
deputy_role =1100165902646906910
administrator_s_role =1132688941045264495
administrator_role =1100163622379995278
tech_creator_role =1105217702391451658
high_oil =1119615502113837117
medium_oil =1119614481543217283
low_oil =1119614070262353953
high_iron =1119633319064248441
medium_iron =1119633321190760590
low_iron =1119631601056366652
high_tin =1119639308614246573
medium_tin =1119639338490265653
low_tin =1119638360290492516
high_silver =1119641715687571567
medium_silver =1119641669860606073
low_silver =1119641396580728842
high_coal =1119642838121062461
medium_coal =1119642827253624892
low_coal =1119642583816212600
high_gold =1119645111597404180
medium_gold =1119645136381562972
low_gold =1119644911885631609
high_gas =1119648280658325584
medium_gas =1119648512733360259
low_gas =1119648522434773002
high_uranium =1119648792887709777
medium_uranium =1119648924282671164
low_uranium =1119648954028666930
sand =1133083407807680642
sea_water =1100418180133957747
low_lithium = 1133661295976140880
medium_lithium = 1133662088955441182
high_lithium = 1133662360289169429


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        help_channel1 = bot.get_channel(help_channel)
        await ctx.send(embed=discord.Embed(
            description=f'Такой команды не существует (возможно она была введена неправильно), все команды указаны в {help_channel1.mention}',
            color=badColor))


class Item:
    def __init__(self, name, desc, price, role_req):
        self.name = name
        self.desc = desc
        self.price = price
        self.role_req = role_req


async def update(ctx, ctx2, update_happiness: bool, update_GDP: bool):
    role_id = country_role  # государство

    role = utils.get(ctx.guild.roles, id=role_id)

    members = role.members
    message = ""
    message2 = ""
    for member in members:
        user_id = member.id
        happiness_level = await check_user_happiness(user_id)
        message += f"{member.mention}: {happiness_level}\n"

        if user_id in users_GDP:
            message2 += f"{member.mention}: {users_GDP[user_id]:,} {emoji}\n"

    if update_happiness:
        await ctx.send(embed=discord.Embed(title="Обновление счастья населения", description=message, color=infoColor))
    if update_GDP:
        if message2 != "":
            await ctx.purge(limit=2)
            await ctx2.send(embed=discord.Embed(title="Обновление ВВП стран", description=message2, color=infoColor))
        else:
            await ctx2.send(embed=discord.Embed(
                description="Список ВВП стран пуст, скорее всего никто ещё не собирал доход после последего включения бота",
                color=badColor))


# def run_schedule_update():
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(schedule_update())
#
#
# # Запуск цикла schedule_update() в отдельном потоке
# update_thread = threading.Thread(target=run_schedule_update)
# update_thread.start()
#
# isFirstUpdateWas = True
# isFirstUpdateWas2 = True
#
#
async def check_user_happiness(user_id):
    role_happiness = {
        medicine_role: 10,  # мед
        high_violence: -10,  # хай преступность
        medium_violence: -5,  # норм преступнось
        high_infrastructure: 8,  # топ инфра
        medium_infrastructure: 3,  # норм инфра
        no_infrastructure: -5,  # ноу инфры
        high_economy: 10,  # топ эко
        low_economy: -10,  # бэд эко
        no_energy: -5,  # нет энергии
        coal_energy: -10,  # угольная энергия
        eco_energy: 2,  # чистая энергия
        high_tourism: 5  # топ туризм
    }

    happiness = 50
    user = await bot.fetch_user(user_id)
    if user is None:
        return happiness

    guild = bot.get_guild(server_id)  # Замените GUILD_ID на идентификатор вашего сервера
    if guild is None:
        return happiness

    member = guild.get_member(user.id)
    if member is None:
        return happiness

    role_ids = [role.id for role in member.roles]
    for role_name, role_happy in role_happiness.items():
        if role_name in role_ids:
            happiness += role_happy

    user_file_path = f"D:/RP World Bot/Users/{user.id}_wars.txt"
    if os.path.isfile(user_file_path):
        with open(user_file_path, "r") as file:
            lines = file.readlines()
    else:
        lines = []

    if len(lines) > 0:
        happiness -= 20

    return happiness


#
#
async def schedule_update():
    while True:
        current_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))  # Europe/Moscow
        target_time1 = current_time.replace(hour=12, minute=0, second=0, microsecond=0)

        if current_time > target_time1:
            target_time1 += datetime.timedelta(days=1)

        time_diff1 = (target_time1 - current_time).total_seconds()

        await asyncio.sleep(time_diff1)
        await update(bot.get_channel(news_channel), bot.get_channel(rich_channel), True, True)


@bot.event
async def on_ready():
    await schedule_update()


cooldown_time_withDraw = 120 * 60  # Время задано в секундах
cooldown_time = 40 * 60  # Время задано в секундах
cooldown_time_resources = 40 * 60  # Время задано в секундах


@bot.command(name="update-sending")
@commands.has_any_role(administrator_role, administrator_s_role, deputy_role, creator_role)
async def send_happy(ctx, happy: str, GDP: str):
    happy_channel = bot.get_channel(news_channel)
    GDP_channel = bot.get_channel(rich_channel)

    if happy.lower() == "yes" or happy.lower() == "no":
        if GDP.lower() == "yes" or GDP.lower() == "no":
            if happy.lower() == "yes":
                happy = True
            else:
                happy = False
            if GDP.lower() == "yes":
                GDP = True
            else:
                GDP = False
        else:
            await ctx.send(embed=discord.Embed(description="Неверные параметры, допустимы только \"yes\" или \"no\"",
                                               color=badColor))
            return
    else:
        await ctx.send(
            embed=discord.Embed(description="Неверные параметры, допустимы только \"yes\" или \"no\"", color=badColor))
        return

    if happy and GDP:
        await update(happy_channel, GDP_channel, True, True)
        return
    elif happy:
        await update(happy_channel, GDP_channel, True, False)
        return
    elif GDP:
        await update(happy_channel, GDP_channel, False, True)
        return


taxes = {
    "Стройкомплекс": 10000000,
    "Городской комплекс": 2000000,
    "Ферма": 600000,
    "Торговый центр": 3000000,
    "Отель": 1000000,
    "Музей": 2000000,
    "Аквапарк": 5000000,
    "Частный район": 1000000,
    "Многоэтажный Район": 2000000,
    "Аптека": 500000,
    "Офис парк": 35000000,
    "Ректификационная колонна": 5000000,
    "Химический завод": 15000000,
    "Фабрика микроконтроллеров": 50000000,
    "Металлургический комбинат": 10000000,
    "Ятк": 20000000,
    "Нпз": 10000000,
    "Гок": 5000000,
    "Обогатительная центрифуга": 10000000
}


@bot.command(name="taxes-info")
async def taxes_info(ctx):
    title = "Доход от налогов с:"
    description = ""
    for name, number in taxes.items():
        description += f"**{name}**\n{number:,}\n"

    description += "\n Доход с налогов зависит от уровня счастья населения и может изменяться от -70% до +70%"

    await ctx.send(embed=discord.Embed(title=title, description=description, color=infoColor))


user_happiness = {}

# 1124777931097505864: 1000000000,  # атом энергосеть
# 1124777699517415474: 900000000,  # грязная энергосеть
# 1124777466502860831: 400000000,  # чистая энергосеть
# 1124777201506717806: 0,  # ноу энергосеть
# 1101938281236680764: 3000000000,  # марс
# 1101938199699406888: 1600000000,  # луна
# 1101937514807304402: 1000000000,  # наука
# 1101937641051672638: 1000000000,  # медик
# 1102289740092408009: 0,  # плохая преступ
# 1101940230203899944: 200000000,  # средняя преступ
# 1101940369299624097: 800000000,  # топ преступ
# 1101935709595648002: 1200000000,  # топ инфра
# 1101935620198244474: 500000000,  # средняя инфра
# 1101935470960721980: 150000000,  # плохая инфра
# 1101936111124762735: 1200000000,  # топ тур
# 1101936017583374336: 500000000,  # средний тур
# 1101935895579480215: 20000000,  # плохой тур
# 1101935342770204733: 1200000000,  # топ эко
# 1101935271265714396: 200000000,  # средняя эко
# 1101935082094215199: 20000000,  # плохая эко

required_resources = {
    atom_energy: {
        "ТВС": 1
    },
    coal_energy: {
        "Уголь": 10
    },
    science_role: {
        "Стекло": 2
    },
    medicine_role: {
        "Серебро": 5
    },
    medium_infrastructure: {
        "Сталь": 3
    },
    high_infrastructure: {
        "Сталь": 5,
        "Битум": 1
    },
    high_economy: {
        "Пластмассы": 1
    }
}


def check_user_resources(user, role):
    user_id = user.id

    # Получение ресурсов пользователя
    user_resources = get_user_resources(user_id)

    # Проверка наличия всех необходимых ресурсов
    resources_available = True
    if role.id in required_resources:
        for resource, quantity in required_resources[role.id].items():
            if resource not in user_resources or user_resources[resource] < quantity:
                resources_available = False
                break
            else:
                update_user_resources(user_id, resource, -quantity)

    if not resources_available:
        return False
    else:
        return True


users_GDP = {}


@bot.command(name='collect')
async def collect(ctx):
    server = ctx.guild

    user = ctx.author

    # if user.id == 1018486099460505622:
    #     await ctx.send("Джиджа иди нахуй")
    #     return

    user_roles = user.roles

    role_income = {
        atom_energy: 1000000000,  # атом энергосеть
        coal_energy: 900000000,  # грязная энергосеть
        eco_energy: 400000000,  # чистая энергосеть
        no_energy: 0,  # ноу энергосеть
        mars_role: 3000000000,  # марс
        moon_role: 1600000000,  # луна
        science_role: 1000000000,  # наука
        medicine_role: 1000000000,  # медик
        high_violence: 0,  # плохая преступ
        medium_violence: 200000000,  # средняя преступ
        low_violence: 600000000,  # топ преступ
        high_infrastructure: 1200000000,  # топ инфра
        medium_infrastructure: 500000000,  # средняя инфра
        low_infrastructure: 150000000,  # плохая инфра
        no_infrastructure: 0,  # ноу инфра
        high_tourism: 1000000000,  # топ тур
        medium_tourism: 400000000,  # средний тур
        low_tourism: 20000000,  # плохой тур
        high_economy: 1200000000,  # топ эко
        medium_economy: 400000000,  # средняя эко
        low_economy: 20000000,  # плохая эко
        # 1119614070262353953: 100000000,
        # 1119614481543217283: 250000000,
        # 1119615502113837117: 400000000,
        # 1119638360290492516: 120000000,
        # 1119639338490265653: 260000000,
        # 1119639308614246573: 350000000,
        # 1119641396580728842: 140000000,
        # 1119641669860606073: 220000000,
        # 1119641715687571567: 320000000,
        # 1119642583816212600: 90000000,
        # 1119642827253624892: 190000000,
        # 1119642838121062461: 290000000,
        # 1119644911885631609: 180000000,
        # 1119645136381562972: 280000000,
        # 1119645111597404180: 420000000,
        # 1119648522434773002: 100000000,
        # 1119648512733360259: 210000000,
        # 1119648280658325584: 340000000,
        # 1119648954028666930: 160000000,
        # 1119648924282671164: 220000000,
        # 1119648792887709777: 340000000,
        # 1119631601056366652: 110000000,
        # 1119633321190760590: 210000000,
        # 1119633319064248441: 310000000
    }

    user_id = user.id

    role_ids = [role.id for role in user_roles]

    # Проверяем, прошло ли достаточно времени с момента последнего сбора дохода
    current_time = time.time()

    if user.id in cooldowns:
        last_collect_time = cooldowns[user_id]
        time_since_last_collect = current_time - last_collect_time

        if time_since_last_collect < cooldown_time:
            # Вычисляем оставшееся время до следующего сбора дохода
            remaining_time = cooldown_time - time_since_last_collect
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)

            # Отправляем сообщение о временном ограничении
            await ctx.send(embed=discord.Embed(
                description=f"Следующее пополнение бюджета планируется через  {minutes} минут {seconds} секунд.",
                color=badColor))
            return

    user_investments = get_user_investment(user_id)
    user_profit = int(get_user_investment(user_id) * (invest_profit / 100))
    user_inv = get_user_inventory(user_id)

    has_income_roles = False
    has_taxes_income = False

    if user_investments > 0:
        has_income_roles = True
    else:
        for role_id in role_ids:
            if role_id in role_income:
                has_income_roles = True
                break
    for item in user_inv:
        if item in taxes:
            has_income_roles = True
            has_taxes_income = True
            break

    # Если у пользователя нет ни одной роли для сбора дохода, выводим сообщение "Нет ролей для сбора дохода"
    if not has_income_roles:
        await ctx.send(embed=discord.Embed(title="Нет ролей для сбора дохода!", color=badColor))
        return
    else:
        title = "Текущий доход от:"
    # Вычисляем общий доход пользователя на основе его ролей
    total_income = 0

    data = ""

    if user_investments > 0:
        total_income += user_profit
        data += f"Инвестиций в размере {user_investments:,} {emoji}:  {user_profit:,} {emoji}\n"

    if has_taxes_income:
        taxes_income = 0
        for item, quantity in user_inv.items():
            if item in taxes:
                taxes_income += taxes[item] * quantity

        user_happiness[user_id] = await check_user_happiness(user_id)
        happiness_modified = user_happiness[user_id] / 50

        real_income = taxes_income * happiness_modified
        total_income += real_income
        data += f"Налогов: {real_income:,} {emoji}\n"

    for role_id in role_ids:
        if role_id in role_income:
            income = role_income[role_id]
            role = ctx.guild.get_role(role_id)  # Получаем объект роли по идентификатору
            if role is not None:
                role_ping = role.mention
                is_res = check_user_resources(user, role)
                if is_res:
                    total_income += income
                    data += f"Роли {role_ping}: {income:,} {emoji}\n"
                else:
                    data += f"Нет ресурсов, роль {role_ping} не приносит доход\n"

    users_GDP[user_id] = (total_income - user_profit) * 36

    vassal_type, metropolis_id = load_user_autonomy(user.id)
    if vassal_type == "вассал":
        metropolis_profit = total_income * 0.2
        total_income = total_income * 0.8
        data += f"\n Отчисления в пользу метрополии составили {int(metropolis_profit):,}"
        metropolis_id = int(metropolis_id)
        update_user_balance(metropolis_id, metropolis_profit)
    elif vassal_type == "автономия":
        metropolis_profit = total_income * 0.5
        total_income = total_income * 0.5
        data += f"\n Отчисления в пользу метрополии составили {int(metropolis_profit):,}"
        metropolis_id = int(metropolis_id)
        update_user_balance(metropolis_id, metropolis_profit)

    embed = discord.Embed(title=title, description=data, color=infoColor)
    await ctx.send(embed=embed)
    update_user_balance(user.id, total_income)

    cooldowns[user.id] = current_time


@bot.command(name='collect-res')
async def collect_res(ctx):
    server = ctx.guild
    # Получаем пользователя, отправившего команду
    user = ctx.author

    user_roles = user.roles

    role_ResIncome = {
        sand: 250,
        sea_water: 250,
        low_coal: 50,
        medium_coal: 150,
        high_coal: 250,
        low_gas: 50,
        medium_gas: 150,
        high_gas: 250,
        low_gold: 50,
        medium_gold: 150,
        high_gold: 250,
        low_iron: 50,
        medium_iron: 150,
        high_iron: 250,
        low_oil: 50,
        medium_oil: 150,
        high_oil: 250,
        low_silver: 50,
        medium_silver: 150,
        high_silver: 250,
        low_tin: 50,
        medium_tin: 150,
        high_tin: 250,
        low_uranium: 50,
        medium_uranium: 150,
        high_uranium: 250,
        low_lithium: 50,
        medium_lithium: 150,
        high_lithium: 250
    }

    role_ResType = {
        sand: "Песок",
        sea_water: "Морская вода",
        low_oil: "Сырая нефть",
        medium_oil: "Сырая нефть",
        high_oil: "Сырая нефть",
        low_tin: "Свинцовая руда",
        medium_tin: "Свинцовая руда",
        high_tin: "Свинцовая руда",
        low_silver: "Серебряная руда",
        medium_silver: "Серебряная руда",
        high_silver: "Серебряная руда",
        low_coal: "Сырой уголь",
        medium_coal: "Сырой уголь",
        high_coal: "Сырой уголь",
        low_gold: "Золотоносный грунт",
        medium_gold: "Золотоносный грунт",
        high_gold: "Золотоносный грунт",
        low_gas: "Неочищенный природный газ",
        medium_gas: "Неочищенный природный газ",
        high_gas: "Неочищенный природный газ",
        low_uranium: "Урановая руда",
        medium_uranium: "Урановая руда",
        high_uranium: "Урановая руда",
        low_iron: "Железная руда",
        medium_iron: "Железная руда",
        high_iron: "Железная руда",
        low_lithium: "Сырой литий",
        medium_lithium: "Сырой литий",
        high_lithium: "Сырой литий"
    }

    role_ids = [role.id for role in user_roles]

    # Проверяем, прошло ли достаточно времени с момента последнего сбора дохода
    current_timeRes = time.time()

    if user.id in cooldownsRes:
        last_collect_timeRes = cooldownsRes[user.id]
        time_since_last_collectRes = current_timeRes - last_collect_timeRes

        if time_since_last_collectRes < cooldown_time_resources:
            # Вычисляем оставшееся время до следующего сбора дохода
            remaining_timeRes = cooldown_time_resources - time_since_last_collectRes
            minutes = int(remaining_timeRes // 60)
            seconds = int(remaining_timeRes % 60)

            # Отправляем сообщение о временном ограничении
            await ctx.send(embed=discord.Embed(
                description=f"Следующее пополнение складов планируется через  {minutes} минут {seconds} секунд.",
                color=badColor))
            return

    has_income_roles = False

    for role_id in role_ids:
        if role_id in role_ResIncome:
            has_income_roles = True
            break

    # Если у пользователя нет ни одной роли для сбора дохода, выводим сообщение "Нет ролей для сбора дохода"
    if not has_income_roles:
        await ctx.send(embed=discord.Embed(title="Нет ролей для сбора ресурсов!", color=badColor))
        return
    else:
        title = "Текущие поставки от:"

    # Вычисляем общий доход пользователя на основе его ролей

    desc = ""
    for role_id in role_ids:
        if role_id in role_ResIncome:
            number = role_ResIncome[role_id]
            type = role_ResType[role_id]
            update_user_resources(user.id, type, number)

            role = ctx.guild.get_role(role_id)  # Получаем объект роли по идентификатору
            if role is not None:
                role_ping = role.mention
                desc += f"Роли {role_ping}: {number:,} {type}\n"

    await ctx.send(embed=discord.Embed(title=title, description=desc, color=infoColor))

    cooldownsRes[user.id] = current_timeRes


# Словарь для хранения времени последнего сбора дохода для каждого пользователя
cooldowns = {}
cooldownsRes = {}
cooldownsWithDraw = {}


@bot.command(name='set-autonomy')
@commands.has_any_role(administrator_role, administrator_s_role, deputy_role, creator_role)
async def set_autonomy(ctx, user: discord.Member, autonomy_type: str, metropolis: discord.Member):
    # Проверяем правильность введенного типа автономии
    if autonomy_type.lower() not in ["вассал", "автономия"]:
        await ctx.send(
            embed=discord.Embed(description="Неправильно указан тип автономии. Допустимые значения: вассал, автономия.",
                                color=badColor))
        return

    # Сохраняем информацию об автономии пользователя
    save_user_autonomy(user.id, autonomy_type, metropolis.id)

    await ctx.send(
        embed=discord.Embed(description=f"Автономия пользователя *{user.nick}* успешно установлена.", color=goodColor))

    # Отдельная функция для сохранения информации об автономии пользователя в файл


def save_user_autonomy(user_id, autonomy_type, metropolis_id):
    file_path = f"D:/RP World Bot/Users/{user_id}_autonomy.txt"
    with open(file_path, "w") as file:
        file.write(f"{autonomy_type.lower()}: {metropolis_id}")


@bot.command(name='get-autonomy')
@commands.has_any_role(administrator_role, administrator_s_role, deputy_role, creator_role)
async def get_autonomy(ctx, user: discord.Member):
    autonomy_type, metropolis_id = load_user_autonomy(user.id)
    await get_autonomy_work(ctx, user, metropolis_id, autonomy_type)


async def get_autonomy_work(ctx, user: discord.Member, target: int, autonomy_type):
    if autonomy_type:
        metropolis = await bot.fetch_user(target)
        await ctx.send(embed=discord.Embed(
            description=f"У пользователя **{user.nick}** установлена автономия типа: {autonomy_type.capitalize()}. Метрополия: *{metropolis.name}*",
            color=infoColor))
    else:
        await ctx.send(embed=discord.Embed(description=f"У пользователя **{user.nick}** не установлена автономия.",
                                           color=infoColor))


@bot.command(name='remove-autonomy')
@commands.has_any_role(administrator_role, administrator_s_role, deputy_role, creator_role)
async def remove_autonomy(ctx, user: discord.Member):
    # Удаляем информацию об автономии пользователя
    delete_user_autonomy(user.id)

    await ctx.send(
        embed=discord.Embed(description=f"Автономия пользователя **{user.nick}** успешно удалена.", color=goodColor))

    # Отдельная функция для удаления информации об автономии пользователя из файла


# @bot.command(name='convert')
# async def convert(ctx, amount: str):
#     server = ctx.guild
#     # Получаем пользователя, отправившего команду
#     user = ctx.author
#
#     # Получаем текущий баланс пользователя
#     balance = get_user_balance(user.id)
#
#     if amount.lower() == 'all':
#         # Если введено "all", списываем все деньги с баланса отправителя
#         amount = balance
#     else:
#         # Удаляем запятые из строки суммы и преобразуем в число
#         amount = int(amount.replace(',', ''))
#
#     # Проверяем, достаточно ли денег на балансе для конвертации
#     if amount > balance:
#         await ctx.send(embed=discord.Embed(title="У вас недостаточно денег на балансе.", color=badColor))
#         return
#
#     # Вычитаем сумму из баланса пользователя
#     update_user_balance(user.id, -amount)
#
#     amountConverted = amount * 1
#
#     formatted_amount = "{:,}".format(amount)
#     formatted_converted = "{:,}".format(amountConverted)
#
#     user_id = 644813283936829470  # Замените на фактический идентификатор игрока
#     admin1 = await bot.fetch_user(user_id)
#     user_id = 1018486099460505622  # Замените на фактический идентификатор игрока
#     admin2 = await bot.fetch_user(user_id)
#     user_id = 935109820128821299  # Замените на фактический идентификатор игрока
#     admin3 = await bot.fetch_user(user_id)
#
#     # Отправляем сообщение об успешной конвертации
#     await ctx.send(embed=discord.Embed(
#         description=f"Вы (ещё пока не успешно) сконвертировали {formatted_amount} {emoji}. Это {formatted_converted} {emoji2}",
#         color=embedColor))
#     await ctx.send(f" {admin1.mention} {admin2.mention} {admin3.mention}")


@bot.command(name='invest')
async def invest(ctx, amount: str):
    server = ctx.guild
    # Получаем пользователя, отправившего команду
    user = ctx.author

    # Получаем текущий баланс пользователя
    balance = get_user_balance(user.id)

    if amount.lower() == 'all':
        # Если введено "all", списываем все деньги с баланса отправителя
        amount = balance
    else:
        # Удаляем запятые из строки суммы и преобразуем в число
        amount = int(amount.replace(',', ''))

    # Проверяем, достаточно ли денег на балансе для инвестирования
    if amount > balance:
        await ctx.send(embed=discord.Embed(title="У вас недостаточно денег на балансе.", color=badColor))
        return

    formatted_amount = "{:,}".format(amount)

    # Вычитаем сумму из баланса пользователя
    update_user_balance(user.id, -amount)

    # Добавляем сумму на инвестиционный счет пользователя
    update_user_investment(user.id, amount)

    await ctx.send(embed=discord.Embed(description=f"Успешно произведено инвестирование {formatted_amount} {emoji}",
                                       color=goodColor))


last_withdraw_times = {}


@bot.command(name='withdraw')
async def withdraw(ctx, amount: str):
    server = ctx.guild
    # Получаем пользователя, отправившего команду
    user = ctx.author

    if amount.lower() == 'max':
        # Если введено "all", списываем все деньги с баланса отправителя
        amount = get_user_investment(user.id) // 4
    else:
        # Удаляем запятые из строки суммы и преобразуем в число
        amount = int(amount.replace(',', ''))

    # Проверяем, прошло ли достаточно времени с момента последнего снятия половины средств
    current_time = datetime.datetime.now()
    last_withdraw_time = last_withdraw_times.get(user.id)
    if last_withdraw_time is not None:
        time_difference = current_time - last_withdraw_time
        if time_difference.total_seconds() < 10800:  # 7200 секунд = 2 часа
            # Время от последнего снятия половины средств не истекло
            hours = int((7200 - time_difference.total_seconds()) // 60 // 60)
            minutes = int(((7200 - time_difference.total_seconds()) // 60) % 60)
            await ctx.send(embed=discord.Embed(
                description=f"Вы уже снимали средства с инвестиционного счета в течение последних 2 часов, следующее снятие будет доступно через {hours} часов {minutes} минут",
                color=badColor))
            return

    # Проверяем, достаточно ли средств на инвестиционном счете для снятия половины суммы
    user_investments = get_user_investment(user.id)
    if user_investments < amount:
        await ctx.send(embed=discord.Embed(title="У вас недостаточно средств на инвестиционном счете", color=badColor))
        return

    # Проверяем, разрешено ли снятие только половины средств
    if amount > user_investments // 4:
        await ctx.send(embed=discord.Embed(title="Вы можете снять только 25% средств с инвестиционного фонда",
                                           color=badColor))
        return

    # Обновляем баланс и инвестиционный счет пользователя
    update_user_balance(user.id, amount)
    update_user_investment(user.id, -amount)

    # Обновляем время последнего снятия половины средств
    last_withdraw_times[user.id] = current_time

    await ctx.send(embed=discord.Embed(
        description=f"Вы успешно сняли {amount:,} {emoji} с инвестиционного фонда и добавили их на свой баланс",
        color=goodColor))


@bot.command(name='take-item')
@commands.has_any_role(administrator_role, administrator_s_role, deputy_role, creator_role)
async def take_item(ctx, user: discord.Member, item_quantity: str, *item_name: str):
    item_name = " ".join(item_name)
    item_name = item_name.capitalize()

    user_id = user.id

    inv = get_user_inventory(user_id)

    if item_name not in inv:
        needed_items_names = {}
        items = inv
        i = 1
        for item in items:
            if item.find(item_name) != -1:
                needed_items_names[item] = i
                i += 1
        if len(needed_items_names) > 1:
            desc = ""
            for name in needed_items_names:
                desc += f"[{str(needed_items_names[name])}] - {name}\n"
            await ctx.send(embed=discord.Embed(title="Найдено несколько предметов:", description=desc, color=infoColor))
            numbers = []
            for name in needed_items_names:
                numbers.append(str(needed_items_names[name]))
            try:
                response = await bot.wait_for('message', timeout=30, check=lambda
                    message: message.author == ctx.author and message.channel == ctx.channel)

                resp = response.content.lower()
                if resp in numbers:
                    number = resp
                    need_name = ""
                    for name in needed_items_names:
                        if str(needed_items_names[name]) == number:
                            need_name = name
                    item_name = need_name
                else:
                    await ctx.send(embed=discord.Embed(title="Введено неверное число, удаление отменено", color=badColor))
                    return
            except asyncio.TimeoutError:
                await ctx.send(embed=discord.Embed(title="Время вышло, удаление отменено", color=badColor))
                return

        elif len(needed_items_names) == 1:
            for name in needed_items_names:
                item_name = name
        else:
            embed = discord.Embed(title="Предмет не найден", color=badColor)
            await ctx.send(embed=embed)
            return

    item_quantity = int(item_quantity.replace(",", ""))

    # Обновляем инвентарь пользователя
    update_user_inventory(user_id, item_name, -item_quantity)

    # Отправляем сообщение об успешном забирании предметов
    await ctx.send(
        embed=discord.Embed(description=f"У пользователя {user.mention} удалено {item_quantity} {item_name}.",
                            color=goodColor))


@bot.command(name='give-item')
@commands.has_any_role(administrator_role, administrator_s_role, deputy_role, creator_role)
async def give_item(ctx, user: discord.Member, item_quantity: str, *item_name_list: str):



    item_name = " ".join(item_name_list)
    item_name = item_name.capitalize()

    server = ctx.guild

    item_quantity = int(item_quantity.replace(",", ""))

    # Получаем ID пользователя
    user_id = user.id

    # Обновляем инвентарь пользователя
    update_user_inventory(user_id, item_name, item_quantity)

    # Отправляем сообщение об успешной выдаче предметов
    await ctx.send(embed=discord.Embed(description=f"Пользователю {user.mention} выдано {item_quantity} {item_name}.",
                                       color=goodColor))
@give_item.error
async def give_item_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send(
            embed=discord.Embed(title="Недостаточно прав для выполнения этой команды.", color=badColor))

@bot.command(name='give-res')
@commands.has_any_role(administrator_role, administrator_s_role, deputy_role, creator_role)
async def give_resource(ctx, user: discord.Member, resource_quantity: str, *resource_name: str):
    resource_name = " ".join(resource_name)
    resource_name = resource_name.capitalize()

    server = ctx.guild

    resource_quantity = int(resource_quantity.replace(",", ""))

    # Получаем ID пользователя
    user_id = user.id

    # Обновляем ресурсы пользователя
    update_user_resources(user_id, resource_name, resource_quantity)

    # Отправляем сообщение об успешной выдаче ресурсов
    await ctx.send(
        embed=discord.Embed(description=f"Пользователю {user.mention} выдано {resource_quantity} {resource_name}.",
                            color=goodColor))


@bot.command(name='take-res')
@commands.has_any_role(administrator_role, administrator_s_role, deputy_role, creator_role)
async def take_resource(ctx, user: discord.Member, resource_quantity: str, *resource_name: str):
    resource_name = " ".join(resource_name)
    resource_name = resource_name.capitalize()
    user_id = user.id
    inv = get_user_inventory(user_id)

    if resource_name not in inv:
        needed_items_names = {}
        items = inv
        i = 1
        for item in items:
            if item.find(resource_name) != -1:
                needed_items_names[item] = i
                i += 1
        if len(needed_items_names) > 1:
            desc = ""
            for name in needed_items_names:
                desc += f"[{str(needed_items_names[name])}] - {name}\n"
            await ctx.send(embed=discord.Embed(title="Найдено несколько ресурсов:", description=desc, color=infoColor))
            numbers = []
            for name in needed_items_names:
                numbers.append(str(needed_items_names[name]))
            try:
                response = await bot.wait_for('message', timeout=30, check=lambda
                    message: message.author == ctx.author and message.channel == ctx.channel)

                resp = response.content.lower()
                if resp in numbers:
                    number = resp
                    need_name = ""
                    for name in needed_items_names:
                        if str(needed_items_names[name]) == number:
                            need_name = name
                    resource_name = need_name
                else:
                    await ctx.send(embed=discord.Embed(title="Введено неверное число, удаление отменено", color=badColor))
                    return
            except asyncio.TimeoutError:
                await ctx.send(embed=discord.Embed(title="Время вышло, удаление отменено", color=badColor))
                return

        elif len(needed_items_names) == 1:
            for name in needed_items_names:
                resource_name = name
        else:
            embed = discord.Embed(title="Ресурс не найден", color=badColor)
            await ctx.send(embed=embed)
            return

    resource_quantity = int(resource_quantity.replace(",", ""))

    # Обновляем ресурсы пользователя
    update_user_resources(user_id, resource_name, -resource_quantity)

    # Отправляем сообщение об успешном забирании ресурсов
    await ctx.send(
        embed=discord.Embed(description=f"У пользователя {user.mention} удалено {resource_quantity} {resource_name}.",
                            color=goodColor))


@bot.command(name='pay')
async def pay(ctx, recipient: discord.Member, amount: str):
    server = ctx.guild
    # Получаем ID отправителя и получателя
    sender_id = ctx.author.id
    recipient_id = recipient.id

    if amount.lower() == 'all':
        # Если введено "all", списываем все деньги с баланса отправителя
        sender_balance = get_user_balance(sender_id)
        amount = sender_balance
    else:
        # Удаляем запятые из строки суммы и преобразуем в число
        amount = int(amount.replace(',', ''))

        # Проверяем, есть ли у отправителя достаточно денег на балансе
        sender_balance = get_user_balance(sender_id)
        if sender_balance < amount:
            await ctx.send(embed=discord.Embed(title="У вас недостаточно денег на балансе.", color=badColor))
            return

    # Снимаем сумму со счета отправителя
    update_user_balance(sender_id, -amount)

    # Добавляем сумму получателю
    update_user_balance(recipient_id, amount)

    # Отправляем сообщение об успешном переводе
    await ctx.send(embed=discord.Embed(
        description=f"{ctx.author.mention} перевел {amount:,} {emoji} пользователю {recipient.mention}.",
        color=goodColor))


prices = {
    # "Урановая руда": 0,
    # "Неочищенный природный газ": 0,
    # "Золотоносный грунт": 0,
    # "Сырой уголь": 0,
    # "Серебряная руда": 0,
    # "Свинцовая руда": 0,
    # "Железная руда": 0,
    # "Сырая нефть": 0,
    # "Урановый концентрат": 0,
    # "Очищенный природный газ": 0,  для продажи необходимо произвести СПГ
    # "Золотоносный концентрат": 0,
    "Каменный уголь": 20000000,
    # "Серебряный концентрат": 0,
    "Свинец": 35000000,
    "Железо": 25000000,
    "Керосин": 80000000,
    "Бензин": 70000000,
    "Дизельное топливо": 50000000,
    "Мазут": 20000000,
    "Пластмассы": 100000000,
    # "Синтез-газ": 0,
    "Сера": 60000000,
    "Порох": 80000000,
    # "Аммиак": 0,
    "Золото": 50000000,
    "Серебро": 35000000,
    # "Необогащённый уран (<1%)": 0,
    # "Низкообогащённый уран (1-5%)": 0,
    # "Низкообогащённый уран (5-20%)": 0,
    # "Среднеобогащённый уран (20-45%)": 0,
    # "Среднеобогащённый уран (45-70%)": 0,
    # "Высокообогащённый уран (70-90%)": 0,
    "Сталь": 60000000,
    "СПГ": 30000000,
    "Литий-7": 40000000,
    # "Плутоний-239": 0,
    # "Ядерные отходы": 0,
    # "Радиоактивная кашица": 0,
    # "Песок": 0,
    "Стекло": 40000000,
    # "Металлический кремний": 0,
    # "Кремниевая пластина": 0,
    "Микроконтроллеры": 250000000,
    # "Солёная вода": 0,
    # "Литий-6": 0,
    # "Тритий": 0,
    # "Дейтерий": 0,
    "Битум": 70000000,
    # "Высокообогащённый уран (>90%)": 0
}


@bot.command(name="sell-info")
async def sell_information(ctx):
    desc = ""
    for item, price in prices.items():
        desc += f"**{item}**\n{price:,}\n"

    desc += "\nЕсли ресурса нет в этом списке, значит его нельзя продать"

    await ctx.send(
        embed=discord.Embed(title="Продажа ресурсов (цена за 1 единицу на складе):", description=desc, color=infoColor))


@bot.command(name="sell")
async def sell(ctx, amount: str, *resource: str):
    resource = " ".join(resource)
    resource = resource.capitalize()

    if resource not in prices:
        needed_items_names = {}
        items = prices
        i = 1
        for item in items:
            if item.find(resource) != -1:
                needed_items_names[item] = i
                i += 1
        if len(needed_items_names) > 1:
            desc = ""
            for name in needed_items_names:
                desc += f"[{str(needed_items_names[name])}] - {name}\n"
            await ctx.send(embed=discord.Embed(title="Найдено несколько предметов:", description=desc, color=infoColor))
            numbers = []
            for name in needed_items_names:
                numbers.append(str(needed_items_names[name]))
            try:
                response = await bot.wait_for('message', timeout=30, check=lambda
                    message: message.author == ctx.author and message.channel == ctx.channel)

                resp = response.content.lower()
                if resp in numbers:
                    number = resp
                    need_name = ""
                    for name in needed_items_names:
                        if str(needed_items_names[name]) == number:
                            need_name = name
                    resource = need_name
                else:
                    await ctx.send(embed=discord.Embed(title="Введено неверное число, продажа отменена", color=badColor))
                    return
            except asyncio.TimeoutError:
                await ctx.send(embed=discord.Embed(title="Время вышло, продажа отменена", color=badColor))
                return

        elif len(needed_items_names) == 1:
            for name in needed_items_names:
                resource = name
        else:
            embed = discord.Embed(title="Указан неверный ресурс/этот ресурс нельзя продать", color=badColor)
            await ctx.send(embed=embed)
            return

    user = ctx.author

    resources = get_user_resources(user.id)
    if resource in resources:
        amount_all = int(resources[resource])
    else:
        await ctx.send(embed=discord.Embed(title="На складах нет указанного ресурса", color=badColor))
        return

    if amount.lower() == "all":
        amount = amount_all
        total_price = int(prices[resource]) * amount
    else:
        amount = int(amount.replace(",", ""))
        total_price = int(prices[resource]) * int(amount)
        if amount > amount_all:
            await ctx.send(embed=discord.Embed(title="На складах недостаточно указанного ресурса", color=badColor))
            return

    update_user_resources(user.id, resource, -amount)
    update_user_balance(user.id, total_price)

    embed = discord.Embed(
        description=f"Продано {amount} {resource} по цене {total_price:,} {emoji}.",
        color=goodColor)

    await ctx.send(embed=embed)

    # # "Урановая руда": 0, !
    # # "Неочищенный природный газ": 0, !
    # # "Золотоносный грунт": 0, !
    # # "Сырой уголь": 0, !
    # # "Серебряная руда": 0, !
    # # "Свинцовая руда": 0, !
    # # "Железная руда": 0, !
    # # "Сырая нефть": 0, !
    # # "Урановый концентрат": 0, !
    # # "Очищенный природный газ": 0,  для продажи необходимо произвести СПГ !
    # # "Золотоносный концентрат": 0, !
    # "Каменный уголь": 40000000, !
    # # "Серебряный концентрат": 0, !
    # # "Обогащённая свинцовая руда": 0, !
    # # "Обогащённая железная руда": 0, !
    # "Свинец": 70000000, !
    # "Железо": 60000000, !
    # "Керосин": 80000000, !
    # "Бензин": 70000000, !
    # "Дизельное топливо": 60000000, !
    # "Мазут": 44000000, !
    # "Пластмассы": 70000000, !
    # # "Синтез-газ": 0, !
    # "Сера": 80000000, !
    # "Порох": 100000000, !
    # # "Аммиак": 0, !
    # "Золото": 100000000, !
    # "Серебро": 70000000, !
    # # "Необогащённый уран (<1%)": 0, !
    # # "Низкообогащённый уран (1-5%)": 0, !
    # # "Низкообогащённый уран (5-20%)": 0, !
    # # "Среднеобогащённый уран (20-45%)": 0, !
    # # "Среднеобогащённый уран (45-70%)": 0, !
    # # "Высокообогащённый уран (70-90%)": 0, !
    # "Cталь": 90000000, !
    # "CПГ": 70000000, !
    # # "Плутоний-239": 0, !
    # # "Ядерные отходы": 0, !
    # # "Радиоактивная кашица": 0, !
    # # "Песок": 0, !
    # "Стекло": 80000000, !
    # # "Кремниевый песок": 0, !
    # # "Металлический кремний": 0, !
    # # "Кремниевая пластина": 0, !
    # "Микроконтроллеры": 20000000, !
    # # "Морская вода": 0, !
    # # "Литий-6": 0, !
    # # "Литий-7": 0, !
    # # "Сырой литий": 0,
    # # "Тритий": 0,
    # # "Дейтерий": 0,
    # # "Высокообогащённый уран (>90%)": 0
    # # "Ядерное топливо": 0


conversion_rules = {
    "Урановый концентрат": {
        "required_resources": {
            "Урановая руда": 2
        },
        "required_items": {
            "Гок": 2
        },
        "converted_resources": {
            "Урановый концентрат": 1
        }
    },
    "Уран": {
        "required_resources": {
            "Урановый концентрат": 1
        },
        "required_items": {
            "Химический завод": 1
        },
        "converted_resources": {
            "Необогащённый уран (<1%)": 1
        }
    },
    "Обогащение урана 1": {
        "required_resources": {
            "Необогащённый уран (<1%)": 2
        },
        "required_items": {
            "Обогатительная центрифуга": 2
        },
        "converted_resources": {
            "Низкообогащённый уран (1-5%)": 1
        }
    },
    "Обогащение урана 2": {
        "required_resources": {
            "Низкообогащённый уран (1-5%)": 2
        },
        "required_items": {
            "Обогатительная центрифуга": 2
        },
        "converted_resources": {
            "Низкообогащённый уран (5-20%)": 1
        }
    },
    "Обогащение урана 3": {
        "required_resources": {
            "Низкообогащённый уран (5-20%)": 2
        },
        "required_items": {
            "Обогатительная центрифуга": 2
        },
        "converted_resources": {
            "Среднеобогащённый уран (20-45%)": 1
        }
    },
    "Обогащение урана 4": {
        "required_resources": {
            "Среднеобогащённый уран (20-45%)": 2
        },
        "required_items": {
            "Обогатительная центрифуга": 2
        },
        "converted_resources": {
            "Среднеобогащённый уран (45-70%)": 1
        }
    },
    "Обогащение урана 5": {
        "required_resources": {
            "Среднеобогащённый уран (45-70%)": 2
        },
        "required_items": {
            "Обогатительная центрифуга": 2
        },
        "converted_resources": {
            "Высокообогащённый уран (70-90%)": 1
        }
    },
    "Обогащение урана 6": {
        "required_resources": {
            "Высокообогащённый уран (70-90%)": 2
        },
        "required_items": {
            "Обогатительная центрифуга": 2
        },
        "converted_resources": {
            "Высокообогащённый уран (>90%)": 1
        }
    },
    "Твс": {
        "required_resources": {
            "Низкообогащённый уран (1-5%)": 10,
            "Сталь": 5
        },
        "required_items": {
            "Ятк": 1
        },
        "converted_resources": {
            "ТВС": 10
        }
    },
    "Очищенный природный газ": {
        "required_resources": {
            "Неочищенный природный газ": 10
        },
        "required_items": {
            "Химический завод": 1
        },
        "converted_resources": {
            "Очищенный природный газ": 8,
            "Сера": 1
        }
    },
    "Спг": {
        "required_resources": {
            "Очищенный природный газ": 10
        },
        "required_items": {
            "Химический завод": 1
        },
        "converted_resources": {
            "СПГ": 10
        }
    },
    "Золотоносный концентрат": {
        "required_resources": {
            "Золотоносный грунт": 2
        },
        "required_items": {
            "Гок": 2
        },
        "converted_resources": {
            "Золотоносный концентрат": 1
        }
    },
    "Золото": {
        "required_resources": {
            "Золотоносный концентрат": 1
        },
        "required_items": {
            "Металлургический комбинат": 1
        },
        "converted_resources": {
            "Золото": 1
        }
    },
    "Каменный уголь": {
        "required_resources": {
            "Сырой уголь": 1.2
        },
        "required_items": {
            "Гок": 1
        },
        "converted_resources": {
            "Каменный уголь": 1
        }
    },
    "Серебряный концентрат": {
        "required_resources": {
            "Серебряная руда": 2
        },
        "required_items": {
            "Гок": 2
        },
        "converted_resources": {
            "Серебряный концентрат": 1
        }
    },
    "Серебро": {
        "required_resources": {
            "Серебряный концентрат": 1
        },
        "required_items": {
            "Металлургический комбинат": 1
        },
        "converted_resources": {
            "Серебро": 1
        }
    },
    "Обогащённая свинцовая руда": {
        "required_resources": {
            "Свинцовая руда": 2
        },
        "required_items": {
            "Гок": 2
        },
        "converted_resources": {
            "Обогащённая свинцовая руда": 1
        }
    },
    "Свинец": {
        "required_resources": {
            "Обогащённая свинцовая руда": 1
        },
        "required_items": {
            "Металлургический комбинат": 1
        },
        "converted_resources": {
            "Свинец": 1
        }
    },
    "Обогащённая железная руда": {
        "required_resources": {
            "Железная руда": 2
        },
        "required_items": {
            "Гок": 2
        },
        "converted_resources": {
            "Обогащённая железная руда": 1
        }
    },
    "Железо": {
        "required_resources": {
            "Обогащённая железная руда": 1
        },
        "required_items": {
            "Металлургический комбинат": 1
        },
        "converted_resources": {
            "Железо": 1
        }
    },
    "Переработка нефти": {
        "required_resources": {
            "Сырая нефть": 20
        },
        "required_items": {
            "Ректификационная колонна": 20
        },
        "converted_resources": {
            "Пластмассы": 1,
            "Мазут": 7,
            "Дизельное топливо": 5,
            "Бензин": 5,
            "Керосин": 2
        }
    },
    "Битум": {
        "required_resources": {
            "Мазут": 2
        },
        "required_items": {
            "Нпз": 1
        },
        "converted_resources": {
            "Битум": 1
        }
    },
    "Крекинг мазута": {
        "required_resources": {
            "Мазут": 7
        },
        "required_items": {
            "Нпз": 2
        },
        "converted_resources": {
            "Дизельное топливо": 3,
            "Бензин": 2,
            "Керосин": 2
        }
    },
    "Крекинг дизельного топлива": {
        "required_resources": {
            "Дизельное топливо": 5
        },
        "required_items": {
            "Нпз": 2,
        },
        "converted_resources": {
            "Бензин": 3,
            "Керосин": 2
        }
    },
    "Полимеризация": {
        "required_resources": {
            "Дизельное топливо": 5
        },
        "required_items": {
            "Нпз": 1
        },
        "converted_resources": {
            "Пластмассы": 2
        }
    },
    "Синтез-газ": {
        "required_resources": {
            "Мазут": 5
        },
        "required_items": {
            "Химический завод": 2
        },
        "converted_resources": {
            "Синтез-газ": 3
        }
    },
    "Аммиак": {
        "required_resources": {
            "Синтез-газ": 2
        },
        "required_items": {
            "Химический завод": 1
        },
        "converted_resources": {
            "Аммиак": 1
        }
    },
    "Порох": {
        "required_resources": {
            "Каменный уголь": 2,
            "Сера": 2
        },
        "required_items": {
            "Химический завод": 1
        },
        "converted_resources": {
            "Порох": 3
        }
    },
    "Сталь": {
        "required_resources": {
            "Каменный уголь": 1,
            "Железо": 2
        },
        "required_items": {
            "Металлургический комбинат": 1
        },
        "converted_resources": {
            "Сталь": 1
        }
    },
    "Переработка ядерных отходов": {
        "required_resources": {
            "Ядерные отходы": 10
        },
        "required_items": {
            "Ятк": 2,
            "Ядерная программа": 0.00001
        },
        "converted_resources": {
            "Плутоний-239": 1,
            "Радиоактивная кашица": 9
        }
    },
    "Стекло": {
        "required_resources": {
            "Песок": 10,
            "Сера": 1
        },
        "required_items": {
            "Химический завод": 1
        },
        "converted_resources": {
            "Стекло": 10
        }
    },
    "Кремниевый песок": {
        "required_resources": {
            "Песок": 5
        },
        "required_items": {
            "Химический завод": 3
        },
        "converted_resources": {
            "Кремниевый песок": 4
        }
    },
    "Металлический кремний": {
        "required_resources": {
            "Кремниевый песок": 5
        },
        "required_items": {
            "Металлургический комбинат": 2
        },
        "converted_resources": {
            "Металлический кремний": 3
        }
    },
    "Кремниевая пластина": {
        "required_resources": {
            "Металлический кремний": 3
        },
        "required_items": {
            "Фабрика микроконтроллеров": 1
        },
        "converted_resources": {
            "Кремниевая пластина": 1
        }
    },
    "Микроконтроллеры": {
        "required_resources": {
            "Кремниевая пластина": 10,
            "Золото": 6,
            "Пластмассы": 3
        },
        "required_items": {
            "Фабрика микроконтроллеров": 3
        },
        "converted_resources": {
            "Микроконтроллеры": 10
        }
    },
    "Литий": {
        "required_resources": {
            "Сырой литий": 10
        },
        "required_items": {
            "Химический завод": 10
        },
        "converted_resources": {
            "Литий-6": 1,
            "Литий-7": 9
        }
    },
    "Очищенная вода": {
        "required_resources": {
            "Морская вода": 10
        },
        "required_items": {
            "Химический завод": 1
        },
        "converted_resources": {
            "Очищенная вода": 9
        }
    },
    "Дейтерий": {
        "required_resources": {
            "Очищенная вода": 100
        },
        "required_items": {
            "Ректификационная колонна": 20
        },
        "converted_resources": {
            "Дейтерий": 1
        }
    },
    "Тритий": {
        "required_resources": {
            "Литий-6": 10
        },
        "required_items": {
            "Ядерный реактор": 3,
            "Ядерная программа": 0.00001
        },
        "converted_resources": {
            "Тритий": 5
        }
    },
    "Плутоний-239": {
        "required_resources": {
            "Высокообогащённый уран (>90%)": 5
        },
        "required_items": {
            "Ядерный реактор": 1,
            "Ядерная программа": 0.00001
        },
        "converted_resources": {
            "Плутоний-239": 1
        }
    },

    # Добавьте остальные правила конвертации ресурсов
}

# Словарь для отслеживания времени последнего использования предметов в рецептах
last_item_usage = {}


@bot.command(name="refine")
async def refine(ctx, amount: str, *resource: str):
    resource = " ".join(resource)
    resource = resource.capitalize()

    user = ctx.author

    amount = amount.replace(",", "")
    amount = int(amount)

    # Проверяем, если количество меньше 1, выводим сообщение об ошибке
    if amount < 1:
        embed = discord.Embed(
            description="Количество должно быть больше или равно 1.",
            color=badColor
        )
        await ctx.send(embed=embed)
        return

    if resource not in conversion_rules:
        needed_items_names = {}
        items = conversion_rules
        i = 1
        for item in items:
            if item.find(resource) != -1:
                needed_items_names[item] = i
                i += 1
        if len(needed_items_names) > 1:
            desc = ""
            for name in needed_items_names:
                desc += f"[{str(needed_items_names[name])}] - {name}\n"
            await ctx.send(embed=discord.Embed(title="Найдено несколько рецептов:", description=desc, color=infoColor))
            numbers = []
            for name in needed_items_names:
                numbers.append(str(needed_items_names[name]))
            try:
                response = await bot.wait_for('message', timeout=30, check=lambda
                    message: message.author == ctx.author and message.channel == ctx.channel)

                resp = response.content.lower()
                if resp in numbers:
                    number = resp
                    need_name = ""
                    for name in needed_items_names:
                        if str(needed_items_names[name]) == number:
                            need_name = name
                    resource = need_name
                else:
                    await ctx.send(embed=discord.Embed(title="Введено неверное число, рецепт отменён", color=badColor))
                    return
            except asyncio.TimeoutError:
                await ctx.send(embed=discord.Embed(title="Время вышло, рецепт отменён", color=badColor))
                return

        elif len(needed_items_names) == 1:
            for name in needed_items_names:
                resource = name
        else:
            embed = discord.Embed(title="Рецепт не найден", color=badColor)
            await ctx.send(embed=embed)
            return

    # Получаем правила конвертации для указанного ресурса
    conversion_rule = conversion_rules[resource]

    time_to_use = can_use_items(ctx.author.id, conversion_rule["required_items"])
    # Проверяем, если рецепт требует предметы и если ограничение времени прошло
    if "required_items" in conversion_rule and time_to_use != True:
        embed = discord.Embed(
            description=f"Предприятия, необходимые для этого рецепта сейчас заняты, они будут доступны через {int(time_to_use // 60)} минут",
            color=badColor
        )
        await ctx.send(embed=embed)
        return

    # Округляем требуемые ресурсы в большую сторону
    required_resources = {
        resource: math.ceil(quantity * amount) for resource, quantity in conversion_rule["required_resources"].items()
    }

    # Выполняем конвертацию ресурсов
    error_type = perform_conversion_refine(ctx.author.id, conversion_rule, amount)
    # await ctx.send(emed=discord.Embed(title="", color=badColor))
    if error_type != "ok":
        if error_type == "error11":
            await ctx.send(embed=discord.Embed(title="Нет требуемого ресурса(ов)!", color=badColor))
        elif error_type == "error12":
            await ctx.send(embed=discord.Embed(title="Недостаточно требуемого ресурса(ов)!", color=badColor))
        elif error_type == "error21":
            await ctx.send(embed=discord.Embed(title="Нет требуемого предмета(ов)!", color=badColor))
        elif error_type == "error22":
            await ctx.send(embed=discord.Embed(title="Недостаточно требуемого предмета(ов)!", color=badColor))
        elif error_type == "error23":
            await ctx.send(embed=discord.Embed(title="Для выполнения этого рецепта требуется наличие ядерной программы",
                                              color=badColor))
        else:
            await ctx.send(
                embed=discord.Embed(title="Произошла ошибка при попытке переработки ресурса!", color=badColor))
        return

    # Помечаем предметы в рецепте как использованные
    mark_items_used(ctx.author.id, conversion_rule.get("required_items", {}))

    # Отправляем сообщение об успешной конвертации
    embed = discord.Embed(
        description=f"Произведено {amount} {resource}",
        color=goodColor
    )
    await ctx.send(embed=embed)


def has_sufficient_resources(user_id, required_resources, amount):
    user_resources = get_user_resources(user_id)

    for resource, quantity in required_resources.items():
        quantity = math.ceil(quantity)
        if resource not in user_resources or user_resources[resource] < quantity:
            return False

    return True


def perform_conversion_refine(user_id, conversion_rule, amount):
    user_resources = get_user_resources(user_id)
    user_inventory = get_user_inventory(user_id)

    for item, quantity in conversion_rule["required_items"].items():
        quantity = quantity * amount
        quantity = math.ceil(quantity)
        if item not in user_inventory:
            if item == "Ядерная программа":
                return "error23"
            return "error21"
        if user_inventory[item] < quantity:
            return "error22"

    need_to_delete = {}

    for resource, quantity in conversion_rule["required_resources"].items():
        quantity = math.ceil(quantity * amount)
        if resource not in user_resources:
            return "error11"
        if user_resources[resource] < quantity:
            return "error12"
        need_to_delete[resource] = quantity

    for resource in need_to_delete:
        quantity = need_to_delete[resource]
        update_user_resources(user_id, resource, -quantity)

    for resource, quantity in conversion_rule["converted_resources"].items():
        update_user_resources(user_id, resource, quantity * amount)

    return "ok"


def can_use_items(user_id, required_items):
    current_time = time.time()

    for item, _ in required_items.items():
        last_usage_time = last_item_usage.get((user_id, item), 0)

        if current_time - last_usage_time < 30 * 60:
            return (30 * 60) - (current_time - last_usage_time)

    return True


def mark_items_used(user_id, required_items):
    current_time = time.time()

    for item, _ in required_items.items():
        last_item_usage[(user_id, item)] = current_time


@bot.command(name="refine-info")
async def refine_info(ctx):
    recipes = list(conversion_rules.keys())
    total_recipes = len(recipes)
    batch_size = 3  # Размер пачки рецептов

    # Разделение рецептов на пачки
    recipe_batches = [recipes[i:i + batch_size] for i in range(0, total_recipes, batch_size)]

    batches = []

    b = {
        "current_batch": 0
    }


    for batch in recipe_batches:
        # Создаем встроенное сообщение
        embed = discord.Embed(title="Информация о рецептах", color=infoColor)

        # Добавляем информацию о каждом рецепте в пачке
        for recipe in batch:
            recipe_info = conversion_rules[recipe]
            required_resources = recipe_info.get("required_resources", {})
            required_items = recipe_info.get("required_items", {})
            converted_resources = recipe_info.get("converted_resources", {})

            recipe_text = "*Необходимые ресурсы:*\n"
            for resource, amount in required_resources.items():
                recipe_text += f"- {resource}: {amount:,}"

            recipe_text += "\n*Необходимые предметы:*\n"
            for item, amount in required_items.items():
                recipe_text += f"- {item}: {amount:,}"

            recipe_text += "\n*Результат переработки:*\n"
            for resource, amount in converted_resources.items():
                recipe_text += f"- {resource}: {amount:,}\n"


            embed.add_field(name=f"🏭 Рецепт: {recipe}\n", value=recipe_text, inline=False)

        batches.append(embed)

    max_batch = len(batches) - 1

    view = View()

    next_page = Button(label="➡️", style=discord.ButtonStyle.blurple)
    previous_page = Button(label="⬅️", style=discord.ButtonStyle.blurple)

    async def next_call(interaction):
        if b["current_batch"] < max_batch:
            b["current_batch"] += 1
            await message.edit(embed=batches[b["current_batch"]], view = view)
    async def previous_call(interaction):
        if b["current_batch"] > 0:
            b["current_batch"] -= 1
            await message.edit(embed=batches[b["current_batch"]], view=view)

    next_page.callback = next_call
    previous_page.callback = previous_call
    view.add_item(previous_page)
    view.add_item(next_page)

    message = await ctx.send(embed = batches[0], view=view)




@bot.command(name="nuke-ready")
async def nuc_ready(ctx, level: int):
    user = ctx.author
    user_id = str(ctx.author.id)
    user_file_path = f"D:/RP World Bot/Users/{user_id}_nuc_ready.txt"

    inv = get_user_inventory(user_id)
    allow1 = False
    allow2 = False
    for item in ICBM_list:
        if item in inv:
            allow1 = True
    for item in attack_list_info:
        if item in inv:
            allow2 = True
    if not allow1 or not allow2:
        await ctx.send(embed=discord.Embed(
            description="У страны нет сил ядерного сдерживания (для этого необходимо иметь по крайней мере 1 МБР и 1 ядерную (термоядерную) боеголовку)",
            color=badColor))
        return

    # Проверка валидности уровня готовности
    if level < 0 or level > 3:
        await ctx.send(
            embed=discord.Embed(description="Неверный уровень готовности. Уровень должен быть в диапазоне от 0 до 3",
                                color=badColor))
        return

    if os.path.isfile(user_file_path):
        # Чтение файла с уровнем готовности
        with open(user_file_path, "r") as file:
            level_was = file.read()
    else:
        level_was = 0

    if level == level_was:
        await ctx.send(embed=discord.Embed(description="Этот уровень уже установлен", color=badColor))
        return

    wait_time = (5 * level) * 60

    if level > level_was:
        await ctx.send(embed=discord.Embed(
            description=f"Начат процесс повышения уровня готовности, это займёт {int(wait_time // 60)} минут",
            color=infoColor))
        await asyncio.sleep(wait_time)
        channel = news_channel
        title = "Готовность сил ядерного сдерживания"
        if level == 1:
            pict = "D:/RP World Bot/Images/nuc_ready_2.jpg"
            desc = f"{user.mention} повышает готовность своих сил ядерного сдерживания с уровня {level_was} до уровня {level}. Пока что это лишь небольшое предупреждение, но в дальнейшем это может перерасти в большую угрозу"
        elif level == 2:
            pict = "D:/RP World Bot/Images/nuc_ready_2.jpg"
            desc = f"{user.mention} повышает готовность своих сил ядерного сдерживания с уровня {level_was} до уровня {level}. Проводятся проверки и тестирования пусковых шахт, это серьёзно дестабилизирует ситуацию в регионе"
        else:
            pict = "D:/RP World Bot/Images/nuc_ready_1.jpg"
            desc = f"{user.mention} повышает готовность своих сил ядерного сдерживания с уровня {level_was} до уровня {level}. Ракеты нацелены на стратегические цели врагов, а боеголовки заряжены. Ситуация приближается к критической, ядерная кнопка может быть нажата в любой момент"
        await send_message_with_image(channel, title, desc, pict)

    # Обновление файла с уровнем готовности
    with open(user_file_path, "w") as file:
        file.write(str(level))


@bot.command(name="nuke-info")
async def nuc_level(ctx):
    user_id = str(ctx.author.id)
    user_file_path = f"D:/RP World Bot/Users/{user_id}_nuc_ready.txt"

    inv = get_user_inventory(user_id)
    allow1 = False
    allow2 = False
    for item in ICBM_list:
        if item in inv:
            allow1 = True
    for item in attack_list_info:
        if item in inv:
            allow2 = True
    if not allow1 or not allow2:
        await ctx.send(embed=discord.Embed(
            description="У страны нет сил ядерного сдерживания (для этого необходимо иметь по крайней мере 1 МБР и 1 ядерную (термоядерную) боеголовку)",
            color=badColor))
        return

    # Проверка наличия файла с уровнем готовности
    if os.path.isfile(user_file_path):
        # Чтение файла с уровнем готовности
        with open(user_file_path, "r") as file:
            level = file.read()
        await ctx.send(embed=discord.Embed(title=f"Уровень готовности: {level}", color=infoColor))
    else:
        await ctx.send(embed=discord.Embed(title="Уровень готовности: 0", color=infoColor))


import random

arrived_warheads = {}

ICBM_price = {
    "Мбр": 1,
    "Мбр х3": 3,
    "Мбр х6": 6,
    "Мбр х10": 10
}

nuke_damage = {
    "Ядерная боеголовка 30 кт": 1,
    "Ядерная боеголовка 60 кт": 2,
    "Ядерная боеголовка 100 кт": 3,
    "Термоядерная боеголовка 300 кт": 7,
    "Термоядерная боеголовка 1 мт": 15,
    "Термоядерная боеголовка 3 мт": 35
}


@bot.command(name="nuke")
async def nuke(ctx, *targets: discord.Member):
    if len(targets) <= 0:
        await ctx.send(embed=discord.Embed(title="Необходимо указать цели", color=badColor))

    user_id = str(ctx.author.id)
    user_file_path = f"D:/RP World Bot/Users/{user_id}_nuc_ready.txt"

    # Проверка наличия файла готовности ядерных сил пользователя
    if os.path.isfile(user_file_path):
        with open(user_file_path, "r") as file:
            nuc_ready_level = int(file.read().strip())

        # Проверка уровня готовности ядерных сил пользователя
        if nuc_ready_level >= 3:
            author_inventory_path = f"D:/RP World Bot/Users/{user_id}_inventory.txt"

            # Проверка наличия файла инвентаря автора
            if os.path.isfile(author_inventory_path):

                author_data = get_user_inventory(user_id)

                user_file_path_a = f"D:/RP World Bot/Users/{user_id}.json"

                if os.path.isfile(user_file_path_a):
                    with open(user_file_path_a, "r") as file:
                        attack_list_user = json.load(file)
                else:
                    await ctx.send(embed=discord.Embed(description="Нет списка атаки"))
                    return

                simple_list = {}
                for name in attack_list_user["attacks"]:
                    simple_list[name["item"]] = name["quantity"]

                for item, quantity in simple_list.items():
                    if item in author_data:
                        if author_data[item] >= quantity:
                            continue
                        else:
                            await ctx.send(
                                embed=discord.Embed(description="Нет нужного количества предметов из списка атаки",
                                                    color=badColor))
                            return
                    else:
                        await ctx.send(
                            embed=discord.Embed(description="Нет всех предметов из списка готовности",
                                                color=badColor))
                        return

                        # Проверка наличия всех предметов из списка готовности автора

                will_use = {}

                need_ICBM = 0
                have_ICBM = 0

                for _, quantity in simple_list.items():
                    need_ICBM += quantity

                for item, quantity in author_data.items():
                    if need_ICBM > have_ICBM:
                        if item in ICBM_price:
                            if have_ICBM + ICBM_price[item] * quantity > need_ICBM:
                                ok = 0
                                for yea in range(quantity):
                                    ok += 1
                                    if have_ICBM + ICBM_price[item] * ok < need_ICBM:
                                        continue
                                    else:
                                        break
                                will_use[item] = ok
                                have_ICBM += need_ICBM - have_ICBM
                            else:
                                have_ICBM += ICBM_price[item]
                                will_use[item] = quantity

                if need_ICBM > have_ICBM:
                    await ctx.send(
                        embed=discord.Embed(description="Недостаточно МБР для доставки боеголовок", color=badColor))
                    return

                keys = {
                    "firstKey": False,
                    "secondKey": False
                }

                async def cancel_call(interaction):
                    await interaction.response.send_message(
                        embed=discord.Embed(title="Запуск ракет отменён", color=goodColor))
                    return

                button_cancel = Button(label="Cancel", style=discord.ButtonStyle.blurple)
                button_cancel.callback = cancel_call

                view = View()
                button1 = Button(emoji="🔑", style=discord.ButtonStyle.gray)

                async def button1_call(interaction):
                    keys["firstKey"] = True
                    await interaction.response.send_message(
                        embed=discord.Embed(title="Ключ 1 повёрнут", color=goodColor))

                button2 = Button(emoji="🔑", style=discord.ButtonStyle.gray)

                async def button2_call(interaction):
                    keys["secondKey"] = True
                    await interaction.response.send_message(
                        embed=discord.Embed(title="Ключ 2 повёрнут", color=goodColor))

                button1.callback = button1_call
                button2.callback = button2_call

                view.add_item(button1)
                view.add_item(button2)
                view.add_item(button_cancel)
                await ctx.send(embed=discord.Embed(title="Поверните оба ключа", color=infoColor), view=view)

                while not keys["firstKey"] or not keys["secondKey"]:
                    await asyncio.sleep(3)

                view2 = View()

                button3 = Button(emoji="🔴", style=discord.ButtonStyle.danger)

                list = {
                    "boom": False
                }

                async def button3_call(interaction):
                    list["boom"] = True
                    await interaction.response.send_message(
                        embed=discord.Embed(title="Ракеты запущены.", color=goodColor))

                button3.callback = button3_call

                view2.add_item(button3)
                view2.add_item(button_cancel)

                await ctx.send(
                    embed=discord.Embed(description="Всё уже готово, осталось лишь нажать на большую красную кнопку...",
                                        color=infoColor), view=view2)

                while not list["boom"]:
                    await asyncio.sleep(3)

                for name, number in will_use.items():
                    update_user_inventory(ctx.author.id, name, -number)

                for name, number in simple_list.items():
                    update_user_inventory(ctx.author.id, name, -number)

                arrived_warheads = simple_list.copy()

                # Отправка сообщения с изображением
                channel_id = news_channel  # Замените на нужный вам ID канала
                title = "Запуск ракет"
                message = f"{ctx.author.mention} запустил свои ракеты с ядерными боеголовками в воздух, предположительные цели: {', '.join([target.mention for target in targets])}"
                image_path = "D:/RP World Bot/Images/rockets_start.png"  # Замените на нужный вам путь к изображению

                await send_message_with_image(channel_id, title, message, image_path)

                await asyncio.sleep(60)

                for target in targets:
                    target_user_id = str(target.id)
                    target_inventory_path = f"D:/RP World Bot/Users/{target_user_id}_inventory.txt"

                    # Проверка наличия файла инвентаря целевого пользователя
                    if os.path.isfile(target_inventory_path):

                        target_data = get_user_inventory(target_user_id)

                        if "Про" in target_data:

                            if "Згрлс" in target_data:
                                AMD_eff = target_data["Згрлс"] * 2 + 50
                            else:
                                AMD_eff = 50

                            channel_id = news_channel
                            title = "Работа Про"
                            message = f"Про {target.mention} начало отрабатывать по вражеским ракетам"
                            image_path = "D:/RP World Bot/Images/ARD.jpg"

                            await send_message_with_image(channel_id, title, message, image_path)

                            keys = []

                            for key, _ in arrived_warheads.items():
                                keys.append(key)

                            number = len(keys) - 1

                            for i in range(target_data["Про"]):
                                if random.randint(1, 100) > AMD_eff:
                                    if number >= 0:
                                        arrived_warheads[keys[number]] -= 1
                                        if arrived_warheads[keys[number]] <= 0:
                                            del arrived_warheads[keys[number]]
                                            number -= 1

                await asyncio.sleep(20)

                items = arrived_warheads.items()

                if len(items) > 0:
                    text = "Всего до цели добрались:"

                    for name, number in arrived_warheads.items():
                        text += f"\n{name}: {number}"
                    text += ".\n"

                    sum_damage = 0
                    for warhead, quantity in arrived_warheads.items():
                        sum_damage += nuke_damage[warhead] * quantity

                    destroyed = {}

                    reserve = {}
                    shield = 0
                    last_target_id = 0
                    turn_off = False
                    while not turn_off:
                        if sum_damage <= 0:
                            turn_off = True
                        for target in targets:
                            target_id_2 = target.id
                            t_inv = get_user_inventory(target_id_2)
                            if last_target_id != 0:
                                for item, quantity in reserve.items():
                                    update_user_inventory(last_target_id, item, quantity)
                            if len(t_inv) > 0:
                                shield = 0
                                ran1 = []
                                ran = t_inv
                                for i in ran:
                                    ran1.append(i)
                                item = random.choice(ran1)
                                quantity = 1
                                if item in ICBM_price and sum_damage > 0 or item in nuke_damage and sum_damage > 0 or item == "Ядерная программа" and sum_damage > 0:
                                    reserve[item] = quantity
                                    update_user_inventory(target_id_2, item, -quantity)
                                    continue
                                if sum_damage >= quantity:
                                    update_user_inventory(target_id_2, item, -quantity)
                                    sum_damage -= quantity
                                    if target_id_2 not in destroyed:
                                        destroyed[target_id_2] = {}
                                    this_person = destroyed[target_id_2]
                                    if item not in this_person:
                                        this_person[item] = quantity
                                    else:
                                        this_person[item] = this_person[item] + quantity
                                elif quantity > sum_damage > 0:
                                    update_user_inventory(target_id_2, item, -sum_damage)
                                    sum_damage = 0
                                    if target_id_2 not in destroyed:
                                        destroyed[target_id_2] = {}
                                    this_person = destroyed[target_id_2]
                                    if item not in this_person:
                                        this_person[item] = sum_damage
                                    else:
                                        this_person[item] = this_person[item] + sum_damage
                                    turn_off = True
                            else:
                                shield += 1
                            if shield >= len(targets):
                                turn_off = True
                                break
                            last_target_id = target.id
                    text += "Уничтожено:"
                    for ids in destroyed:
                        blud = await bot.fetch_user(ids)
                        text += f"\n{blud.mention}:"
                        blud_rule = destroyed[ids]
                        for item, quantity in blud_rule.items():
                            text += f"\n{item}: {quantity:,}"

                    image_path = "D:/RP World Bot/Images/boom.png"


                else:
                    text = "ПРО успешно отразило все вражеские удары"
                    image_path = "D:/RP World Bot/Images/ARD_succes.jpg"

                title = "Результаты ядерной атаки"
                channel = news_channel
                await send_message_with_image(channel, title, text, image_path)

            else:
                await ctx.send(embed=discord.Embed(description="В инвентаре нет всех предметов из списка готовности",
                                                   color=badColor))
        else:
            await ctx.send(
                embed=discord.Embed(description="Недостаточный уровень готовности ядерных сил", color=badColor))
    else:
        await ctx.send("Недостаточный уровень готовности ядерных сил")


ICBM_list = {"Мбр", "Мбр х3", "Мбр х6", "Мбр х10"}
attack_list_info = {"Термоядерная боеголовка 3 мт", "Термоядерная боеголовка 1 мт", "Термоядерная боеголовка 300 кт",
                    "Ядерная боеголовка 100 кт", "Ядерная боеголовка 60 кт", "Ядерная боеголовка 30 кт"}


@bot.command(name="add-attack")
async def add_attack(ctx, quantity: int, *item_name: str):
    item_name = " ".join(item_name)
    item_name = item_name.capitalize()

    inv = get_user_inventory(ctx.author.id)

    if item_name not in inv:
        needed_items_names = {}
        items = inv
        i = 1
        for item in items:
            if item.find(item_name) != -1:
                needed_items_names[item] = i
                i += 1
        if len(needed_items_names) > 1:
            desc = ""
            for name in needed_items_names:
                desc += f"[{str(needed_items_names[name])}] - {name}\n"
            await ctx.send(embed=discord.Embed(title="Найдено несколько предметов:", description=desc, color=infoColor))
            numbers = []
            for name in needed_items_names:
                numbers.append(str(needed_items_names[name]))
            try:
                response = await bot.wait_for('message', timeout=30, check=lambda
                    message: message.author == ctx.author and message.channel == ctx.channel)

                resp = response.content.lower()
                if resp in numbers:
                    number = resp
                    need_name = ""
                    for name in needed_items_names:
                        if str(needed_items_names[name]) == number:
                            need_name = name
                    item_name = need_name
                else:
                    await ctx.send(embed=discord.Embed(title="Введено неверное число, команда отменена", color=badColor))
                    return
            except asyncio.TimeoutError:
                await ctx.send(embed=discord.Embed(title="Время вышло, команда отменена", color=badColor))
                return

        elif len(needed_items_names) == 1:
            for name in needed_items_names:
                item_name = name
        else:
            embed = discord.Embed(title="Предмет не найден", color=badColor)
            await ctx.send(embed=embed)
            return

    # Проверка наличия предмета в словаре attack-list
    if item_name in attack_list_info:
        user_id = str(ctx.author.id)
        user_file_path = f"D:/RP World Bot/Users/{user_id}.json"

        # Проверка наличия файла пользователя
        if os.path.isfile(user_file_path):
            # Загрузка данных пользователя из файла
            with open(user_file_path, "r") as file:
                user_data = json.load(file)
        else:
            # Создание нового объекта данных пользователя
            user_data = {
                "attacks": []
            }

        # Добавление предмета в список атаки игрока
        attack_data = {
            "item": item_name,
            "quantity": quantity,
        }
        user_data["attacks"].append(attack_data)

        # Сохранение данных пользователя в файл
        with open(user_file_path, "w") as file:
            json.dump(user_data, file)

        # Создание и отправка embed-сообщения с информацией о добавленном предмете
        embed = discord.Embed(title="Добавление предмета в список атаки",
                              description=f"{item_name} успешно добавлен в список атаки.",
                              color=discord.Color.green())
        embed.add_field(name="Количество", value=quantity, inline=True)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"{item_name} невозможно добавить в список атаки")


@bot.command(name="remove-attack")
async def remove_attack(ctx, quantity: int, *item_name: str):
    item_name = " ".join(item_name)

    if item_name not in attack_list_info:
        needed_items_names = {}
        items = attack_list_info
        i = 1
        for item in items:
            if item.find(item_name) != -1:
                needed_items_names[item] = i
                i += 1
        if len(needed_items_names) > 1:
            desc = ""
            for name in needed_items_names:
                desc += f"[{str(needed_items_names[name])}] - {name}\n"
            await ctx.send(embed=discord.Embed(title="Найдено несколько предметов:", description=desc, color=infoColor))
            numbers = []
            for name in needed_items_names:
                numbers.append(str(needed_items_names[name]))
            try:
                response = await bot.wait_for('message', timeout=30, check=lambda
                    message: message.author == ctx.author and message.channel == ctx.channel)

                resp = response.content.lower()
                if resp in numbers:
                    number = resp
                    need_name = ""
                    for name in needed_items_names:
                        if str(needed_items_names[name]) == number:
                            need_name = name
                    item_name = need_name
                else:
                    await ctx.send(
                        embed=discord.Embed(title="Введено неверное число, команда отменена", color=badColor))
                    return
            except asyncio.TimeoutError:
                await ctx.send(embed=discord.Embed(title="Время вышло, команда отменена", color=badColor))
                return

        elif len(needed_items_names) == 1:
            for name in needed_items_names:
                item_name = name
        else:
            embed = discord.Embed(title="Предмет не найден", color=badColor)
            await ctx.send(embed=embed)
            return

    user_id = str(ctx.author.id)
    user_file_path = f"D:/RP World Bot/Users/{user_id}.json"

    # Проверка наличия файла пользователя
    if os.path.isfile(user_file_path):
        # Загрузка данных пользователя из файла
        with open(user_file_path, "r") as file:
            user_data = json.load(file)

        # Проверка наличия предмета в списке атаки пользователя
        attacks = user_data.get("attacks", [])
        for attack in attacks:
            if attack["item"] == item_name:
                if attack["quantity"] <= quantity:
                    quantity = attack["quantity"]

                attack["quantity"] -= quantity

                if attack["quantity"] <= 0:
                    attacks.remove(attack)

                break

        # Сохранение обновленных данных пользователя в файл
        with open(user_file_path, "w") as file:
            json.dump(user_data, file)

        # Создание и отправка embed-сообщения об успешном удалении предмета
        embed = discord.Embed(
            description=f"Успешно удалено {quantity} {item_name} из списка атаки.",
            color=discord.Color.green())
        await ctx.send(embed=embed)
    else:
        await ctx.send("Нет списка атаки")


@bot.command(name="attack-info")
async def attack_list(ctx):
    user_id = str(ctx.author.id)
    user_file_path = f"D:/RP World Bot/Users/{user_id}.json"

    # Проверка наличия файла пользователя
    if os.path.isfile(user_file_path):
        # Загрузка данных пользователя из файла
        with open(user_file_path, "r") as file:
            user_data = json.load(file)

        # Получение списка атаки пользователя
        attacks = user_data.get("attacks", [])

        # Проверка наличия предметов в списке атаки
        if attacks:
            # Создание embed-сообщения с информацией о списке атаки
            embed = discord.Embed(title="Список атаки", color=discord.Color.blue())

            for attack in attacks:
                item_name = attack["item"]
                quantity = attack["quantity"]

                embed.add_field(name=item_name, value=f"Количество: {quantity}", inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=discord.Embed(title="Список атаки пуст", color=infoColor))
    else:
        await ctx.send(embed=discord.Embed(title="Список атаки пуст", color=infoColor))


async def send_message_with_image(channel_id, title, message, image_path):
    channel = bot.get_channel(channel_id)  # Получаем объект канала по ID
    if not channel:
        print(f"Канал с ID {channel_id} не найден.")
        return

    try:
        with open(image_path, "rb") as file:
            image = discord.File(file)
            embed = discord.Embed(title=title, description=message, color=infoColor)
            embed.set_image(url="attachment://image.png")
            await channel.send(embed=embed, file=image)
    except FileNotFoundError:
        print(f"Файл с изображением {image_path} не найден.")
    except discord.Forbidden:
        print("У бота нет прав на отправку сообщений в указанный канал.")


@bot.command(name="build-info")
async def build_info(ctx):
    builds = list(build_rules.keys())
    total_builds = len(builds)
    batch_size = 5  # Размер пачки рецептов

    batches = []

    c = {
        "current_batch": 0
    }

    # Разделение рецептов на пачки
    build_batches = [builds[i:i + batch_size] for i in range(0, total_builds, batch_size)]

    for batch in build_batches:
        # Создаем встроенное сообщение
        embed = discord.Embed(title="Информация о постройках", color=infoColor)

        # Добавляем информацию о каждой постройке в пачке
        for build in batch:
            build_info = build_rules[build]
            required_resources = build_info.get("required_resources", {})
            price = build_info.get("price", 0)
            build_time = build_info.get("build_time", 0)

            build_text = "*Необходимые ресурсы:*"
            for resource, amount in required_resources.items():
                build_text += f"\n- {resource}: {amount:,}"

            build_text += f"\n*Цена:* {price:,}"
            build_text += f"\n*Время постройки:* {build_time} *минут*"

            embed.add_field(name=f"🏗️ Постройка: {build}", value=build_text, inline=False)

        batches.append(embed)

    max_batch = len(batches) - 1

    view = View()

    next_page = Button(label="➡️", style=discord.ButtonStyle.blurple)
    previous_page = Button(label="⬅️", style=discord.ButtonStyle.blurple)

    async def next_call(interaction):
        if c["current_batch"] < max_batch:
            c["current_batch"] += 1
            await message.edit(embed=batches[c["current_batch"]], view = view)
    async def previous_call(interaction):
        if c["current_batch"] > 0:
            c["current_batch"] -= 1
            await message.edit(embed=batches[c["current_batch"]], view=view)

    next_page.callback = next_call
    previous_page.callback = previous_call
    view.add_item(previous_page)
    view.add_item(next_page)

    message = await ctx.send(embed = batches[0], view=view)


build_rules = {
    "Стройкомплекс": {
        "required_resources": {},
        "price": 200000000,
        "build_time": 60,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Городской комплекс": {
        "required_resources": {},
        "price": 100000000,
        "build_time": 25,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Ферма": {
        "required_resources": {},
        "price": 30000000,
        "build_time": 40,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Торговый центр": {
        "required_resources": {},
        "price": 50000000,
        "build_time": 30,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Отель": {
        "required_resources": {},
        "price": 25000000,
        "build_time": 20,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Музей": {
        "required_resources": {},
        "price": 60000000,
        "build_time": 30,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Аквапарк": {
        "required_resources": {},
        "price": 20000000,
        "build_time": 10,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Аэропорт": {
        "required_resources": {},
        "price": 200000000,
        "build_time": 60,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Частный район": {
        "required_resources": {},
        "price": 20000000,
        "build_time": 10,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Многоэтажный Район": {
        "required_resources": {},
        "price": 60000000,
        "build_time": 20,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Дорога": {
        "required_resources": {},
        "price": 5000000,
        "build_time": 5,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Железная дорога": {
        "required_resources": {},
        "price": 15000000,
        "build_time": 15,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Полицейский участок": {
        "required_resources": {},
        "price": 30000000,
        "build_time": 20,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Тюрьма": {
        "required_resources": {},
        "price": 100000000,
        "build_time": 60,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Лаборатория": {
        "required_resources": {},
        "price": 300000000,
        "build_time": 60,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Ботанический сад": {
        "required_resources": {},
        "price": 300000000,
        "build_time": 40,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Больница": {
        "required_resources": {},
        "price": 200000000,
        "build_time": 60,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Аптека": {
        "required_resources": {},
        "price": 10000000,
        "build_time": 10,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Космодром": {
        "required_resources": {},
        "price": 5000000000,
        "build_time": 120,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Космическая ракета": {
        "required_resources": {
            "Сталь": 500,
            "Керосин": 100,
            "Микроконтроллеры": 30
        },
        "price": 1500000000,
        "build_time": 60,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Спутник": {
        "required_resources": {
            "Сталь": 100,
            "Микроконтроллеры": 60
        },
        "price": 1000000000,
        "build_time": 30,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Луноход": {
        "required_resources": {
            "Железо": 200,
            "Литий-7": 50,
            "Микроконтроллеры": 50
        },
        "price": 1500000000,
        "build_time": 60,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Марсоход": {
        "required_resources": {
            "Железо": 300,
            "Литий-7": 100,
            "Микроконтроллеры": 100
        },
        "price": 2000000000,
        "build_time": 80,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Офис парк": {
        "required_resources": {},
        "price": 500000000,
        "build_time": 40,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Ядерный реактор": {
        "required_resources": {},
        "price": 5000000000,
        "build_time": 180,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Ректификационная колонна": {
        "required_resources": {},
        "price": 300000000,
        "build_time": 30,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Химический завод": {
        "required_resources": {},
        "price": 1000000000,
        "build_time": 30,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Фабрика микроконтроллеров": {
        "required_resources": {},
        "price": 10000000000,
        "build_time": 180,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Металлургический комбинат": {
        "required_resources": {},
        "price": 600000000,
        "build_time": 30,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Ятк": {
        "required_resources": {},
        "price": 3000000000,
        "build_time": 120,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Нпз": {
        "required_resources": {},
        "price": 1000000000,
        "build_time": 40,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Гок": {
        "required_resources": {},
        "price": 500000000,
        "build_time": 30,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Обогатительная центрифуга": {
        "required_resources": {},
        "price": 2000000000,
        "build_time": 60,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Солнечная батарея": {
        "required_resources": {},
        "price": 20000000,
        "build_time": 10,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Ветряная электростанция": {
        "required_resources": {},
        "price": 50000000,
        "build_time": 20,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Гэс": {
        "required_resources": {},
        "price": 250000000,
        "build_time": 40,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Тэс": {
        "required_resources": {},
        "price": 200000000,
        "build_time": 20,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Аэс": {
        "required_resources": {},
        "price": 2000000000,
        "build_time": 60,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Мбр": {
        "required_resources": {
            "Сталь": 20,
            "Керосин": 20,
            "Микроконтроллеры": 5
        },
        "price": 300000000,
        "build_time": 20,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Мбр х3": {
        "required_resources": {
            "Сталь": 30,
            "Керосин": 30,
            "Микроконтроллеры": 10
        },
        "price": 1000000000,
        "build_time": 25,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Мбр х6": {
        "required_resources": {
            "Сталь": 50,
            "Керосин": 50,
            "Микроконтроллеры": 20
        },
        "price": 1600000000,
        "build_time": 30,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Мбр х10": {
        "required_resources": {
            "Сталь": 70,
            "Керосин": 70,
            "Микроконтроллеры": 35
        },
        "price": 2000000000,
        "build_time": 30,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Ядерная боеголовка 30 кт": {
        "required_resources": {
            "Высокообогащённый уран (>90%)": 4,
            "Плутоний-239": 2
        },
        "price": 600000000,
        "build_time": 15,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Ядерная боеголовка 60 кт": {
        "required_resources": {
            "Высокообогащённый уран (>90%)": 8,
            "Плутоний-239": 4
        },
        "price": 1000000000,
        "build_time": 15,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Ядерная боеголовка 100 кт": {
        "required_resources": {
            "Высокообогащённый уран (>90%)": 10,
            "Плутоний-239": 5
        },
        "price": 1500000000,
        "build_time": 15,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Термоядерная боеголовка 300 кт": {
        "required_resources": {
            "Высокообогащённый уран (>90%)": 2,
            "Плутоний-239": 1,
            "Дейтерий": 4,
            "Тритий": 4,
            "Литий-6": 3
        },
        "price": 2500000000,
        "build_time": 30,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Термоядерная боеголовка 1 мт": {
        "required_resources": {
            "Высокообогащённый уран (>90%)": 5,
            "Плутоний-239": 3,
            "Дейтерий": 10,
            "Тритий": 10,
            "Литий-6": 6
        },
        "price": 5000000000,
        "build_time": 30,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Термоядерная боеголовка 3 мт": {
        "required_resources": {
            "Высокообогащённый уран (>90%)": 15,
            "Плутоний-239": 9,
            "Дейтерий": 30,
            "Тритий": 30,
            "Литий-6": 18
        },
        "price": 10000000000,
        "build_time": 30,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Ядерная программа": {
        "required_resources": {
            "Высокообогащённый уран (>90%)": 50
        },
        "price": 50000000000,
        "build_time": 300,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Про": {
        "required_resources": {
            "Микроконтроллеры": 25,
            "Свинец": 30,
            "Сталь": 50,
            "Порох": 10
        },
        "price": 3000000000,
        "build_time": 60,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Згрлс": {
        "required_resources": {
            "Микроконтроллеры": 100,
            "Свинец": 100,
            "Сталь": 50,
        },
        "price": 8000000000,
        "build_time": 100,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Штаб гру": {
        "required_resources": {},
        "price": 800000000,
        "build_time": 40,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Шахта": {
        "required_resources": {},
        "price": 400000000,
        "build_time": 30,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Рудообрабатывающее предприятие": {
        "required_resources": {},
        "price": 200000000,
        "build_time": 20,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    "Химическое оружие": {
        "required_resources": {
            "Аммиак": 20,
            "Сера": 5
        },
        "price": 50000000,
        "build_time": 15,
        "required_item": "Стройкомплекс",
        "items_required": 1
    },
    # "Военный завод": {
    #     "required_resources": {},
    #     "price": 300000000,
    #     "build_time": 30,
    #     "required_item": "Стройкомплекс",
    #     "items_required": 1
    # },
    # "Пп мина": {
    #     "required_resources": {
    #         "Порох": 0.1
    #     },
    #     "price": 100000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 0.001
    # },
    # "Пт мина": {
    #     "required_resources": {
    #         "Порох": 0.2
    #     },
    #     "price": 300000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 0.001
    # },
    # "Морская мина": {
    #     "required_resources": {
    #         "Порох": 0.5
    #     },
    #     "price": 1000000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 0.001
    # },
    # "Винтовка": {
    #     "required_resources": {
    #     },
    #     "price": 10000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 0.01
    # },
    # "Снайперская винтовка": {
    #     "required_resources": {
    #     },
    #     "price": 100000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 0.01
    # },
    # "Автомат": {
    #     "required_resources": {
    #     },
    #     "price": 50000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 0.01
    # },
    # "Пп гранатомёт": {
    #     "required_resources": {
    #     },
    #     "price": 200000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 0.05
    # },
    # "Бтр": {
    #     "required_resources": {
    #         "Сталь": 5,
    #         "Дизельное топливо": 3
    #     },
    #     "price": 5000000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 0.2
    # },
    # "Бмп": {
    #     "required_resources": {
    #         "Сталь": 10,
    #         "Микроконтроллеры": 1,
    #         "Дизельное топливо": 5
    #     },
    #     "price": 20000000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 0.5
    # },
    # "Обт": {
    #     "required_resources": {
    #         "Сталь": 20,
    #         "Микроконтроллеры": 3,
    #         "Дизельное топливо": 10
    #     },
    #     "price": 100000000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 1
    # },
    # "Гаубица": {
    #     "required_resources": {
    #     },
    #     "price": 10000000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 0.5
    # },
    # "Сау": {
    #     "required_resources": {
    #     },
    #     "price": 15000000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 0.5
    # },
    # "Переносной птрк": {
    #     "required_resources": {
    #     },
    #     "price": 1000000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 0.1
    # },
    # "Самоходный птрк": {
    #     "required_resources": {
    #     },
    #     "price": 10000000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 0.5
    # },
    # "Зрк": {
    #     "required_resources": {
    #         "Микроконтроллеры": 3
    #     },
    #     "price": 50000000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 1
    # },
    # "Рсзо": {
    #     "required_resources": {
    #     },
    #     "price": 20000000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 0.5
    # },
    # "Многоцелевой истребитель": {
    #     "required_resources": {
    #         "Сталь": 10,
    #         "Микроконтроллеры": 10
    #     },
    #     "price": 500000000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 1
    # },
    # "Истребитель": {
    #     "required_resources": {
    #         "Сталь": 8,
    #         "Микроконтроллеры": 10
    #     },
    #     "price": 450000000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 1
    # },
    # "Штурмовик": {
    #     "required_resources": {
    #         "Сталь": 10,
    #         "Микроконтроллеры": 8
    #     },
    #     "price": 400000000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 1
    # },
    # "Стратегический бомбардировщик": {
    #     "required_resources": {
    #         "Сталь": 20,
    #         "Микроконтроллеры": 20
    #     },
    #     "price": 1000000000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 3
    # },
    # "Фрегат": {
    #     "required_resources": {
    #         "Сталь": 30,
    #         "Микроконтроллеры": 10
    #     },
    #     "price": 100000000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 2
    # },
    # "Эсминец": {
    #     "required_resources": {
    #         "Сталь": 50,
    #         "Микроконтроллеры": 30
    #     },
    #     "price": 1000000000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 5
    # },
    # "Крейсер": {
    #     "required_resources": {
    #         "Сталь": 80,
    #         "Микроконтроллеры": 50
    #     },
    #     "price": 3000000000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 10
    # },
    # "Авианосец": {
    #     "required_resources": {
    #         "Сталь": 120,
    #         "Микроконтроллеры": 10
    #     },
    #     "price": 10000000000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 15
    # },
    # "Подлодка": {
    #     "required_resources": {
    #         "Сталь": 30,
    #         "Микроконтроллеры": 10
    #     },
    #     "price": 500000000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 3
    # },
    # "Ударный вертолёт": {
    #     "required_resources": {
    #         "Сталь": 20,
    #         "Микроконтроллеры": 5
    #     },
    #     "price": 150000000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 1
    # },
    # "Транспортный вертолёт": {
    #     "required_resources": {
    #         "Сталь": 25
    #     },
    #     "price": 300000000,
    #     "build_time": 30,
    #     "required_item": "Военный завод",
    #     "items_required": 1
    # },
}


def is_item_building(user_id):
    return user_id in building_items and len(building_items[user_id]) > 0


def is_item_built(user_id, item):
    if user_id in building_items:
        for building_item in building_items[user_id]:
            if building_item["item"] == item:
                return True
    return False


def add_building_item(user_id, item, amount, start_time):
    if user_id not in building_items:
        building_items[user_id] = []
    building_items[user_id].append({
        "item": item,
        "amount": amount,
        "start_time": start_time
    })
    save_building_items()


def consume_resources(user_id, required_resources, amount):
    for resource, quantity in required_resources.items():
        update_user_resources(user_id, resource, -quantity * amount)


def subtract_currency(user_id, amount):
    update_user_balance(user_id, -amount)


@bot.command(name="build")
async def build(ctx, amount: str, *item_name: str):
    item_name = " ".join(item_name)
    item_name = item_name.capitalize()

    user_id = ctx.author.id
    user_balance = get_user_balance(user_id)
    user_inventory = get_user_inventory(user_id)

    if "Стройкомплекс" in user_inventory:
        max_builds = (user_inventory["Стройкомплекс"] // 10) + 6
    else:
        max_builds = 6
    # if "Военный завод" in user_inventory:
    #     max_wars = user_inventory["Военный завод"]
    # else:
    #     max_wars = 0


    amount = amount.replace(",", "")
    amount = int(amount)

    # Проверяем, если количество меньше 1, выводим сообщение об ошибке
    if amount < 1:
        embed = discord.Embed(
            description="Количество должно быть больше или равно 1",
            color=badColor
        )
        await ctx.send(embed=embed)
        return

    if item_name not in conversion_rules:
        needed_items_names = {}
        items = build_rules
        i = 1
        for item in items:
            if item.find(item_name) != -1:
                needed_items_names[item] = i
                i += 1
        if len(needed_items_names) > 1:
            desc = ""
            for name in needed_items_names:
                desc += f"[{str(needed_items_names[name])}] - {name}\n"
            await ctx.send(embed=discord.Embed(title="Найдено несколько рецептов:", description=desc, color=infoColor))
            numbers = []
            for name in needed_items_names:
                numbers.append(str(needed_items_names[name]))
            try:
                response = await bot.wait_for('message', timeout=30, check=lambda
                    message: message.author == ctx.author and message.channel == ctx.channel)

                resp = response.content.lower()
                if resp in numbers:
                    number = resp
                    need_name = ""
                    for name in needed_items_names:
                        if str(needed_items_names[name]) == number:
                            need_name = name
                    item_name = need_name
                else:
                    await ctx.send(embed=discord.Embed(title="Введено неверное число, строительство отменено", color=badColor))
                    return
            except asyncio.TimeoutError:
                await ctx.send(embed=discord.Embed(title="Время вышло, строительство отменено", color=badColor))
                return

        elif len(needed_items_names) == 1:
            for name in needed_items_names:
                item_name = name
        else:
            embed = discord.Embed(title="Рецепт не найден", color=badColor)
            await ctx.send(embed=embed)
            return

    if item_name == "Ядерная боеголовка 30 кт" or item_name == "Ядерная боеголовка 60 кт" or item_name == "Ядерная боеголовка 100 кт" or item_name == "Термоядерная боеголовка 300 кт" or item_name == "Термоядерная боеголовка 1 мт" or item_name == "Термоядерная боеголовка 3 мт":
        if "Ядерная программа" not in user_inventory:
            await ctx.send(
                embed=discord.Embed(description=f"Для производства {item_name} необходимо наличие ядерной программы",
                                    color=badColor))
            return

    # Получаем правила построения для указанного предмета
    build_rule = build_rules[item_name]

    # Проверяем, если предмет уже находится в процессе постройки
    if is_item_building(user_id) and is_item_built(user_id, item_name):
        embed = discord.Embed(
            description=f"{item_name} уже находится в процессе постройки",
            color=badColor
        )
        await ctx.send(embed=embed)
        return


    total_builds = 0
    if is_item_building(user_id):
        for items in building_items[user_id]:
            total_builds += items["amount"]
    # Проверяем, если пользователь превысил лимит построек
    if total_builds + amount > max_builds:
        embed = discord.Embed(
            description=f"Одновременно может идти не более {max_builds} строек",
            color=badColor
        )
        await ctx.send(embed=embed)
        return
    # else:
    #     total_builds = 0
    #     if is_item_building(user_id):
    #         for items in building_items[user_id]:
    #             build_rule1 = build_rules[items]
    #             total_builds += items["amount"] * build_rule1["items_required"]
    #     total_builds = math.ceil(total_builds)
    #     # Проверяем, если пользователь превысил лимит построек
    #     if total_builds + (amount * build_rule["items_required"]) > max_wars:
    #         embed = discord.Embed(
    #             description=f"Одновременно может быть занято не более {max_wars} военных заводов",
    #             color=badColor
    #         )
    #         await ctx.send(embed=embed)
    #         return

    # Проверяем, если у пользователя недостаточно денег
    if user_balance < build_rule["price"] * amount:
        embed = discord.Embed(
            description=f"Недостаточно денег для постройки {amount} {item_name}",
            color=badColor
        )
        await ctx.send(embed=embed)
        return

    # Проверяем, если у пользователя достаточно ресурсов
    if not has_sufficient_resources(user_id, build_rule["required_resources"], amount):
        embed = discord.Embed(
            description=f"Недостаточно ресурсов для постройки {amount} {item_name}",
            color=badColor
        )
        await ctx.send(embed=embed)
        return

    # Вычитаем стоимость постройки из баланса пользователя
    subtract_currency(user_id, build_rule["price"] * amount)

    # Вычитаем требуемые ресурсы из инвентаря пользователя
    consume_resources(user_id, build_rule["required_resources"], amount)

    # Добавляем предмет в процесс постройки
    build_time = build_rule.get("build_time") * 60
    start_time = time.time()
    add_building_item(user_id, item_name, amount, start_time)

    embed = discord.Embed(
        description=f"Началась стройка {amount} {item_name}",
        color=goodColor
    )

    if item_name == "Ядерная программа":
        channel = news_channel
        title = "Ядерные исследования"
        desc = f"Сегодня {ctx.author.mention} начал разработку своей ядерной программы. Неизвестно к чему это приведёт в будущем, но это точно создаст большую угрозу миру на планете"
        path = "D:/RP World Bot/Images/NucRes.jpg"
        await send_message_with_image(channel, title, desc, path)

    await ctx.send(embed=embed)


@bot.command(name="collect-build")
async def collect_buildings(ctx):
    user_id = ctx.author.id

    # Проверяем, если у пользователя есть предметы для сбора
    if user_id not in building_items or len(building_items[user_id]) == 0:
        embed = discord.Embed(
            description="Нет строящихся/построившихся зданий/предметов",
            color=badColor
        )
        await ctx.send(embed=embed)
        return

    description = ""
    min_time = -255000000

    collected_items = []
    remaining_items = []

    for building_item in building_items[user_id]:
        item = building_item["item"]
        amount = building_item["amount"]
        start_time = building_item["start_time"]
        build_rule = build_rules.get(item, {})  # Получаем правила построения для указанного предмета
        build_time = build_rule.get("build_time") * 60  # Значение по умолчанию: 1800 секунд (30 минут)
        elapsed_time = time.time() - (start_time + build_time)

        if elapsed_time >= 0:
            update_user_inventory(user_id, item, amount)
            collected_items.append((item, amount))
        else:
            remaining_items.append(building_item)
            if elapsed_time > min_time:
                min_time = elapsed_time

    building_items[user_id] = remaining_items

    need_time = -(int(min_time // 60))
    if need_time > 4 and need_time < 9:
        if need_time > 4 and need_time < 7:
            description = f"До готовности ближайшей стройки осталось ещё 5-6 так называемых минут"
        else:
            description = f"До готовности ближайшей стройки осталось ещё 7-8 так называемых минут"
    else:
        description = f"До готовности ближайшей стройки осталось {need_time} минут"

    if len(collected_items) > 0:
        items_text = "\n".join([f"{item}: {amount}" for item, amount in collected_items])
        embed = discord.Embed(
            description=f"Построено:\n{items_text}",
            color=goodColor
        )
    else:
        embed = discord.Embed(
            description=description,
            color=badColor
        )

    await ctx.send(embed=embed)
    save_building_items()


@bot.command(name='trade')
async def trade(ctx, recipient: discord.User, amount: str, price: str, *item: str):

    item = " ".join(item)
    item = item.capitalize()

    # Проверяем, есть ли у отправителя достаточно предметов для продажи
    sender_id = ctx.author.id
    server = ctx.guild
    sender_resources = get_user_resources(sender_id)

    if item not in sender_resources or sender_resources[item] < int(amount.replace(',', '')):
        needed_items_names = {}
        items = sender_resources
        i = 1
        for item in items:
            if item.find(item) != -1:
                needed_items_names[item] = i
                i += 1
        if len(needed_items_names) > 1:
            desc = ""
            for name in needed_items_names:
                desc += f"[{str(needed_items_names[name])}] - {name}\n"
            await ctx.send(embed=discord.Embed(title="Найдено несколько ресурсов:", description=desc, color=infoColor))
            numbers = []
            for name in needed_items_names:
                numbers.append(str(needed_items_names[name]))
            try:
                response = await bot.wait_for('message', timeout=30, check=lambda
                    message: message.author == ctx.author and message.channel == ctx.channel)

                resp = response.content.lower()
                if resp in numbers:
                    number = resp
                    need_name = ""
                    for name in needed_items_names:
                        if str(needed_items_names[name]) == number:
                            need_name = name
                    item = need_name
                else:
                    await ctx.send(embed=discord.Embed(title="Введено неверное число, продажа отменена", color=badColor))
                    return
            except asyncio.TimeoutError:
                await ctx.send(embed=discord.Embed(title="Время вышло, продажа отменена", color=badColor))
                return

        elif len(needed_items_names) == 1:
            for name in needed_items_names:
                item = name
        else:
            embed = discord.Embed(title="Ресурс не найден", color=badColor)
            await ctx.send(embed=embed)
            return




    # Проверяем, разрешает ли получатель продажу
    embed = discord.Embed(
        description=f"{ctx.author.mention} хочет продать вам {amount} {item} по цене {price} {emoji}. Согласиться (да) или отказаться (нет)?",
        color=infoColor)
    await ctx.send(recipient.mention)
    await ctx.send(embed=embed)

    def check_author(message):
        return message.author == recipient and message.channel == ctx.channel

    try:
        confirmation = await bot.wait_for('message', check=check_author, timeout=60.0)
    except asyncio.TimeoutError:
        await ctx.send(embed=discord.Embed(title="Время ожидания истекло. Продажа отменена.", color=badColor))
        return

    if confirmation.content.lower() != 'да':
        await ctx.send(embed=discord.Embed(title="Продажа отменена.", color=badColor))
        return
    # Вычитаем проданные предметы из инвентаря отправителя
    update_user_resources(sender_id, item, -int(amount.replace(',', '')))

    # Добавляем проданные предметы и деньги получателю
    recipient_id = recipient.id
    update_user_resources(recipient_id, item, int(amount.replace(',', '')))
    update_user_balance(recipient_id, int(price.replace(',', '')))

    # Отправляем сообщение об успешной продаже
    await ctx.send(embed=discord.Embed(
        description=f"{ctx.author.mention} продал {amount} {item} {recipient.mention} за {price} {emoji}.",
        color=goodColor))


@bot.command(name="war")
@commands.has_any_role(administrator_role, administrator_s_role, deputy_role, creator_role)
async def initiate_war(ctx, *users: discord.Member):
    user_ids = [str(user.id) for user in users]
    initiator_id = str(ctx.author.id)

    for user in users:
        for userA in users:
            if user.id != userA.id:
                user_file_path = f"D:/RP World Bot/Users/{user.id}_wars.txt"
                if os.path.isfile(user_file_path):
                    with open(user_file_path, "a") as file:
                        file.write(str(user.id) + "\n")
                else:
                    with open(user_file_path, "w") as file:
                        file.write(str(user.id) + "\n")

    await ctx.send(embed=discord.Embed(
        description=f"Война инициирована с пользователями: {', '.join([user.nick for user in users])}",
        color=goodColor))
    channel = news_channel
    title = "Война"
    desc = f"Начался вооружённый конфликт между странами, его участники: {', '.join([user.mention for user in users])}"
    pict = "D:/RP World Bot/Images/war_start.jpg"
    await send_message_with_image(channel, title, desc, pict)


@bot.command(name="war-stop")
@commands.has_any_role(administrator_role, administrator_s_role, deputy_role, creator_role)
async def stop_war(ctx, *users: discord.Member):
    user_ids = [str(user.id) for user in users]

    for user in users:
        user_file_path = f"D:/RP World Bot/Users/{user.id}_wars.txt"
        if os.path.isfile(user_file_path):
            with open(user_file_path, "r") as file:
                lines = file.readlines()

            with open(user_file_path, "w") as file:
                for line in lines:
                    if line.strip() not in user_ids:
                        file.write(line)

    await ctx.send(embed=discord.Embed(
        description=f"Война остановлена между пользователями: {', '.join([user.name for user in users])}",
        color=goodColor))
    channel = news_channel
    title = "Конец войны"
    desc = f"Завершился вооружённый конфликт между странами, его участники: {', '.join([user.mention for user in users])}"
    pict = "D:/RP World Bot/Images/war_stop.jpg"
    await send_message_with_image(channel, title, desc, pict)


import discord
import os

balance_file_path = 'D:/RP World Bot/Users/balance.txt'
investment_file_path = 'D:/RP World Bot/Users/investments.txt'


@bot.command(name='bal')
async def balance(ctx, user: discord.Member = None):
    # Получаем пользователя, отправившего команду
    if user is None:
        user = ctx.author
    server = ctx.guild

    # Получаем баланс пользователя из файла
    user_balance = get_user_balance(user.id)
    user_investments = get_user_investment(user.id)
    user_profit = int(get_user_investment(user.id) * (invest_profit / 100))

    formatted_balance = "{:,}".format(user_balance)
    formatted_investments = "{:,}".format(user_investments)
    formatted_profit = "{:,}".format(user_profit)

    embed = discord.Embed(
        description=f"Текущий баланс: {formatted_balance} " + emoji + f"\nНа инвестиционном счёте находится {formatted_investments} {emoji}, это приносит {formatted_profit} {emoji} каждые 30 минут",
        color=infoColor)
    embed.set_author(name=user.nick, icon_url=user.avatar.url)
    # Отправляем сообщение с балансом пользователю
    await ctx.send(embed=embed)


@bot.command(name="inv")
async def resources(ctx, user: discord.Member = None):
    server = ctx.guild
    if user is None:
        user = ctx.author
    user_inventory = get_user_inventory(user.id)

    if not user_inventory:
        embed = discord.Embed(title="Инвентарь пуст", color=infoColor)
        embed.set_author(name=user.nick, icon_url=user.avatar.url)
        await ctx.send(embed=embed)
        return

    inventory_message = ""
    for item, quantity in user_inventory.items():
        inventory_message += f"{item}: {quantity:,}\n"

    embed = discord.Embed(description=inventory_message, color=infoColor)
    embed.set_author(name=user.nick, icon_url=user.avatar.url)
    await ctx.send(embed=embed)


@bot.command(name="res")
async def resources(ctx, user: discord.Member = None):
    server = ctx.guild
    if user is None:
        user = ctx.author
    user_resources = get_user_resources(user.id)

    if not user_resources:
        embed = discord.Embed(title="На складах ничего нет", color=infoColor)
        embed.set_author(name=user.nick, icon_url=user.avatar.url)
        await ctx.send(embed=embed)
        return

    resources_message = ""
    for item, quantity in user_resources.items():
        resources_message += f"{item}: {quantity:,}\n"

    embed = discord.Embed(description=resources_message, color=infoColor)
    embed.set_author(name=user.nick, icon_url=user.avatar.url)
    await ctx.send(embed=embed)


# @bot.command(name="army")
# async def show_army(ctx, user: discord.User = None):
#     server = ctx.guild
#     if user is None:
#         user = ctx.author
#     user_army = get_user_army(user.id)
#
#     if not user_army:
#         embed = discord.Embed(title="Казармы пусты", color=embedColor)
#         embed.set_author(name=user.nick, icon_url=user.avatar.url)
#         await ctx.send(embed=embed)
#         return
#
#     army_message = ""
#     for unit, quantity in user_army.items():
#         army_message += f"{unit}: {quantity:,}\n"
#
#     embed = discord.Embed(description=army_message, color=embedColor)
#     embed.set_author(name=user.nick, icon_url=user.avatar.url)
#     await ctx.send(embed=embed)

@bot.command(name='delete-item')
@commands.has_any_role(tech_creator_role, administrator_role, administrator_s_role, deputy_role, creator_role)
async def delete_item(ctx, *item_name: str):
    item_name = " ".join(item_name)

    if ctx.author.id == 1018486099460505622:
        await ctx.send(embed=discord.Embed(title="В доступе отказано",
                                           description=f"Во избежание дальнейших проблем с установкой цен и необходимости вносить изменения в код, пользователь {ctx.author.mention} не имеет доступа к созданию/редактированию/удалению предметов из магазина.",
                                           color=badColor))
        return

    if not check_item_availability(item_name):
        await ctx.send(embed=discord.Embed(title=f"{item_name} не найден в магазине",
                                           color=badColor))

    if remove_item_from_shop(item_name):
        await ctx.send(embed=discord.Embed(title=f"'{item_name}' успешно удален из магазина",
                                           color=goodColor))


@bot.command(name='create-item')
@commands.has_any_role(tech_creator_role, administrator_role, administrator_s_role, deputy_role, creator_role)
async def create_item(ctx, item_name: str, item_price: str, role: discord.Role = None):
    if ctx.author.id == 1018486099460505622:
        await ctx.send(embed=discord.Embed(title="В доступе отказано",
                                           description=f"Во избежание дальнейших проблем с установкой цен и необходимости вносить изменения в код, пользователь {ctx.author.mention} не имеет доступа к созданию/редактированию/удалению предметов из магазина.",
                                           color=badColor))
        return

    # Удаляем запятые из вводимого числа
    item_price = item_price.replace(",", "")

    # Проверяем, существует ли уже предмет с указанным названием
    if check_item_availability(item_name):
        await ctx.send(embed=discord.Embed(title=f"Предмет '{item_name}' уже существует", color=badColor))
        return

    # Добавляем предмет в список существующих предметов
    role_id = role.id if role else None
    add_item(item_name, item_price, role_id)

    await ctx.send(embed=discord.Embed(title=f"Предмет '{item_name}' успешно добавлен в список предметов",
                                       color=goodColor))


@bot.command(name="edit-price")
@commands.has_any_role(tech_creator_role, administrator_role, administrator_s_role, deputy_role, creator_role)
async def edit_item_price(ctx, price: str, *item_name: str):
    item_name = " ".join(item_name)
    price = price.replace(",", "")

    if ctx.author.id == 1018486099460505622:
        await ctx.send(embed=discord.Embed(title="В доступе отказано",
                                           description=f"Во избежание дальнейших проблем с установкой цен и необходимости вносить изменения в код, пользователь {ctx.author.mention} не имеет доступа к созданию/редактированию/удалению предметов из магазина.",
                                           color=badColor))
        return

    if not check_item_availability(item_name):
        await ctx.send(embed=discord.Embed(title="Предмет не найден", color=badColor))
        return

    role = get_role_id_by_item(item_name)

    remove_item_from_shop(item_name)
    add_item(item_name, price, role)

    await ctx.send(embed=discord.Embed(description="Цена успешно перезаписана", color=goodColor))


ITEMS_FILE_PATH = "D:/RP World Bot/Server/items.txt"

itemsPerPage = 50  # Количество предметов на странице


def get_all_items():
    items = {}
    if not os.path.exists(ITEMS_FILE_PATH):
        return items
    with open(ITEMS_FILE_PATH, "r", encoding="utf-8") as file:
        for line in file:
            item_data = line.strip().split(":")
            name = item_data[0]
            price = int(item_data[1])
            role_id = item_data[2] if len(item_data) > 2 and item_data[2] != "None" else None
            items[name] = {"price": price, "role_id": role_id}
    return items


def format_price(price):
    return "{:,}".format(price)  # Форматируем цену с разделителями разрядов


@bot.command(name='shop')
async def shop(ctx):
    items = get_all_items()
    if not items:
        await ctx.send(embed=discord.Embed(title="В магазине нет доступных предметов.", color=infoColor))
        return

    total_pages = (len(items) - 1) // itemsPerPage + 1
    page = 1

    description = ""
    for item_name, item_info in items.items():
        item_price = item_info["price"]
        formatted_price = format_price(item_price)  # Форматируем цену
        description += f"**{item_name}**\n {formatted_price} {emoji}"

        role_id = item_info["role_id"]
        if role_id:
            role = ctx.guild.get_role(role_id)
            if role:
                description += f" (Требуется роль: {role.mention})"
        description += "\n\n"

        if len(description) >= 2000:  # Отправляем сообщение, когда достигли максимального размера описания
            embed = discord.Embed(title="Магазин", description=description[:2000], color=infoColor)
            embed.set_footer(text=f"Страница {page}/{total_pages}")
            await ctx.send(embed=embed)
            description = ""
            page += 1

    if description:  # Отправляем оставшиеся предметы, если они есть
        embed = discord.Embed(title="Магазин", description=description, color=infoColor)
        embed.set_footer(text=f"Страница {page}/{total_pages}")
        await ctx.send(embed=embed)


# @bot.command(name='give-army')
# @commands.has_any_role(1100163622379995278, 1100165902646906910, 1099790203863969942)
# async def give_army(ctx, user: discord.Member, unit_name: str, unit_quantity: str):
#     server = ctx.guild
#     if not any(role.id in [1100163622379995278, 1100165902646906910, 1099790203863969942] for role in ctx.author.roles):
#         await ctx.send(embed=discord.Embed(title="У вас недостаточно прав для выполнения этой команды.", color=badColor))
#         return
#
#     unit_quantity = int(unit_quantity.replace(",", ""))
#     user_id = user.id
#
#     update_user_army(user_id, unit_name, unit_quantity)
#
#     await ctx.send(embed=discord.Embed(description=f"Пользователю {user.mention} выдано {unit_quantity} {unit_name}.",
#                                        color=goodColor))

# @bot.command(name='take-army')
# @commands.has_any_role(1100163622379995278, 1100165902646906910, 1099790203863969942)
# async def take_army(ctx, user: discord.Member, unit_name: str, unit_quantity: str):
#     server = ctx.guild
#     if not any(role.id in [1100163622379995278, 1100165902646906910, 1099790203863969942] for role in ctx.author.roles):
#         await ctx.send(embed=discord.Embed(title="У вас недостаточно прав для выполнения этой команды.", color=badColor))
#         return
#
#     unit_quantity = int(unit_quantity.replace(",", ""))
#     user_id = user.id
#
#     update_user_army(user_id, unit_name, -unit_quantity)
#
#     await ctx.send(embed=discord.Embed(description=f"У пользователя {user.mention} удалено {unit_quantity} {unit_name}.",
#                                        color=goodColor))

@bot.command(name='buy')
async def buy(ctx, quantity: str, *item_name: str):
    item_name = " ".join(item_name)
    item_name = item_name.capitalize()

    # Удаление запятых из введенного количества
    quantity = quantity.replace(",", "")

    # Проверка введенного количества на корректность
    if not quantity.isdigit():
        embed = discord.Embed(
            title="Некорректное количество",
            color=badColor
        )
        await ctx.send(embed=embed)
        return

    quantity = int(quantity)
    item_price = get_item_price(item_name)
    role_id = get_role_id_by_item(item_name)

    if item_price is None:
        needed_items_names = {}
        items = get_all_items1()
        i = 1
        for item in items:
            if item.find(item_name) != -1:
                needed_items_names[item] = i
                i += 1
        if len(needed_items_names) > 1:
            desc = ""
            for name in needed_items_names:
                desc += f"[{str(needed_items_names[name])}] - {name}\n"
            await ctx.send(embed=discord.Embed(title="Найдено несколько предметов:", description=desc, color=infoColor))
            numbers = []
            for name in needed_items_names:
                numbers.append(str(needed_items_names[name]))
            try:
                response = await bot.wait_for('message', timeout=30, check=lambda
                    message: message.author == ctx.author and message.channel == ctx.channel)

                resp = response.content.lower()
                if resp in numbers:
                    number = resp
                    need_name = ""
                    for name in needed_items_names:
                        if str(needed_items_names[name]) == number:
                            need_name = name
                    item_price = get_item_price(need_name)
                    role_id = get_role_id_by_item(need_name)
                    item_name = need_name
                else:
                    await ctx.send(embed=discord.Embed(title="Введено неверное число, покупка отменена", color=badColor))
                    return
            except asyncio.TimeoutError:
                await ctx.send(embed=discord.Embed(title="Время вышло, покупка отменена", color=badColor))
                return

        elif len(needed_items_names) == 1:
            for name in needed_items_names:
                item_price = get_item_price(name)
                role_id = get_role_id_by_item(name)
                item_name = name
        else:
            embed = discord.Embed(title="Предмет не найден", color=badColor)
            await ctx.send(embed=embed)
            return

            # Проверка требуемой роли
    if role_id is not None and role_id != ' None':  # Изменение в этой строке
        role = discord.utils.get(ctx.guild.roles, id=int(role_id))
        if role is None or role not in ctx.author.roles:
            embed = discord.Embed(
                title="Нет необходимой роли для покупки этого предмета",
                color=badColor
            )
            await ctx.send(embed=embed)
            return

    total_price = item_price * quantity

    # Проверка баланса пользователя
    user_balance = get_user_balance(ctx.author.id)  # Получение баланса пользователя
    if user_balance < total_price:
        embed = discord.Embed(
            title="Недостаточно денег для покупки",
            color=badColor
        )
        await ctx.send(embed=embed)
        return

    # Вычитаем стоимость покупки из баланса пользователя
    update_user_balance(ctx.author.id, -total_price)  # Вычитаем стоимость из баланса пользователя

    # Добавляем предметы к пользователю
    update_user_inventory(ctx.author.id, item_name, quantity)  # Добавляем предметы пользователю

    embed = discord.Embed(
        description=f"Успешно куплено {quantity} {item_name} за {total_price:,} {emoji}",
        color=goodColor
    )
    await ctx.send(embed=embed)


async def confirm_clear_inv(ctx, user: discord.User):
    await ctx.send(embed=discord.Embed(
        description=f"Очистить инвентарь {user.mention}? Это действие нельзя отменить. Введите 'да' для подтверждения",
        color=infoColor))

    try:

        response = await bot.wait_for('message', timeout=30, check=lambda
            message: message.author == ctx.author and message.channel == ctx.channel)

        # Проверяем ответ пользователя
        if response.content.lower() == 'да':
            user_id = user.id
            inv = get_user_inventory(user_id)

            for item, quantity in inv.items():
                update_user_inventory(user_id, item, -quantity)
            await ctx.send(embed=discord.Embed(title="Инвентарь успешно очищен", color=goodColor))
        else:
            await ctx.send(embed=discord.Embed(title="Очистка отменена", color=badColor))
    except asyncio.TimeoutError:
        await ctx.send(embed=discord.Embed(title="Время ожидания истекло. Очистка отменена", color=badColor))


@bot.command(name="reset-inv")
@commands.has_any_role(administrator_role, administrator_s_role, deputy_role, creator_role)
async def reset_inventory(ctx, user: discord.User):
    await confirm_clear_inv(ctx, user)


@bot.command(name="add-money")
@commands.has_any_role(administrator_role, administrator_s_role, deputy_role, creator_role)
async def add_money(ctx, user: discord.User, amount: str):
    amount = amount.replace(',', '')

    amount = int(amount)
    server = ctx.guild
    update_user_balance(user.id, amount)

    await ctx.send(
        embed=discord.Embed(
            description=f"Успешно добавлено {amount:,} " + emoji + f" к балансу пользователя {user.mention}.",
            color=goodColor))


@add_money.error
async def add_money_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send(
            embed=discord.Embed(title="У вас недостаточно прав для выполнения этой команды.", color=badColor))


@bot.command(name="remove-money")
@commands.has_any_role(administrator_role, administrator_s_role, deputy_role, creator_role)
async def remove_money(ctx, user: discord.User, amount: str):
    if user.id == 644813283936829470:
        await ctx.send(":angry:")
        return

    amount = amount.replace(',', '')

    if not amount.isdigit():
        await ctx.send("Введено некорректное число.")
        return

    amount = int(amount)
    update_user_balance(user.id, -amount)

    await ctx.send(embed=discord.Embed(
        description=f"Успешно удалено {amount:,} " + emoji + f" с баланса пользователя {user.nick}.", color=goodColor))


@remove_money.error
async def remove_money_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send(
            embed=discord.Embed(title="У вас недостаточно прав для выполнения этой команды.", color=badColor))


@bot.command(name="reset-money")
@commands.has_any_role(administrator_role, administrator_s_role, deputy_role, creator_role)
async def reset_money(ctx, user: discord.User):
    if user.id == 644813283936829470:
        await ctx.send(":angry:")
        return
    update_user_balance(user.id, -get_user_balance(user.id))

    await ctx.send(
        embed=discord.Embed(description=f"Успешно обнулён баланс пользователя {user.mention}.", color=goodColor))


@reset_money.error
async def reset_money_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send(
            embed=discord.Embed(title="У вас недостаточно прав для выполнения этой команды.", color=badColor))


async def confirm_clear_data(ctx):
    await ctx.send(embed=discord.Embed(
        title="Вы действительно хотите обнулить ~~баланс всех пользователей?~~ всю информацию о всех пользователях? Это действие нельзя отменить. Введите 'да' для подтверждения.",
        color=infoColor))

    try:

        response = await bot.wait_for('message', timeout=30, check=lambda
            message: message.author == ctx.author and message.channel == ctx.channel)

        # Проверяем ответ пользователя
        if response.content.lower() == 'да':
            clear_user_data_files()
            await ctx.send(embed=discord.Embed(title="Баланс всех пользователей успешно очищен.", color=goodColor))
        else:
            await ctx.send(embed=discord.Embed(title="Очистка данных отменена.", color=badColor))
    except asyncio.TimeoutError:
        await ctx.send(embed=discord.Embed(title="Время ожидания истекло. Очистка данных отменена.", color=badColor))


@bot.command(name='reset-economy')
async def clear_data(ctx):
    if ctx.author.id != 644813283936829470:
        user_id = 644813283936829470
        user = await bot.fetch_user(user_id)
        await ctx.send(
            embed=discord.Embed(title=f"Только {user.mention} может использовать эту команду", color=badColor))
        return
    await confirm_clear_data(ctx)


user_data_path = "D:/RP World Bot/Users"


def get_user_balance(user_id):
    filename = f"D:/RP World Bot/Users/{user_id}.txt"
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            balance = int(file.read())
            return balance
    else:
        return 1000000000


def update_user_balance(user_id, amount):
    filename = f"D:/RP World Bot/Users/{user_id}.txt"
    balance = get_user_balance(user_id)
    balance += amount
    with open(filename, 'w') as file:
        file.write(str(int(balance)))


def get_user_investment(user_id):
    filename = f"D:/RP World Bot/Users/{user_id}_investments.txt"
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            investment = int(file.read())
            return investment
    else:
        return 0


def update_user_investment(user_id, amount):
    filename = f"D:/RP World Bot/Users/{user_id}_investments.txt"
    investment = get_user_investment(user_id)
    investment += amount
    with open(filename, 'w') as file:
        file.write(str(investment))


def get_user_inventory(user_id):
    inventory_path = f"D:/RP World Bot/Users/{user_id}_inventory.txt"
    inventory = {}

    if os.path.exists(inventory_path):
        with open(inventory_path, "r") as file:
            for line in file:
                item, quantity = line.strip().split(":")
                inventory[item.strip()] = int(quantity.strip())

    return inventory


def update_user_inventory(user_id, item_name, item_quantity):
    file_path = f"D:/RP World Bot/Users/{user_id}_inventory.txt"

    inventory = get_user_inventory(user_id)

    if item_name in inventory:
        inventory[item_name] += item_quantity

        if inventory[item_name] <= 0:
            del inventory[item_name]
    else:
        if item_quantity > 0:
            inventory[item_name] = item_quantity

    save_inventory(file_path, inventory)


def save_inventory(file_path, inventory):
    with open(file_path, "w") as file:
        for item, quantity in inventory.items():
            file.write(f"{item}: {quantity}\n")


# def get_user_army(user_id):
#     army_path = f"D:/RP World Bot/Users/{user_id}_army.txt"
#     army = {}
#
#     if os.path.exists(army_path):
#         with open(army_path, "r") as file:
#             for line in file:
#                 unit, quantity = line.strip().split(":")
#                 army[unit.strip()] = int(quantity.strip())
#
#     return army
#
#
# def update_user_army(user_id, unit_name, unit_quantity):
#     file_path = f"D:/RP World Bot/Users/{user_id}_army.txt"
#
#     army = get_user_army(user_id)
#
#     if unit_name in army:
#         army[unit_name] += unit_quantity
#
#         if army[unit_name] <= 0:
#             del army[unit_name]
#     else:
#         if unit_quantity > 0:
#             army[unit_name] = unit_quantity
#
#     save_army(file_path, army)
#
#
# def save_army(file_path, army):
#     with open(file_path, "w") as file:
#         for unit, quantity in army.items():
#             file.write(f"{unit}: {quantity}\n")


# Функция создания нового файла пользователя, если его еще нет
def create_user_file(user_id):
    filename = f"D:/RP World Bot/Users/{user_id}.txt"
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            file.write("0")


def get_user_resources(user_id):
    resources_path = f"D:/RP World Bot/Users/{user_id}_resources.txt"
    resources = {}

    if os.path.exists(resources_path):
        with open(resources_path, "r") as file:
            for line in file:
                resource, quantity = line.strip().split(":")
                resources[resource.strip()] = int(quantity.strip())

    return resources


def update_user_resources(user_id, resource_name, resource_quantity):
    file_path = f"D:/RP World Bot/Users/{user_id}_resources.txt"

    resources = get_user_resources(user_id)

    if resource_name in resources:
        resources[resource_name] += resource_quantity

        if resources[resource_name] <= 0:
            del resources[resource_name]
    else:
        if resource_quantity > 0:
            resources[resource_name] = resource_quantity

    save_resources(file_path, resources)


def save_resources(file_path, resources):
    with open(file_path, "w") as file:
        for resource, quantity in resources.items():
            file.write(f"{resource}: {int(quantity)}\n")


def get_all_items1():
    items = {}
    if not os.path.exists(ITEMS_FILE_PATH):
        return items
    with open(ITEMS_FILE_PATH, "r", encoding="utf-8") as file:
        for line in file:
            item_data = line.strip().split(":")
            name = item_data[0]
            price = int(item_data[1])
            role_id = item_data[2] if len(item_data) > 2 else None
            items[name] = (price, role_id)
    return items


def get_item_price(item_name):
    items = get_all_items1()
    return items.get(item_name, (None, None))[0]


def get_role_id_by_item(item_name):
    items = get_all_items1()
    for name, (price, role_id) in items.items():
        if name.lower() == item_name.lower():
            return role_id
    return None


def remove_item_from_shop(item_name):
    if not os.path.exists(ITEMS_FILE_PATH):
        return False

    items = []
    with open(ITEMS_FILE_PATH, "r", encoding="utf-8") as file:
        for line in file:
            item_data = line.strip().split(":")
            name = item_data[0].strip()
            if name.lower() != item_name.lower():
                items.append(line)

    with open(ITEMS_FILE_PATH, "w", encoding="utf-8") as file:
        file.writelines(items)

    return True


def add_item(item_name, item_price, role_id=None):
    if not os.path.exists(ITEMS_FILE_PATH):
        with open(ITEMS_FILE_PATH, "w", encoding="utf-8") as file:
            file.write(f"{item_name}: {item_price}: {role_id}\n")
        return
    with open(ITEMS_FILE_PATH, "a", encoding="utf-8") as file:
        file.write(f"{item_name}: {item_price}: {role_id}\n")


def check_item_availability(item_name):
    if not os.path.exists(ITEMS_FILE_PATH):
        return False
    with open(ITEMS_FILE_PATH, "r", encoding="utf-8") as file:
        for line in file:
            item_data = line.strip().split(":")
            name = item_data[0]
            if name.strip() == item_name:
                return True
    return False


AUTONOMY_DIR = "D:/RP World Bot/Users"


def get_autonomy_file(user_id):
    return AUTONOMY_DIR + f"/{user_id}_autonomy.txt"


def save_user_autonomy(user_id, autonomy_type, metropolis_id):
    file_path = get_autonomy_file(user_id)
    with open(file_path, "w") as file:
        file.write(f"{autonomy_type}: {metropolis_id}")


def load_user_autonomy(user_id):
    file_path = get_autonomy_file(user_id)
    if not os.path.exists(file_path):
        return None, None
    with open(file_path, "r") as file:
        line = file.readline().strip()
        autonomy_type, metropolis_id = line.split(":")
        return autonomy_type, int(metropolis_id)


def delete_user_autonomy(user_id):
    file_path = get_autonomy_file(user_id)
    if os.path.exists(file_path):
        os.remove(file_path)


# Функция очистки данных всех пользователей
def clear_user_data_files():
    directory = "D:/RP World Bot/Users"
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)
            os.remove(filepath)
        elif filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            os.remove(filepath)


BUILDING_ITEMS_FILE = "D:/RP World Bot/Users/building_items.json"


def load_building_items():
    building_items = {}
    if os.path.exists(BUILDING_ITEMS_FILE):
        with open(BUILDING_ITEMS_FILE, "r") as file:
            data = json.load(file)
            building_items = data
            return building_items
    else:
        return building_items


def save_building_items():
    with open(BUILDING_ITEMS_FILE, "w") as file:
        json.dump(building_items, file)


building_items = load_building_items()

atexit.register(save_building_items)

bot.run('MTExOTMwMjY3MTQ1MTU2NjE4MQ.Ghd0q-.QjcbncQbpUxkgGNG3zxcembZLJazhpW45MTwrs')
