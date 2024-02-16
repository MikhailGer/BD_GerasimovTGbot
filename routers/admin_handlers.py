from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from utils.states import *

from config.config import ADMIN_ID, get_DATABASE_FILE, admin_check, admin_delete, admin_clear

import aiofiles
import kb
from kb import create_keyboard

import text
import DB
from DB import connect_DB
from DB import list_files_in_directory_data

router = Router(name=__name__)


@router.message(Start_File_Inition.file)
async def file_inition(msg: Message, state: FSMContext):
    DB_file = msg.text.lower()
    directory = 'data'
    result = await list_files_in_directory_data(directory)
    if DB_file in result:
        await msg.answer("Database chosen")
        async with aiofiles.open('config/DATABASE_FILE.txt', 'w+') as f:
            await f.write('data/' + DB_file)
        async with DB.DB(await get_DATABASE_FILE()) as db:
            greet_counter = await db.user_counter()
            await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.admin_kb)
            await msg.answer(f"Objects in DB: {greet_counter}")
            await state.clear()
    else:
        await msg.answer("Database not found, try again")
        await state.set_state(Start_File_Inition.file)


@router.message(F.text, Command("back"))
async def start_handler(msg: Message, state: FSMContext):
    await state.clear()
    if await admin_check(msg.from_user.id):
        await msg.answer("Back in menu", reply_markup=kb.admin_kb)
    else:
        await msg.answer("Back in menu", reply_markup=kb.user_kb)


@router.message(Command("select_all"))
async def select_all_handler(msg: Message):
    if await get_DATABASE_FILE():
        if await admin_check(msg.from_user.id):
            async with DB.DB(await get_DATABASE_FILE()) as db:
                answer = await db.db_select_all()
                await msg.answer(answer)
    else:
        await msg.answer("Database hasn't been run yet, start it:", reply_markup=kb.start_kb)

@router.message(Command("insert"))
async def insert_handler(msg: Message, state: FSMContext):
    if await get_DATABASE_FILE():
        if await admin_check(msg.from_user.id):
            await msg.answer("Enter new id: ", reply_markup=kb.back_kb)
            await state.set_state(Inition.id)
    else:
        await msg.answer("Database hasn't been run yet, start it:", reply_markup=kb.start_kb)

