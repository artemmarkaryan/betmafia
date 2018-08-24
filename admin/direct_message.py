import telebot
import back.tools
import admin.menu

bot = back.tools.bot


dm_chat_id = {}
dm_text = {}


def dm1(m):
    bot.send_message(m.chat.id, "Введи chat id:")
    bot.register_next_step_handler(m, dm1_definer)


def dm1_definer(m):
    if m.text.isdigit():
        dm_chat_id[m.chat.id] = m.text
        kb = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        kb.add('Да', 'Нет')
        bot.send_message(
            chat_id=m.chat.id,
            text="<b>" + m.text + "</b>" + " - нужный chat id.\nВсе верно?",
            reply_markup=kb,
            parse_mode='html'
        )
        bot.register_next_step_handler(m, dm1_postdefiner)
    else:
        bot.send_message(m.chat.id, 'chat id содержит только цифры')
        dm1(m)


def dm1_postdefiner(m):
    if m.text == 'Да':
        dm2(m)

    elif m.text == 'Нет':
        dm1(m)

    else:
        kb = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        kb.add('Да', 'Нет')
        bot.send_message(
            chat_id=m.chat.id,
            text="<b>" + dm_chat_id[m.chat.id] + "</b>" + " - нужный chat id.\nDct верно?",
            reply_markup=kb,
            parse_mode='html'
        )
        bot.register_next_step_handler(m, dm1_postdefiner)


def dm2(m):
    bot.send_message(m.chat.id, "Введи текст сообщения:")
    bot.register_next_step_handler(m, dm2_definer)


def dm2_definer(m):
    dm_text[m.chat.id] = m.text
    kb = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    kb.add('Да', 'Нет')
    bot.send_message(
        chat_id=m.chat.id,
        text="<b>" + m.text + "</b>\nВсе верно?",
        reply_markup=kb,
        parse_mode='html'
    )
    bot.register_next_step_handler(m, dm2_postdefiner)


def dm2_postdefiner(m):
    if m.text == 'Да':
        try:
            bot.send_message(dm_chat_id[m.chat.id], dm_text[m.chat.id], parse_mode='html')
            bot.send_message(m.chat.id, f"<b>✓</b> Сообщение с текстом <b>'{dm_text[m.chat.id]}'</b> "
                                        f"отправлено пользователю <b>{dm_chat_id[m.chat.id]}</b>", parse_mode='html')
        except telebot.apihelper.ApiException:
            bot.send_message(m.chat.id,
                             f"<b>✕</b> Сообщение <b>не отправлено</b> пользователю "
                             f"<b>{dm_chat_id[m.chat.id]}</b>. Скорее всего, он забанил бота",
                             parse_mode='html')
        finally:
            admin.menu.menu(m)

    elif m.text == 'Нет':
        dm2(m)

    else:
        kb = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        kb.add('Да', 'Нет')
        bot.send_message(
            chat_id=m.chat.id,
            text="<b>" + dm_text[m.chat.id] + "</b>\nВсе верно?",
            reply_markup=kb,
            parse_mode='html'
        )
        bot.register_next_step_handler(m, dm2_postdefiner)
