import random
import back.tools
from _md5 import md5
import config.settings


con = back.tools.con

# {
#     payment_id: int
#     operation_id: int
#     price: int
#     chat_id: int
#     time: int
#     hash: varchar
#     success: bool
# }


def generate_link(chat_id, price):
    print('generate_link')

    while True:
        payment_id = random.randint(10000, 99999)
        if back.tools.get('payments', id_=payment_id) is None:
            break

    hash_ = generate_hash(price, payment_id)

    with back.tools.DBConnection(config.settings.database_url) as con:
        curs = con.cursor()
        curs.execute(f'''INSERT INTO payments (id, price, chat_id, hash) VALUES ({payment_id}, {price}, {chat_id}, '{hash_}')''')
        curs.execute(f'UPDATE users SET payment_id = array_append(payment_id, {payment_id}) where id = {chat_id}')

    print('generate_link', 'm.chat.id', chat_id, 'payment_id', payment_id)

    link = f'{config.settings.payment_link}m={config.settings.shop_id}&oa={price}&o={payment_id}' \
           f'&s={hash_}&us_chat_id={chat_id}&lang=ru&i=&em='
    return link


def generate_hash(price, payment_id):
    # ID Вашего магазина:Сумма платежа:Секретное слово:Номер заказа
    hash_ = md5(f"{config.settings.shop_id}:{price}:{config.settings.secret}:{payment_id}".encode('utf-8')).hexdigest()
    return hash_
