import telebot
import threading
import back.tools
from back.tools import report
import back.payment
import admin.menu
import config.settings
from config.buttons import btn
from back.message import Msg
import forecast_sender

bot = back.tools.bot

fc_sender = threading.Thread(target=forecast_sender.poll)

timers = []


def null_func():
    pass


@bot.message_handler(regexp=btn['unsubscribe'])
def unsubscribe(m):
    print('m.chat.id', m.chat.id, 'unsubscribed')
    back.tools.set_(m.chat.id, 'users', 'subscribed', False)
    bot.send_message(m.chat.id, '✓ Подписка отменена')


@bot.message_handler(commands=['admin'])
def admin_(m):
    admin.menu.menu(m)


last_action = {}


@bot.message_handler(commands=['start'])
def msg2(m):
    report(action='start', chat_id=m.chat.id)

    if m.chat.id in config.settings.admins:
        admin.menu.menu(m)
        return

    if m.chat.id in last_action.keys() and last_action[m.chat.id] == 'start':
        return

    if back.tools.get('users', id_=m.chat.id) is None:
        back.tools.add_user(m.chat.id)
    else:
        Msg('msg_start_again').send(m.chat.id)
        return

    last_action[m.chat.id] = 'start'

    Msg('msg2').send(m.chat.id)
    timers.append(Msg('msg3').postpone(m.chat.id, ['msg2', ], timer=10))
    timers.append(Msg('msg6').postpone(m.chat.id, ['msg3', ], timer=600))
    timers.append(Msg('msg4').postpone(m.chat.id, ['msg3', 'msg6'], timer=24 * 3600))
    timers.append(Msg('msg5').postpone(m.chat.id, ['msg4', ], timer=2 * 24 * 3600))
    timers.append(Msg('msg7').postpone(m.chat.id, ['msg5', ], timer=2 * 24 * 3600 + 300))


# Опрос и переход на отработку
@bot.message_handler(regexp=btn['survey'])
def survey1(m):

    for timer in timers:
        report(action='cancel timer', timer=timer.name)
        timer.cancel()

    Msg('msg12').send(m.chat.id, next_step=survey1_definer)
    timers.append(Msg('msg10').postpone(m.chat.id, ['msg12', ], timer=300))
    timers.append(Msg('msg_payment').postpone(m.chat.id, ['msg10'], timer=24 * 3600))


def survey1_definer(m):

    for timer in timers:
        report(action='cancel timer', timer=timer.name)
        timer.cancel()

    if m.text == 'Да':
        back.tools.set_(m.chat.id, 'users', 'question1', True)
        Msg('msg13').send(m.chat.id, next_step=survey2_definer)

    elif m.text == 'Нет':
        back.tools.set_(m.chat.id, 'users', 'question1', False)
        Msg('msg13').send(m.chat.id, next_step=survey2_definer)

    else:
        Msg('msg12').send(m.chat.id, next_step=survey1_definer)


def survey2_definer(m):

    if m.text == 'Да':
        back.tools.set_(m.chat.id, 'users', 'question2', True)
        Msg('msg14').send(m.chat.id, next_step=survey3_definer)

    elif m.text == 'Нет':
        back.tools.set_(m.chat.id, 'users', 'question2', False)
        Msg('msg14').send(m.chat.id, next_step=survey3_definer)

    else:
        Msg('msg13').send(m.chat.id, next_step=survey2_definer)


