# скорее всего это потом станет прогой
import requests
from bs4 import BeautifulSoup as bs
import urllib.request
import openpyxl
import telebot
import sqlite3
from sqlite3 import Error
import os
url='https://ba.hse.ru/base2023'
def get_statistic():
    response = requests.get(url)
    soup = bs(response.text, 'lxml')

    blocks = soup.find_all('div', class_='builder-section foldable_block')

    msk_info = blocks[0]
    info_all_link = msk_info.find_all('a')[0].get('href')
    urllib.request.urlretrieve(info_all_link, "statistic.xlsx")
def find_program_list(need_find="Прикладная математика и информатика"):
    response = requests.get(url)
    soup = bs(response.text, 'lxml')

    blocks = soup.find_all('div', class_='builder-section foldable_block')

    msk_info = blocks[0]
    program_info = []
    for link in msk_info.find_all('tr'):
        program_info.append(link)


    for i in range(len(program_info)):
        name=program_info[i].find_all('td')[0].text
        if (name == need_find):
            link=program_info[i].find_all('td')[1].find_all('a')[0].get('href')
            urllib.request.urlretrieve(link, "list_abi.xlsx")
            break
#начинаем обработку xlsx файлов
def iter_rows(ws):
    for row in ws.iter_rows():
        yield [cell.value for cell in row]
def get_info_statistic(path, target="Прикладная математика и информатика"):
    wb_obj = openpyxl.load_workbook(path)
    ws=wb_obj.active
    for merge in list(ws.merged_cells):
        ws.unmerge_cells(range_string=str(merge))
    res=list(iter_rows(ws))
    #print(res)
    titles=res[6]
    res_mes=""
    for row in res:
        if (row[1]==target):
            #print(res[3][0])
            res_mes=res_mes+res[3][0]+'\n'
            #print(res[6][10])
            res_mes = res_mes + res[6][10] + '\n'
            #print(row[10])
            res_mes = res_mes + row[10] + '\n'
            #print(res[6][14][8:])
            res_mes = res_mes + res[6][14][8:] + '\n'
            #print(row[14])
            res_mes = res_mes + row[14] + '\n'
            return res_mes
def get_place(path, snils):
    wb_obj = openpyxl.load_workbook(path)
    ws = wb_obj.active
    res_mes=""
    for merge in list(ws.merged_cells):
        ws.unmerge_cells(range_string=str(merge))
    res = list(iter_rows(ws))
    for row in res:
        if (row[2]==snils):
            #print(res[9][2])
            res_mes=res_mes+res[9][2]+'\n'
            #print()
            res_mes=res_mes+"Место в списке абитуриентов  {0} :  {1}".format(res[1][2], row[0])+'\n'
            return res_mes
def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection
def execute_query(query):
    connection = create_connection("users.db")
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")
    cursor.close()
    connection.close()
create_users_table = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  Snils TEXT
);
"""

create_users = """
INSERT INTO
  users (name, Snils)
VALUES
  (?, ?);
"""
def add_users(chat_id, snils):
    connection = create_connection("users.db")
    data_tuple=(chat_id,snils)
    cursor = connection.cursor()
    try:
        cursor.execute(create_users, data_tuple)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")
    cursor.close()
    connection.close()
def check_exists_db(chat_id):
    connection = create_connection("users.db")
    curs=connection.cursor()
    info = curs.execute('SELECT * FROM users WHERE name=?', (chat_id,)).fetchone()
    if info:
        connection.close()
        return True
    else:
        connection.close()
        return False
def get_from_table(chat_id, pos):
    connection = create_connection("users.db")
    curs = connection.cursor()
    info = curs.execute('SELECT * FROM users WHERE name=?', (chat_id,)).fetchone()
    connection.close()
    return info[pos]
API_KEY="6327868399:AAGeN0lxgMjCpkJEohSFL4vYJTyOf8frMEc"
bot=telebot.TeleBot(API_KEY)
@bot.message_handler(commands=['start'])
def hello(message):
    bot.send_message(message.chat.id,"Запуск произведен для пользователя {0}".format(message.chat.id))
    if not(check_exists_db(message.chat.id)):
        bot.send_message(message.chat.id, "Отправьте свой номер СНИЛС в формате XXX-XXX-XXX XX")
        bot.register_next_step_handler(message, add_user)
def add_user(message):
    add_users(message.chat.id,message.text)
    print("Done adding")
@bot.message_handler(commands=['place'])
def get_place_pos(message):
    print("place_request_open")
    snils=get_from_table(message.chat.id, 2)
    find_program_list("Прикладная математика и информатика")
    res = get_place("list_abi.xlsx", snils)
    bot.send_message(message.chat.id, res)
    os.remove("list_abi.xlsx")
    print("place_request_close")
@bot.message_handler(commands=['statistic'])
def get_statistic_b(message):
    print("statistic_request_open")
    get_statistic()
    res = get_info_statistic("statistic.xlsx","Прикладная математика и информатика")
    bot.send_message(message.chat.id, res)
    os.remove("statistic.xlsx")
    print("statistic_request_close")
execute_query(create_users_table) #надо же сделать таблицу
#get_from_table("855175110")
#add_users(connection,"1","168-186")
#print(check_exists_db(connection, "1"))
bot.polling()