import telebot
import back.tools
import admin.direct_message
import admin.dispatch
import admin.forecast
import admin.added_forecasts
import config.settings
from config.buttons import btn

bot = back.tools.bot


def menu(m):
    if m.chat.id in config.settings.admins:
        kb = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
        buttons = [
            btn['forecast'],
            btn['added_forecasts'],
            btn['user amount'],
            btn['unsubscribed users'],
            btn['dispatch'],
            btn['direct message'],
        ]
        kb.add(*buttons)
        bot.send_message(m.chat.id, 'Выбери пункт меню ↓:', reply_markup=kb, parse_mode='html')
        bot.register_next_step_handler(m, menu_definer)


def menu_definer(m):
    if m.text == btn['forecast']:
        admin.forecast.forecast1(m)

    elif m.text == btn['added_forecasts']:
        admin.added_forecasts.added_forecasts1(m)

    elif m.text == btn['user amount']:
        with back.tools.DBConnection(config.settings.database_url) as con:
            curs = con.cursor()
            curs.execute('SELECT FROM users')
            results = curs.fetchall()
            bot.send_message(m.chat.id,
                             "Всего пользователей: <b>" + str(len(results)) + "</b>",
                             parse_mode='html')
        menu(m)

    elif m.text == btn['unsubscribed users']:
        with back.tools.DBConnection(config.settings.database_url) as con:
            curs = con.cursor()
            curs.execute(f'SELECT FROM users WHERE subscribed = false')
            results = curs.fetchall()
            bot.send_message(m.chat.id,
                             "Всего отписавшихся пользователей: <b>" + str(len(results)) + "</b>",
                             parse_mode='html')
        menu(m)

    elif m.text == btn['direct message']:
        admin.direct_message.dm1(m)

    elif m.text == btn['dispatch']:
        admin.dispatch.dispatch1(m)

    else:
        menu(m)



