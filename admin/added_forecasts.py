import telebot
import back.tools
import admin.menu

bot = back.tools.bot


def added_forecasts1(m):
    forecasts = back.tools.get('forecasts')
    for forecast in forecasts:
        back.tools.report(send_forecast=forecast)
        if forecast['date'] is None:
            back.tools.delete(forecast['id'], 'forecasts')
        else:
            kb = telebot.types.InlineKeyboardMarkup()
            button_delete = telebot.types.InlineKeyboardButton(
                text="Удалить прогноз",
                callback_data='dl'+str(forecast['id'])
            )
            kb.add(button_delete)

            text = f"<b>Будет отправлен {forecast['date']}\n" \
                   f"Текст:</b> {forecast['text']}"
            bot.send_message(m.chat.id, text, parse_mode='html', reply_markup=kb)
    admin.menu.menu(m)


@bot.callback_query_handler(func=lambda query: query.data[0:2] == 'dl')
def delete_forecast(query):
    data = query.data
    back.tools.report(action='delete forecast', query_data=data)
    forecast_id = ''.join(list(data)[2:len(data)])
    back.tools.delete(forecast_id, 'forecasts')
    bot.edit_message_text(
        text=f"<b>✓ Прогноз удалён</b>",
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        parse_mode='html'
    )
