from urllib import parse
import psycopg2

url = parse.urlparse('postgres://wfgssloebauhqa:a5bf0147b20d9c1db13887a64877f2bdeac58014ade5aa78a076ad9816196b22@ec2-54-246-84-200.eu-west-1.compute.amazonaws.com:5432/d4388l3nkf43tn')
con = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

curs = con.cursor()
def create_users():
    curs.execute('''CREATE TABLE users 
    (id INTEGER,
     time INTEGER,
     video1 BOOL,
     video2 BOOL,
     video3 BOOL,
     question1 VARCHAR,
     question2 VARCHAR,
     question3 VARCHAR,
     payment VARCHAR,
     bets INTEGER,
     subscribed BOOL)''')
# create_users()
# curs.execute(f'''UPDATE users SET subscribed = {True}''')
curs.execute('DROP TABLE payments')
curs.execute('''CREATE TABLE payments 
(payment_id INTEGER, 
operation_id INTEGER,
price INTEGER,
chat_id INTEGER,
time INTEGER,
hash VARCHAR, 
success BOOL 
)''')
con.commit()
