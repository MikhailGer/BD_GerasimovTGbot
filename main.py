import asyncio

import logging

import config.config

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from routers import router as main_router


async def main():
    bot = Bot(token=config.config.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(main_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


#     db = DB.DB()
#     print("There are ", db.user_counter(), " objects in DB")
#     print("commands: insert, select_all, get_object_by_id, get_object_by_age, delete_object_by_id, "
#           "get_object_by_username, change_username_by_id, backup")
#
#     while True:
#         command = input("input command: ")
#
#         if command == "insert":
#             username = input("input username: ")
#             email = input("input email: ")
#             age = int(input("input age: "))
#             db.db_insert(username, email, age)
#
#         elif command == "select_all":
#             db.db_select_all()
#
#         elif command == "backup":
#             db.backup()
#
#         elif command == "get_object_by_id":
#             id = int(input("input id: "))
#             db.get_object_by_id(id)
#
#         elif command == "get_object_by_age":
#             age = int(input("input age: "))
#             db.get_object_by_age(age)
#
#         elif command == "get_object_by_username":
#             username = input("input username: ")
#             db.get_object_by_username(username)
#
#         #удаление юзера по id
#         elif command == "delete_object_by_id":
#             while True:
#                 id = input("input id: ")
#                 test = db.get_object_by_id(id)
#                 if len(test) != 0:
#                         confirmation = False
#                         confirmation = input("Confirm user deletion: yes/no ")
#                         if confirmation == 'yes':
#                             db.delete_object_by_id(id)
#                             break
#                         elif confirmation == 'no':
#                             break
#                         else:
#                             print("unknown command")
#                 elif id == "back":
#                     break
#                 else:
#                     print("user not found, try again, or type back")
#
#        #изменение имени по id
#         elif command == "change_username_by_id":
#             while True:
#                 id = input("input id: ")
#                 test = db.get_object_by_id(id)
#                 if len(test) != 0:
#                     confirmation = False
#                     confirmation = input("Confirm changing username: yes/no ")
#                     if confirmation == 'yes':
#                         db.change_username_by_id(id)
#                         break
#                     elif confirmation == 'no':
#                         break
#                     else:
#                         print("unknown command")
#
#                 elif id == "back":
#                     break
#                 else:
#                     print("user not found, try again, or type back")
#
#         else:
#             print("unknown commad")
#
#
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
