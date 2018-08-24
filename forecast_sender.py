import time
import telebot
from back.tools import date, report, DBConnection, bot, get, set_
from config.settings import database_url


def poll():
    while True:
        current_time = time.strftime('%H:%M')
        report(current_time=current_time)
        mins = int(time.strftime('%M')) + 60 * int(time.strftime('%H'))

        if 21 * 60 + 30 < mins < 22 * 60 + 30:
            report(send_forecast=True)
            report(current_date=date(0))
            send_forecast(select_forecast(date(0)))

        time.sleep(10)


def select_forecast(date_):
    with DBConnection(database_url) as con:
        curs = con.cursor()
        curs.execute('select id from forecasts '
                     'where sent=false and date=%s', (date_,))
        fetch = curs.fetchone()

    if fetch is not None:
        report(forecast_id=fetch[0])
        return fetch[0]
    else:
        return 0


def send_forecast(forecast_id):
    if forecast_id == 0:
        return

    forecast_photo = get('forecasts', 'photo', forecast_id)
    forecast_text = f'<b>Прогноз на {date(0)}</b>\n' + get('forecasts', 'text', forecast_id)

    with DBConnection(database_url) as con:
        curs = con.cursor()
        curs.execute('select id from users where forecasts_left > 0')
        fetch = [chat_id[0] for chat_id in curs.fetchall()]

    sent_amount = 0
    not_sent = 0

    for chat_id in fetch:
        try:

            if forecast_photo is not None:
                if len(forecast_text) < 200:
                    bot.send_photo(chat_id, forecast_photo, caption=forecast_text, parse_mode='html')
                else:
                    bot.send_photo(chat_id, forecast_photo)
                    bot.send_message(chat_id, forecast_text, parse_mode='html')
            else:
                bot.send_message(chat_id, forecast_text, parse_mode='html')

            with DBConnection(database_url) as con:
                curs = con.cursor()
                curs.execute('update users set forecasts_left = forecasts_left-1 where id = %s', (chat_id,))

            sent_amount += 1

        except telebot.apihelper.ApiException:
            not_sent += 1

    report(sent_amount=sent_amount, not_sent=not_sent)
    set_(forecast_id, 'forecasts', 'sent', True)
    set_(forecast_id, 'forecasts', 'users_recieved', sent_amount)



