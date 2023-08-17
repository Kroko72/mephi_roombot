import sqlite3
from telegram.ext import CommandHandler
import telegram.ext


def start(update, conext):
    update.message.reply_text("Напишите /help")


def help(update, context):
    update.message.reply_text("""
    Пример использования команд:
    /your_room A000 номер_телефона - ввести номер вашей комнаты и номер телефона (формат номера - только цифры)
    /find_mates A000 - найти соседей по комнате
    """)


def your_room(update, context):
    global conn, cursor
    room = update.message.text.split()[1]
    tel = update.message.text.split()[2]
    print(room, tel)
    t = cursor.execute('''SELECT * from rooms''').fetchall()
    print(t)
    cursor.execute(f'''INSERT INTO rooms(room_id) VALUES('{room}')''')
    last_id = cursor.execute('''SELECT max(human_id) from rooms''').fetchone()[0]
    print(last_id)
    cursor.execute(f'''INSERT INTO peoples(human_id,teleg) VALUES('{last_id}','{tel}')''')
    conn.commit()
    update.message.reply_text("данные сохранены")


def find_mates(update, context):
    global conn, cursor
    find_by = update.message.text.split()[1]
    print(find_by)
    mates_id = ["'" + str(i[0]) + "'" for i in cursor.execute(f"""SELECT * FROM rooms WHERE room_id='{find_by}'""").fetchall()]
    print(mates_id)
    mates_amount = len(mates_id)
    req = " or human_id=".join(mates_id)
    print(req)
    mates = [i[1] for i in cursor.execute(f"""SELECT * FROM peoples WHERE human_id={req}""").fetchall()]
    print(mates)
    if len(mates) != 0:
        update.message.reply_text("Номера ваших сокамерников:")
        for i in mates:
            update.message.reply_text(i)
    else:
        update.message.reply_text("Сокамерников не найдено")


def main():
    global conn, cursor
    conn = sqlite3.connect("db/rooms.db", check_same_thread=False)
    cursor = conn.cursor()
    updater = telegram.ext.Updater("TOKEN")
    disp = updater.dispatcher
    disp.add_handler(CommandHandler('start', start))
    disp.add_handler(CommandHandler("help", help))
    disp.add_handler(CommandHandler("your_room", your_room))
    disp.add_handler(CommandHandler("find_mates", find_mates))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
