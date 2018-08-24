import telebot
import back
import config

from config.buttons import btn
from back.message import Msg

con = back.tools.con

bot = back.tools.bot


class Admin:
    def __init__(self, chat_id):
        self.chat_id = chat_id

    def user_amount(self):
        curs = con.cursor()
        curs.execute('SELECT FROM users')
        results = curs.fetchall()
        bot.send_message(self.chat_id, len(results))

    def unsubscribed_users(self):
        curs = con.cursor()
        curs.execute(f'SELECT FROM users WHERE subscribed = false')
        results = curs.fetchall()
        bot.send_message(self.chat_id, len(results))

    def dispatch(self):
        curs = con.cursor()
        curs.execute(f'SELECT id FROM users WHERE subscribed = true')
        results = curs.fetchall()[0]
        for id_ in results:
            if dispatch_photo_dict[self.chat_id] != '':
                bot.send_photo(id_, dispatch_photo_dict[self.chat_id])
                bot.send_message(id_, dispatch_text_dict[self.chat_id])
            else:
                bot.send_message(id_, dispatch_text_dict[self.chat_id])

        dispatch_photo_dict[self.chat_id] = ''
        dispatch_text_dict[self.chat_id] = ''


dispatch_photo_dict = {}
dispatch_text_dict = {}
direct_message_dict = {}


def admin_menu(m):
    if m.chat.id in config.settings.admins:
        Msg('admin').send(m.chat.id, next_step=admin_definer)


def admin_definer(m):
    if m.text == btn['user amount']:
        Admin(m.chat.id).user_amount()
        admin_menu(m)
    elif m.text == btn['unsubscribed users']:
        Admin(m.chat.id).unsubscribed_users()
        admin_menu(m)
    elif m.text == btn['direct message']:
        bot.send_message(m.chat.id, 'Введите chat_id')
        direct_message1(m)
    elif m.text == btn['dispatch']:
        kb = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        dispatch_text_dict[m.chat.id] = ''
        dispatch_photo_dict[m.chat.id] = ''
        kb.add(btn['no'])
        bot.send_message(m.chat.id, 'Если нужно - отправьте фото, если нет - нажмите "нет"', reply_markup=kb)
        bot.register_next_step_handler(m, dispatch1)


def direct_message1(m):
    direct_message_dict[m.chat.id] = m.text
    bot.send_message(m.chat.id, 'Введите текст')
    bot.register_next_step_handler(m, direct_message2)


def direct_message2(m):
    bot.send_message(direct_message_dict[m.chat.id], m.text)
    bot.send_message(m.chat.id, f'Отправлено сообщение с текстом {m.text} на chat_id {direct_message_dict[m.chat.id]}')
    admin_menu(m)


def dispatch1(m):
    if m.photo == None and m.text != btn['no']:
        kb = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        kb.add(btn['no'])
        bot.send_message(m.chat.id, 'Если нужно - отправьте фото, если нет - нажмите "нет"', reply_markup=kb)
        bot.register_next_step_handler(m, dispatch1)
    else:
        if m.photo is not None:
            dispatch_photo_dict[m.chat.id] = m.photo[0].file_id
        bot.send_message(m.chat.id, 'Отправьте текст рассылки')
        bot.register_next_step_handler(m, dispatch2)


def dispatch2(m):
    dispatch_text_dict[m.chat.id] = m.text
    kb = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    kb.add(btn['admit'])
    kb.add(btn['decline'])
    try:
        bot.send_photo(m.chat.id, dispatch_photo_dict[m.chat.id])
        bot.send_message(m.chat.id, dispatch_text_dict[m.chat.id] + '\n\nТак будет выглядеть рассылка', reply_markup=kb)
    except:
        bot.send_message(m.chat.id, dispatch_text_dict[m.chat.id] + '\n\nТак будет выглядеть рассылка', reply_markup=kb)
    bot.register_next_step_handler(m, dispatch3)


def dispatch3(m):
    if m.text == btn['admit']:
        Admin(m.chat.id).dispatch()
    if m.text == btn['decline']:
        Msg('admin').send(m.chat.id)