def survey3_definer(m):
    if m.text == 'Да':
        back.tools.set_(m.chat.id, 'users', 'question2', True)
    elif m.text == 'Нет':
        back.tools.set_(m.chat.id, 'users', 'question2', False)
    else:
        Msg('msg14').send(m.chat.id, next_step=survey3_definer)

    if back.tools.get('users', 'question1', m.chat.id):
        Msg('msg15').send(m.chat.id)

    else:
        Msg('msg16').send(m.chat.id)
        Msg('msg17').postpone(chat_id=m.chat.id,
                              previous_msg_title=['msg16', 'msg16.1'],
                              timer=10)

    #     Зеленая и красная рамочка
    if not back.tools.get('users', 'video2', m.chat.id):
        timers.append(Msg('msg28').postpone(m.chat.id, ['msg15', 'msg17'], timer=24 * 3600))
        timers.append(Msg('msg29').postpone(m.chat.id, ['msg28'], timer=32 * 3600))
        timers.append(Msg('msg30').postpone(m.chat.id, ['msg15', 'msg17', ], timer=56 * 3600))
        timers.append(Msg('msg31').postpone(m.chat.id, ['msg30', ], timer=64 * 3600))
        timers.append(Msg('msg32').postpone(m.chat.id, ['msg31', ], timer=98 * 3600))
    timers.append(Msg('msg30').postpone(m.chat.id, ['msg15', 'msg17', ], timer=24 * 3600))
    timers.append(Msg('msg31').postpone(m.chat.id, ['msg30', ], timer=32 * 3600))
    timers.append(Msg('msg32').postpone(m.chat.id, ['msg31', ], timer=48 * 3600))


@bot.message_handler(regexp=btn['details'])
def starter(m):
    if m.chat.id in last_action.keys() and last_action[m.chat.id] == 'details':
            return
    else:
        last_action[m.chat.id] = 'details'
        payment(m)


@bot.message_handler(regexp=btn['buy forecast'])
def starter_(m):
    for timer in timers:
        report(action='cancel timer', timer=timer.name)
        timer.cancel()

    if m.chat.id in last_action.keys() and last_action[m.chat.id] == 'buy forecast':
        return
    else:
        last_action[m.chat.id] = 'buy forecast'
        payment(m)


@bot.message_handler(regexp=btn['yes'])
def msg_7_10_yes(m):
    if back.message.sent_dict[m.chat.id] == 'msg7':
        survey1(m)

    if back.message.sent_dict[m.chat.id] == 'msg10':
        Msg('msg17').send(m.chat.id)


# msg 7,10 -> no
@bot.message_handler(regexp=btn['no'])
def msg_7_10_no(m):
    if back.message.sent_dict[m.chat.id] == 'msg7' or back.message.sent_dict[m.chat.id] == 'msg10':
        Msg('msg9').send(m.chat.id, next_step=complaint)


def complaint(m):
    if len(m.text) < 5:
        Msg('msg9').send(m.chat.id, next_step=complaint)


@bot.message_handler(regexp=btn['pay1500'])  # Оплатить 1500 РУБ
def upsell(m):

    if m.chat.id in last_action.keys() and last_action[m.chat.id] == 'pay1500':
        return
    else:
        last_action[m.chat.id] = 'pay1500'

        back.tools.delete(m.chat.id, 'users', 'payment_id')

        btn1500 = telebot.types.InlineKeyboardButton(text='Оплатить только VIP 1500 руб.',
                                                     url=back.payment.generate_link(m.chat.id, 1500),
                                                     )
        btn2200 = telebot.types.InlineKeyboardButton(text='Оплатить 2 прогноза 2200 руб.',
                                                     url=back.payment.generate_link(m.chat.id, 2200),
                                                     )
        inline_markup_ = telebot.types.InlineKeyboardMarkup(row_width=1)
        inline_markup_.add(btn1500, btn2200)
        bot.send_message(m.chat.id,
                         text='''
👍🏻 <b>Отлично! Ваш VIP прогноз уже в корзине</b>
На сегодня есть ещё уверенные прогнозы. Сейчас вы можете докупить ещё один прогноз к вашему с большой скидкой!
Итого: 1500+700(вместо 1500)=2200 р.
''',
                         reply_markup=inline_markup_,
                         parse_mode='HTML',
                         disable_notification=True)
        done_payment(m)


def done_payment(m):
    kb = telebot.types.InlineKeyboardMarkup()
    btn_agree = telebot.types.InlineKeyboardButton(
        text='Я оплатил',
        callback_data='p'+str(m.chat.id),
    )
    kb.add(btn_agree)

    text = 'После оплаты, пожалуйста, нажмите на кнопку внизу ↓'
    bot.send_message(m.chat.id, text, reply_markup=kb, parse_mode='html')