@router.message(Inition.id)
async def form_id(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        await state.update_data(id=msg.text)
        await state.set_state(Inition.username)
        await msg.answer("Enter username: ", reply_markup=kb.back_kb)

    else:
        await msg.answer("Enter a digit", reply_markup=kb.back_kb)
        await Inition.id.set()


@router.message(Inition.username)
async def form_username(msg: Message, state: FSMContext):
    await state.update_data(username=msg.text)
    await state.set_state(Inition.email)
    await msg.answer("Enter email: ", reply_markup=kb.back_kb)


@router.message(Inition.email)
async def form_email(msg: Message, state: FSMContext):
    await state.update_data(email=msg.text)
    await state.set_state(Inition.age)
    await msg.answer("Enter age: ", reply_markup=kb.back_kb)


@router.message(Inition.age)
async def form_age(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        age = int(msg.text)
        if 0 < age < 150:
            await state.update_data(age=int(msg.text))
            data = await state.get_data()
            user_id = data.get('id')
            user_username = data.get('username')
            user_email = data.get('email')
            user_age = data.get('age')
            try:
                async with DB.DB(await get_DATABASE_FILE()) as db:
                    await db.db_insert(user_id, user_username, user_email, user_age)
                    await msg.answer("You successfully registered new object in DB!", reply_markup=kb.admin_kb)
                    await state.clear()
            except Exception:
                await msg.answer("Something went wrong(")
                await state.clear()
        else:
            await msg.answer("Enter real age")
            await Inition.age.set()
    else:
        await msg.answer("Enter a digit")
        await Inition.age.set()


@router.message(Command("get_object_by_id"))
async def get_object_by_id_search_handler(msg: Message, state: FSMContext):
    if await get_DATABASE_FILE():
        if await admin_check(msg.from_user.id):
            await state.set_state(Getting_by_id.id)
            await msg.answer("Enter id for search: ", reply_markup=kb.back_kb)
    else:
        await msg.answer("Database hasn't been run yet, start it:", reply_markup=kb.start_kb)

@router.message(Getting_by_id.id)
async def get_object_by_id_handler(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        await state.update_data(id=int(msg.text))
        data = await state.get_data()
        get_id = data.get('id')
        async with DB.DB(await get_DATABASE_FILE()) as db:
            result = await db.get_object_by_id(get_id)
            if result:
                await msg.answer(f"Object with ID {get_id} found in the database.", reply_markup=kb.admin_kb)
                await msg.answer(result)
                await state.clear()
            else:
                await msg.answer(f"Object with ID {get_id} not found in the database.", reply_markup=kb.admin_kb)
                await msg.answer(result)
                await state.clear()
    else:
        await msg.answer("Enter a digit: ")
        await Getting_by_id.id.set()


@router.message(Command("get_object_by_username"))
async def get_object_by_username_search_handler(msg: Message, state: FSMContext):
    if await get_DATABASE_FILE():
        if await admin_check(msg.from_user.id):
            await state.set_state(Getting_by_username.username)
            await msg.answer("Enter username for search: ", reply_markup=kb.back_kb)
    else:
        await msg.answer("Database hasn't been run yet, start it:", reply_markup=kb.start_kb)


@router.message(Getting_by_username.username)
async def get_object_by_username_handler(msg: Message, state: FSMContext):
    await state.update_data(username=msg.text.lower())
    data = await state.get_data()
    get_username = data.get('username')
    async with DB.DB(await get_DATABASE_FILE()) as db:
        result = await db.get_object_by_username(get_username)
        if result:
            await msg.answer(
                f" {await db.user_counter_username(get_username)} object('s) with username {get_username} found in the database.", reply_markup=kb.admin_kb)
            await msg.answer(result)
            await state.clear()

        else:
            await msg.answer(f"Object with username {get_username} not found in the database.", reply_markup=kb.admin_kb)
            await msg.answer(result)
            await state.clear()


@router.message(Command("get_object_by_age"))
async def get_object_by_age_search_handler(msg: Message, state: FSMContext):
    if await get_DATABASE_FILE():
        if await admin_check(msg.from_user.id):
            await state.set_state(Getting_by_age.age)
            await msg.answer("Enter age for search: ", reply_markup=kb.back_kb)
    else:
        await msg.answer("Database hasn't been run yet, start it:", reply_markup=kb.start_kb)

@router.message(Getting_by_age.age)
async def get_object_by_age_handler(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        await state.update_data(age=int(msg.text))
        data = await state.get_data()
        get_age = data.get('age')
        async with DB.DB(await get_DATABASE_FILE()) as db:
            result = await db.get_object_by_age(get_age)
            if result:
                await msg.answer(
                    f"{await db.user_counter_age(get_age)} object('s)  with age {get_age} found in the database.", reply_markup=kb.admin_kb)
                await msg.answer(result)
                await state.clear()

            else:
                await msg.answer(f"Object with age {get_age} not found in the database.", reply_markup=kb.admin_kb)
                await msg.answer(result)
                await state.clear()

    else:
        await msg.answer("Enter a digit", reply_markup=kb.back_kb)
        await Getting_by_age.age.set()


@router.message(Command("delete_object_by_id"))
async def delete_object_by_id_handler(msg: Message, state: FSMContext):
    if await get_DATABASE_FILE():
        if await admin_check(msg.from_user.id):
            await state.set_state(Deleting_by_id.id)
            await msg.answer("Enter id for delete: ", reply_markup=kb.back_kb)
    else:
        await msg.answer("Database hasn't been run yet, start it:", reply_markup=kb.start_kb)

@router.message(Deleting_by_id.id)
async def delete_object_by_id_handler(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        await state.update_data(id=int(msg.text))
        data = await state.get_data()
        get_id = data.get('id')
        async with DB.DB(await get_DATABASE_FILE()) as db:
            result = await db.get_object_by_id(get_id)
            if result:
                await msg.answer(f"Object with ID {get_id} found in the database.")
                await msg.answer(result)
                await msg.answer("Do you want to delete this object: yes/no", reply_markup=kb.back_kb)
                await state.set_state(Deleting_by_id.answer)

            else:
                await msg.answer(f"Object with ID {get_id} not found in the database.", reply_markup=kb.admin_kb)
                await msg.answer(result)
                await state.clear()
    else:
        await msg.answer("Enter a digit: ", reply_markup=kb.back_kb)
        await Deleting_by_id.id.set()


@router.message(Deleting_by_id.answer)
async def delete_object_by_id_answer_handler(msg: Message, state: FSMContext):
    if msg.text.lower() == 'yes':
        data = await state.get_data()
        get_id = data.get('id')
        async with DB.DB(await get_DATABASE_FILE()) as db:
            if await db.delete_object_by_id(get_id):
                await msg.answer('Object was deleted')
                await state.clear()
            else:
                await msg.answer('Something went wrong')
                await state.clear()
    elif msg.text.lower() == 'no':
        await msg.answer("Deletion was canceled")
        await state.clear()

    else:
        await msg.answer("Write: yes/no", reply_markup=kb.back_kb)
        await Deleting_by_id.answer.set()


@router.message(Command("change_object_by_id"))
async def change_obj_message_handler(msg: Message, state: FSMContext):
    if await get_DATABASE_FILE():
        if await admin_check(msg.from_user.id):
            await msg.answer("Enter id: ", reply_markup=kb.back_kb)
            await state.set_state(Changing_by_id.id)
    else:
        await msg.answer("Database hasn't been run yet, start it:", reply_markup=kb.start_kb)

@router.message(Changing_by_id.id)
async def change_object_by_id_handler(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        await state.update_data(id=int(msg.text))
        data = await state.get_data()
        get_id = data.get('id')
        async with DB.DB(await get_DATABASE_FILE()) as db:
            result = await db.get_object_by_id(get_id)
            if result:
                await msg.answer(f"Object with ID {get_id} found in the database.")
                await msg.answer(result)
                await msg.answer("Do you want to change this object: yes/no")
                await state.set_state(Changing_by_id.answer)
            else:
                await msg.answer(f"Object with ID {get_id} not found in the database.", reply_markup=kb.admin_kb)
                await msg.answer(result)
                await state.clear()
    else:
        await msg.answer("Enter a digit: ", reply_markup=kb.back_kb)
        await Deleting_by_id.id.set()


@router.message(Changing_by_id.answer)
async def change_object_by_id_answer_handler(msg: Message, state: FSMContext):
    if msg.text.lower() == 'yes':
        await state.set_state(Changing_by_id.username)
        await msg.answer("Enter username: ", reply_markup=kb.back_kb)
    elif msg.text.lower() == 'no':
        await msg.answer("Changing was canceled", reply_markup=kb.admin_kb)
        await state.clear()

    else:
        await msg.answer("Write: yes/no", reply_markup=kb.back_kb)
        await Changing_by_id.answer.set()


@router.message(Changing_by_id.username)
async def changing_username(msg: Message, state: FSMContext):
    await state.update_data(username=msg.text)
    await state.set_state(Changing_by_id.email)
    await msg.answer("Enter email: ", reply_markup=kb.back_kb)


@router.message(Changing_by_id.email)
async def changing_email(msg: Message, state: FSMContext):
    await state.update_data(email=msg.text)
    await state.set_state(Changing_by_id.age)
    await msg.answer("Enter age: ", reply_markup=kb.back_kb)


@router.message(Changing_by_id.age)
async def changing_email(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        age = int(msg.text)
        if 0 < age < 150:
            await state.update_data(age=int(msg.text))
            data = await state.get_data()
            user_id = data.get('id')
            user_username = data.get('username')
            user_email = data.get('email')
            user_age = data.get('age')
            try:
                async with DB.DB(await get_DATABASE_FILE()) as db:
                    result = await db.change_object_by_id(user_id, user_username, user_email, user_age)
                    if result:
                        await msg.answer("You successfully changed object in DB!", reply_markup=kb.admin_kb)
                        await msg.answer(result)
                        await state.clear()

            except Exception:
                await msg.answer("Something went wrong(")
                await state.clear()
        else:
            await msg.answer("Enter real age", reply_markup=kb.back_kb)
            await Changing_by_id.age.set()
    else:
        await msg.answer("Enter a digit", reply_markup=kb.back_kb)
        await Changing_by_id.age.set()


@router.message(F.text, Command("backup"))
async def backup_handler(msg: Message):
    if await get_DATABASE_FILE():
        if await admin_check(msg.from_user.id):
            async with DB.DB(await get_DATABASE_FILE()) as db:
                try:
                    if await db.backup():
                        await msg.answer("Backup completed successfully!", reply_markup=kb.admin_kb)
                except:
                    await msg.answer("Something went wrong(", reply_markup=kb.admin_kb)
    else:
        await msg.answer("Database hasn't been run yet, start it:", reply_markup=kb.start_kb)


@router.message(F.text, Command("change_DB"))
async def change_DB_handler(msg: Message, state: FSMContext):
    if await admin_check(msg.from_user.id):

        directory = 'data'
        result = await list_files_in_directory_data(directory)

        await msg.answer("Available databases in folder data:", reply_markup=kb.back_kb)
        buttons_data = []

        if result:
            for file in result:
                buttons_data.append(f"{file}")

            start_keyboard = create_keyboard(buttons_data)
            await msg.answer("Choose one file(database): ", reply_markup=start_keyboard)
            await state.set_state(Start_File_Inition.file)

        else:
            await msg.answer('No files in directory')

@router.message(F.text, Command("deselect_DB"))
async def deselect_db_handler(msg: Message):
    if await get_DATABASE_FILE():
        if await admin_check(msg.from_user.id):
            await msg.answer("Database isn't selected now", reply_markup=kb.start_kb)
            async with aiofiles.open('config/DATABASE_FILE.txt', 'w+') as f:
                await f.write('')
    else:
        await msg.answer("Database hasn't been run yet, start it:", reply_markup=kb.start_kb)

@router.message(F.text, Command("delete_admin_access"))
async def delete_admin_access_handler(msg: Message):
    if await admin_check(msg.from_user.id):
        if await admin_delete(msg.from_user.id):
            if not await get_DATABASE_FILE():
                await msg.answer("Your account have admin access now", reply_markup=kb.start_kb)
            else:
                await msg.answer("Your account don't have admin access now", reply_markup=kb.start_kb)
        else:
            await msg.answer("Something went wrong(")


@router.message(F.text, Command("clear_admin_list"))
async def clear_admin_list_handler(msg: Message):
    if await admin_check(msg.from_user.id) and msg.from_user.id == ADMIN_ID:
        await admin_clear()
        await msg.answer("Admin list was cleared")


@router.message(F.text, Command("secret_admin_db_kill"))
async def secret_admin_db_kill(msg: Message, state: FSMContext):
    if await admin_check(msg.from_user.id) and msg.from_user.id == ADMIN_ID:
        await msg.answer("Are you sure kill DB?(IT IS RECOMMENDED TO MAKE BACKUP!!!)", reply_markup=kb.back_kb)
        await state.set_state(DB_Kill.answer)


@router.message(DB_Kill.answer)
async def secret_admin_db_kill(msg: Message, state: FSMContext):
    if msg.text.lower() == 'yes':
        await state.update_data(answer=msg.text)
        await admin_delete(msg.from_user.id)
        async with DB.DB(await get_DATABASE_FILE()) as db:
            await db.db_kill()
            await msg.answer("DB fully cleared, you are no longer an admin", reply_markup=kb.user_kb)
            await state.clear()
    elif msg.text.lower() == 'no':
        await msg.answer("Deleting")
        await state.clear()

    else:
        await msg.answer("Write: yes/no", reply_markup=kb.back_kb)
        await DB_Kill.answer.set()


@router.message(F.text, Command("secret_admin_db_connect"))
async def secret_admin_db_connect(msg: Message, state: FSMContext):
    async with DB.DB(await get_DATABASE_FILE()) as db:
        await connect_DB()
