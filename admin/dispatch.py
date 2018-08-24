import telebot
import back.tools
import config.settings
from config.buttons import btn
import admin.menu

bot = back.tools.bot


dispatch_photo = {}
dispatch_text = {}


def dispatch1(m):
    kb = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    kb.add('Да', 'Нет', btn['to_beginning'])
    bot.send_message(m.chat.id, "Нужно прикрепить фотографию?", reply_markup=kb, parse_mode='html')
    bot.register_next_step_handler(m, dispatch1_definer)


def dispatch1_definer(m):
    if m.text == 'Да':
        dispatch2(m)

    elif m.text == 'Нет':
        dispatch_photo[m.chat.id] = None
        dispatch3(m)

    elif m.text == btn['to_beginning']:
        admin.menu.menu(m)

    else:
        dispatch1(m)


def dispatch2(m):
    bot.send_message(m.chat.id, 'Прикрепи фотографию. Без подписи')
    bot.register_next_step_handler(m, dispatch2_definer)


def dispatch2_definer(m):
    if 'photo' in m.json.keys():
        dispatch_photo[m.chat.id] = m.json['photo'][-1]['file_id']
        bot.send_message(m.chat.id, '✓ Фотография сохранена')
        dispatch3(m)

    else:
        dispatch2(m)


def dispatch3(m):
    bot.send_message(m.chat.id, 'Напишите текст рассылки:')
    bot.register_next_step_handler(m, dispatch3_definer)


def dispatch3_definer(m):
    dispatch_text[m.chat.id] = m.text
    kb = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    kb.add('Да', 'Нет', btn['to_beginning'])
    bot.send_message(
        chat_id=m.chat.id,
        text="<b>" + m.text + "</b>\nВсе верно?",
        reply_markup=kb,
        parse_mode='html'
    )
    bot.register_next_step_handler(m, dispatch3_postdefiner)


def dispatch3_postdefiner(m):

    if m.text == 'Да':
        with back.tools.DBConnection(config.settings.database_url) as con:
            curs = con.cursor()
            curs.execute('select id from users where subscribed = true')
            fetch = [id_[0] for id_ in curs.fetchall()]
        sent_amount = 0

        for id_ in fetch:
            try:
                if dispatch_photo[m.chat.id] is not None:
                    if len(dispatch_text[m.chat.id]) < 200:
                        bot.send_photo(
                            chat_id=id_,
                            photo=dispatch_photo[m.chat.id],
                            caption=dispatch_text[m.chat.id],
                        )
                    else:
                        bot.send_photo(
                            chat_id=id_,
                            photo=dispatch_photo[m.chat.id]
                        )
                        bot.send_message(id_, dispatch_text[m.chat.id])
                else:
                    bot.send_message(id_, dispatch_text[m.chat.id])
            finally:
                sent_amount += 1

        bot.send_message(m.chat.id, "Рассылка  завершена. Её получили " + str(sent_amount) + " пользователей")
        admin.menu.menu(m)

    elif m.text == btn['to_beginning']:
        admin.menu.menu(m)

    else:
        dispatch3(m)
