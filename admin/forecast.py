import telebot
import time
import back.tools
from config.buttons import btn
import admin.menu

bot = back.tools.bot

current_forecast_id = {}

def forecast1(m):
    current_forecast_id[m.chat.id] = back.tools.create_forecast()
    kb = telebot.types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
    kb.add('Да', 'Нет', btn['to_beginning'])
    bot.send_message(m.chat.id, "Нужно прикрепить фотографию?", reply_markup=kb, parse_mode='html')
    bot.register_next_step_handler(m, forecast1_definer)


def forecast1_definer(m):
    if m.text == 'Да':
        forecast2(m)

    elif m.text == 'Нет':
        forecast3(m)

    elif m.text == btn['to_beginning']:
        admin.menu.menu(m)

    else:
        forecast1(m)


def forecast2(m):
    bot.send_message(m.chat.id, 'Прикрепи фотографию. Без подписи')
    bot.register_next_step_handler(m, forecast2_definer)


def forecast2_definer(m):
    if 'photo' in m.json.keys():
        back.tools.set_(current_forecast_id[m.chat.id], 'forecasts', 'photo', m.json['photo'][-1]['file_id'])
        bot.send_message(m.chat.id, '✓ Фотография сохранена')
        forecast3(m)

    else:
        forecast2(m)


def forecast3(m):
    bot.send_message(m.chat.id, 'Напиши текст прогноза:')
    bot.register_next_step_handler(m, forecast3_definer)


def forecast3_definer(m):
    back.tools.set_(current_forecast_id[m.chat.id], 'forecasts', 'text', m.text)
    kb = telebot.types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
    kb.add('Да', 'Нет', btn['to_beginning'])
    bot.send_message(
        chat_id=m.chat.id,
        text="<b>" + m.text + "</b>\nВсе верно?",
        reply_markup=kb,
        parse_mode='html'
    )
    bot.register_next_step_handler(m, forecast3_postdefiner)


def forecast3_postdefiner(m):
    if m.text == 'Да':
        bot.send_message(m.chat.id, '✓ Текст сохранен')
        forecast4(m)

    elif m.text == btn['to_beginning']:
        back.tools.delete(current_forecast_id[m.chat.id], 'forecasts')
        admin.menu.menu(m)

    else:
        forecast3(m)


def forecast4(m):
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
    kb.add(back.tools.date(0))
    kb.add(back.tools.date(1))
    kb.add(back.tools.date(2))
    bot.send_message(m.chat.id, 'Выбери дату прогноза:', reply_markup=kb)
    bot.register_next_step_handler(m, forecast4_definer)


def forecast4_definer(m):
    if m.text == back.tools.date(0) or m.text == back.tools.date(1) or m.text == back.tools.date(2):
        back.tools.set_(current_forecast_id[m.chat.id], 'forecasts', 'date', m.text)
        bot.send_message(m.chat.id, 'Пожалуйста, проверь данные прогноза:', parse_mode='html')

        forecast_photo = back.tools.get('forecasts', 'photo', current_forecast_id[m.chat.id])
        forecast_text = back.tools.get('forecasts', 'text', current_forecast_id[m.chat.id])

        if forecast_photo is not None:
            if len(forecast_text) < 200:
                bot.send_photo(m.chat.id, forecast_photo,
                               caption="<b>Текст:</b> " + forecast_text, parse_mode='html')
            else:
                bot.send_photo(m.chat.id, forecast_photo)
                bot.send_message(m.chat.id, "<b>Текст:</b> " + forecast_text, parse_mode='html')
        else:
            bot.send_message(m.chat.id, "<b>Текст:</b> " + forecast_text, parse_mode='html')

        kb = telebot.types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
        kb.add('Да', 'Нет', btn['to_beginning'])
        bot.send_message(m.chat.id, 'Все верно?', reply_markup=kb, parse_mode='html')
        bot.register_next_step_handler(m, forecast4_postdefiner)

    else:
        bot.send_message(m.chat.id, '<b>Неправильный фотмат даты</b>\nПожалуйста, нажми одну из кнопок', parse_mode='html')
        forecast4(m)


def forecast4_postdefiner(m):
    if m.text == 'Да':
        bot.send_message(m.chat.id, '<b>✓ Данные рассылки сохранены</b>\nПользователи своевременно ее получат.', parse_mode='html')
        admin.menu.menu(m)

    elif m.text == 'Нет':
        back.tools.delete(current_forecast_id[m.chat.id], 'forecasts')
        forecast1(m)

    else:
        forecast4(m)
