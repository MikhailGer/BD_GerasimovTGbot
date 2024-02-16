import datetime
import aiosqlite
import asyncio
import os
from config.config import get_DATABASE_FILE

async def connect_DB():
    async with DB(await get_DATABASE_FILE()) as connection:
        await connection.db.execute('''CREATE TABLE IF NOT EXISTS Users (id INTEGER PRIMARY KEY,username TEXT NOT NULL,email TEXT
        NOT NULL,age INTEGER)''')
        await connection.db.commit()
        print('Connected')
        return connection.db


async def list_files_in_directory_data(directory):
    files = []
    for file in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, file)):
            files.append(file)
    return files


class DB:
    def __init__(self, db_file):
        self.db_file = db_file
        self.lock = asyncio.Lock()

    async def __aenter__(self):
        self.db = await aiosqlite.connect(self.db_file)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.db.close()

    # создание файла бэкапа бд с привязкой названия файла к текущему времени
    async def backup(self):
        current_datetime = datetime.datetime.now()
        current_datetime_str = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
        async with DB(f'data\my_database_backup_{current_datetime_str}.db') as connection_backup:
            async with self.lock:
                async with self.db.execute('SELECT id, username, email, age FROM Users') as cursor:
                    async with connection_backup.db.execute('''CREATE TABLE Users (id INTEGER PRIMARY KEY,username TEXT NOT NULL,email TEXT
                    NOT NULL,age INTEGER)''') as cursor_backup:
                        result_data = []
                        data = await cursor.fetchall()
                        for user in data:
                            result_data.append({
                                "id": user[0], "username": user[1], "email": user[2], "age": user[3], })
                            sql = 'INSERT INTO Users (id, username, email, age) VALUES (?, ?, ?, ?)'
                            await cursor_backup.execute(sql, (user[0], user[1], user[2], user[3]))
                        print('Backup completed successfully!')
                        await connection_backup.db.commit()
                        return True

    # все имена трансформируются с помощю lower() для поиска по одному и тому же имени
    async def db_insert(self, id, username, email, age):
        async with self.db.execute('INSERT INTO Users (id, username, email, age) VALUES (?, ?, ?, ?)',
                                   (id, username.lower(), email, age)) as cursor:
            await self.db.commit()

    async def user_counter(self):
        async with self.db.execute('SELECT COUNT(*) FROM Users') as cursor:
            total_users = await cursor.fetchone()
            total_users = total_users[0]
            return total_users

    async def user_counter_age(self, age):
        async with self.db.execute('SELECT COUNT(*) FROM Users WHERE age = ?', (age,)) as cursor:
            total_users = await cursor.fetchone()
            total_users = total_users[0]
            return total_users

    async def user_counter_username(self, username):
        async with self.db.execute('SELECT COUNT(*) FROM Users WHERE username = ?', (username,)) as cursor:
            total_users = await cursor.fetchone()
            total_users = total_users[0]
            return total_users

    async def db_select_all(self):
        async with self.db.execute('SELECT * FROM Users') as cursor:
            users = await cursor.fetchall()
            mas = []
            result = ''
            for user in users:
                mas.append(user)
            result = ("\n".join(map(str, mas)))
            return result

    async def get_object_by_id(self, id):
        result_data = dict()
        async with self.db.execute('SELECT id, username, email, age FROM Users WHERE id = ?', (id,)) as cursor:
            data = await cursor.fetchone()
            if data:
                result_data = {
                    "id": data[0], "username": data[1], "email": data[2], "age": data[3], }

            return str(result_data)

    async def get_object_by_age(self, age):
        # result_data = []
        result_data = ''
        async with self.db.execute('SELECT id, username, email, age FROM Users WHERE age = ?', (age,)) as cursor:
            data = await cursor.fetchall()
            # for user in data:
            #     result_data.append({
            #         "id": user[0], "username": user[1], "email": user[2], "age": user[3], })
            # return str(result_data)
            for user in data:
                result_data += f"id: {user[0]}, username: {user[1]}, email: {user[2]}, age: {user[3]}"
                result_data += "\n"
                result_data += "----------"
                result_data += "\n"

            return result_data

    # все имена в БД в нижнем регистре, поиск ведется в нижнем регистре

    # реализация гет бай юзернейма через f строку
    async def get_object_by_username(self, username):
        # result_data = []
        result_data = ''
        async with self.db.execute('SELECT id, username, email, age FROM Users WHERE username = ?',
                                   (username.lower(),)) as cursor:
            data = await cursor.fetchall()
            # for user in data:
            #     result_data.append({
            #         "id": user[0], "username": user[1], "email": user[2], "age": user[3], })
            for user in data:
                result_data += f"id: {user[0]}, username: {user[1]}, email: {user[2]}, age: {user[3]}"
                result_data += "\n"
                result_data += "----------"
                result_data += "\n"

            return result_data

    async def delete_object_by_id(self, id):
        try:
            async with self.db.execute('DELETE FROM Users WHERE id = ?', (id,)) as cursor:
                await self.db.commit()
                return True
        except:
            return False

    async def change_object_by_id(self, id, username, email, age):
        async with self.db.execute('UPDATE Users SET username = ?, email = ?, age = ? WHERE id = ?',
                                   (username, email, age, id,)) as cursor:
            await self.db.commit()
            # result = []
            result_data = ''
            sql_select = 'SELECT * FROM Users WHERE id = ?'
            await cursor.execute(sql_select, (id,))
            data = await cursor.fetchall()
            # for user in data:
            #     result_data.append({
            #         "id": user[0], "username": user[1], "email": user[2], "age": user[3], })
            # return str(result_data)
            for user in data:
                result_data += f"id: {user[0]}, username: {user[1]}, email: {user[2]}, age: {user[3]}"
                result_data += "\n"
                result_data += "----------"
                result_data += "\n"
            return result_data

    # очистка БД от данных
    async def db_kill(self):
        async with self.db.execute('DELETE FROM Users') as cursor:
            print("DB_cleared")
            await self.db.commit()