@bot.callback_query_handler(func=lambda query: ''.join(list(query.data)[0]) == 'p')
def payment_checker(query):
    data = query.data
    user_id = ''.join(list(data)[1:len(data)])

    payment_1500 = back.tools.get('users', 'payment_id', user_id)[0]
    payment_1500_status = back.tools.get('payments', 'success', payment_1500)
    report(action='check_payment', chat_id=query.message.chat.id, payment_1500=payment_1500_status)

    payment_2200 = back.tools.get('users', 'payment_id', user_id)[1]
    payment_2200_status = back.tools.get('payments', 'success', payment_2200)
    report(action='check_payment', chat_id=query.message.chat.id, payment_2200=payment_2200_status)
    try:

        if payment_1500_status is None and payment_2200_status is None:

            kb = telebot.types.InlineKeyboardMarkup()
            btn_agree = telebot.types.InlineKeyboardButton(
                text='Я оплатил',
                callback_data='p' + str(query.message.chat.id),
            )
            kb.add(btn_agree)
            text = '<b>✕ Платежа не существует.</b>\nНажмите на одну из кнопок в сообщении выше'
            bot.edit_message_text(
                text,
                chat_id=query.message.chat.id,
                message_id=query.message.message_id,
                reply_markup=kb,
                parse_mode='html'
            )

        if payment_1500_status is False and payment_2200_status is False:
            kb = telebot.types.InlineKeyboardMarkup()
            btn_agree = telebot.types.InlineKeyboardButton(
                text='Я оплатил',
                callback_data='p' + str(query.message.chat.id),
            )
            kb.add(btn_agree)
            text = "<b>✕ Платёж не подтвержден.</b>\nПопробуйте еще раз через несколько минут. " \
                   "\nЕсли проблема повторится, пожалуйста, обратитесь в службу поддержки: @ник_поддержки"
            bot.edit_message_text(
                text,
                chat_id=query.message.chat.id,
                message_id=query.message.message_id,
                reply_markup=kb,
                parse_mode='html'
            )

        if payment_1500_status is True or payment_2200_status is True:
            text = "<b>✓ Платёж подтвержден.</b>\nПрогнозы рассылаются каждый день в 18:30. \nСкоро вы получите свой!" \
                   "\n\nЕсли вы не получили прогноз, пожалуйста, обратитесь в службу поддержки: @ник_поддержки"
            bot.edit_message_text(
                text,
                chat_id=query.message.chat.id,
                message_id=query.message.message_id,
                parse_mode='html'
            )
    except:
        pass


@bot.message_handler(regexp=btn['pay'])  # Оплатить, Купить прогноз
def payment(m):
    """
    реагирует на "Оплатить"
    отправляет кнопку "Оплатить 1500", "Отзывы"
    """
    for timer in timers:
            report(action='cancel timer', timer=timer.name)
            timer.cancel()

    if m.chat.id in last_action.keys() and last_action[m.chat.id] == 'pay':
        return
    else:
        last_action[m.chat.id] = 'pay'

        Msg('msg_payment').send(m.chat.id)
        Msg('msg21').postpone(m.chat.id, previous_msg_title=['msg_payment', ], timer=3600)
        Msg('msg22').postpone(m.chat.id, previous_msg_title=['msg21', ], timer=3*3600)


@bot.message_handler(regexp=btn['feedbacks']) # Отзывы
def feedback(m):
    last_action[m.chat.id] = 'feedbacks'
    Msg('msg_feedbacks').send(m.chat.id)
    payment(m)


@bot.message_handler(content_types=['text', 'photo'])
def a(m):
    if m.text in [
            btn['forecast'],
            btn['user amount'],
            btn['unsubscribed users'],
            btn['dispatch'],
            btn['direct message']
    ]:
        admin.menu.menu_definer(m)
    else:
        bot.send_message(m.chat.id, 'Что-то пошло не так. Попробуй заново')


bot.polling(interval=0.5, none_stop=False, timeout=120)
