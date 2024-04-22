import logging
from aiogram import Bot, Dispatcher, types, executor

from config import TELE_TOKEN
from football_api_getters import get_league_table, LEAGUES_DICT, get_current_matches_by_league, \
    get_prediction_by_fixture_id, get_team_players, get_team_form, update_team_dict, get_team_dict
from image_makers import make_standings_table_image, create_wind_rose_by_predictions, create_players_table, \
    create_result_table
from string_transformers import create_current_matches_string

league_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
league_keyboard.add(types.KeyboardButton(text="Table"))
league_keyboard.add(types.KeyboardButton(text="Team"))
league_keyboard.add(types.KeyboardButton(text="Matches on-air"))
league_keyboard.add(types.KeyboardButton(text="Match comparison"))

team_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
team_keyboard.add(types.KeyboardButton(text="Players"))
team_keyboard.add(types.KeyboardButton(text="Last 10 matches"))

CURRENT_LEAGUE = ''
CURRENT_TEAM = ''


logging.basicConfig(level=logging.INFO)
bot = Bot(token=TELE_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Welcome to the Analytics Football Bot! Please specify league that you want to discover:", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(lambda message: message.text in LEAGUES_DICT)
async def handle_league_choice(message: types.Message):
    global CURRENT_LEAGUE

    if CURRENT_LEAGUE != message.text:
        CURRENT_LEAGUE = message.text
        update_team_dict(CURRENT_LEAGUE)
    await message.reply("What do you want to know?", reply_markup=league_keyboard)


@dp.message_handler(lambda message: message.text == "Table")
async def handle_league_table(message: types.Message):
    df = get_league_table(CURRENT_LEAGUE)
    image_path = make_standings_table_image(df)

    with open(image_path, 'rb') as photo:
        await message.answer_photo(photo)

    message.text = CURRENT_LEAGUE
    await handle_league_choice(message)


@dp.message_handler(lambda message: message.text == "Team")
async def handle_team_input(message: types.Message):
    await message.reply(f"What team of the league {CURRENT_LEAGUE} do you want to discover?", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(lambda message: message.text == "Matches on-air")
async def handle_league_matches(message: types.Message):
    df = get_current_matches_by_league(CURRENT_LEAGUE)
    curr_matches = create_current_matches_string(df)

    await message.reply(curr_matches)
    message.text = CURRENT_LEAGUE
    await handle_league_choice(message)


@dp.message_handler(lambda message: message.text == "Match comparison")
async def handle_match_comparison_input(message: types.Message):
    await message.reply(f"Please, enter match id:", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(lambda message: message.text.isnumeric())
async def handle_match_comparison(message: types.Message):
    df = get_prediction_by_fixture_id(message.text)
    image_path, legend = create_wind_rose_by_predictions(df)

    with open(image_path, 'rb') as photo:
        await message.answer_photo(photo)
    await message.reply(legend)

    message.text = CURRENT_LEAGUE
    await handle_league_choice(message)


@dp.message_handler(lambda message: message.text in get_team_dict())
async def handle_team_choice(message: types.Message):
    global CURRENT_TEAM

    CURRENT_TEAM = message.text
    await message.reply("What do you want to know about team?", reply_markup=team_keyboard)


@dp.message_handler(lambda message: message.text == 'Players')
async def handle_team_players(message: types.Message):
    df = get_team_players(CURRENT_TEAM)
    image_path = create_players_table(df)

    with open(image_path, 'rb') as photo:
        await message.answer_photo(photo)

    message.text = CURRENT_TEAM
    await handle_team_choice(message)


@dp.message_handler(lambda message: message.text == 'Last 10 matches')
async def handle_team_last_matches(message: types.Message):
    df = get_team_form(CURRENT_TEAM)
    image_path = create_result_table(df)

    with open(image_path, 'rb') as photo:
        await message.answer_photo(photo)

    message.text = CURRENT_TEAM
    await handle_team_choice(message)


@dp.message_handler()
async def handle_choice(message: types.Message):
    await message.reply('You have entered smth wrong :(')
    await send_welcome(message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
