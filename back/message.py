import telebot
import threading

import back

from config.messages import msg
from back.tools import report

sent_dict = {}

bot = back.tools.bot


class Msg:
    def __init__(self,
                 msg_title
                 ):
        assert msg_title in msg.keys()

        self.msg_title = msg_title
        self.text = msg[msg_title]['text']
        # self.text = self.text[0]
        self.buttons = msg[msg_title]['buttons']
        self.link = msg[msg_title]['link']
        if self.link != '':
            link_place = self.text.find('link')
            self.text = self.text[:link_place] + \
                        f'👉👉<a href="{self.link}">Жми "Посмотреть"</a>👈👈' + \
                        self.text[link_place+4:]

    def send(self, chat_id, previous_msg_title=None, notify=False, next_step=None):
        check_previous_msg = True

        if self.msg_title == 'msg3':
            back.tools.set_(chat_id, 'users', 'video1', True)
        if self.msg_title == 'msg4':
            back.tools.set_(chat_id, 'users', 'video2', True)
        if self.msg_title == 'msg5':
            back.tools.set_(chat_id, 'users', 'video3', True)

        if previous_msg_title is None:
            previous_msg_title = []
        if len(previous_msg_title) > 0:
            if sent_dict[chat_id] not in previous_msg_title:
                check_previous_msg = False

        if check_previous_msg is True:
            keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
            for button in self.buttons:
                keyboard.add(button)
            try:
                sent = bot.send_message(chat_id=chat_id,
                                        text=self.text,
                                        disable_web_page_preview=False,
                                        reply_markup=keyboard,
                                        parse_mode='HTML',
                                        disable_notification=notify,
                                        )
                report(action='send_msg', msg=self.msg_title, send_text=True)
            except:
                assert False, f'tools.Msg.send("{self.msg_title}") error'

            # report(f'tools.Msg.send() {self.msg_title}')
            sent_dict[chat_id] = self.msg_title
            # report(f'tools.sent_dict changed to: {sent_dict[chat_id]}')
            if next_step is not None:
                try:
                    report(action='register_next_step', next_step=next_step)
                    bot.register_next_step_handler(sent, next_step)
                except:
                    assert False, 'tools.Msg.send(): next_step not registered'

    def postpone(self, chat_id, previous_msg_title, timer, next_step=None):
        report(action='postpone_message', msg=next_step, time=timer)
        timer_ = threading.Timer(interval=timer,
                                 function=self.send,
                                 args=[chat_id, previous_msg_title, True, next_step])
        timer_.start()
        return timer_
