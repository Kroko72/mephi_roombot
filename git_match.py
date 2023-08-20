import sqlite3
from telegram.ext import CommandHandler
import telegram.ext


def help(update, context) -> None:
    update.message.reply_text("""
    Сначала заполняем данные о себе (используем команду your_room), потом ищем сокамерников (используем команду find_mates)
    
    Вместо номера телефона (ниже инструкция по использованию команд) можно ввести свой телеграм, но лучше номер
    
    Возможно, ваш сосед по комнате написал в номере комнаты букву на другом языке или написал её маленькой или большой, проверяйте это
    
    По вопросам писать в телеграмм @Therealkroko
    
    Инструкция по использованию:
    предположим вы живёте в комнате номер A000, корпуса 0, а ваш номер телефона 89991231231.
    Тогда вы, чтобы заполнить данные о себе, должны написать команду /your_room A000 0 89991231231
    В этой команде сначала идёт номер комнаты, затем номер корпуса, а потом номер телефона. Вместо номера телефона можно оставлять свой телеграмм.
    После того, как вы заполнили данные о себе, попробуйте найти соседей по комнате. Вы должны быть одним из них. Если это не так, пишите в телеграмм @Therealkroko
    Чтобы найти соседей по комнате, вы должны написать команду /find_mates A000 0
    В этой команде сначала идёт номер комнаты, затем номер корпуса.
    
    Учтите, что номер корпуса - это не то, что написано в адресе общежития, а то, какой номер корпуса у вашего общежития. Например у нового общежития 9 корпус.
    """)


def start(update, context) -> None:
    update.message.reply_text("напишите /help")


def your_room(update, context) -> None:
    global conn, cursor
    try:
        room = update.message.text.split()[1]
        building = update.message.text.split()[2]
        tel = update.message.text.split()[3]
        # print(room, tel)
        t = cursor.execute('''SELECT * from rooms''').fetchall()
        # print(t)
        cursor.execute(f'''INSERT INTO rooms(room_id,building) VALUES('{room}','{building}')''')
        last_id = cursor.execute('''SELECT max(human_id) from rooms''').fetchone()[0]
        # print(last_id)
        cursor.execute(f'''INSERT INTO peoples(human_id,teleg) VALUES('{last_id}','{tel}')''')
        print(room, building, tel, last_id, "\n")
        print(t, "\n")
        conn.commit()
        update.message.reply_text("данные сохранены")
    except Exception:
        update.message.reply_text("Проверьте правильность введённой команды. Для справки напишите /help")


def find_mates(update, context) -> None:
    global conn, cursor
    try:
        find_by = update.message.text.split()[1]
        in_building = update.message.text.split()[2]
        print("find-by:", find_by, in_building)
        mates_id = ["'" + str(i[0]) + "'" for i in cursor.execute(
            f"""SELECT * FROM rooms WHERE room_id='{find_by}' AND building='{in_building}'""").fetchall()]
        print("find-mates_id:", mates_id)
        if len(mates_id) != 0:  # если не нашёл соседей
            req = " or human_id=".join(mates_id)
            print("find-req:", req)
            mates = [i[1] for i in cursor.execute(f"""SELECT * FROM peoples WHERE human_id={req}""").fetchall()]
            print("find-mates:", mates)
            if len(mates) != 0:
                update.message.reply_text("Контакты ваших сокамерников:")
                for i in mates:
                    update.message.reply_text(i)
        else:
            update.message.reply_text("Сокамерников не найдено")
    except Exception:
        update.message.reply_text("Проверьте правильность введённой команды. Для справки напишите /help")


def main() -> None:
    global conn, cursor
    conn = sqlite3.connect("db/git_rooms.db", check_same_thread=False)
    cursor = conn.cursor()
    updater = telegram.ext.Updater("Token")
    disp = updater.dispatcher
    disp.add_handler(CommandHandler("start", start))
    disp.add_handler(CommandHandler("help", help))
    disp.add_handler(CommandHandler("your_room", your_room))
    disp.add_handler(CommandHandler("find_mates", find_mates))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
