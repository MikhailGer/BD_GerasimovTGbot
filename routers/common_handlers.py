import sqlite3
import aiofiles


from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from utils.states import *

from config.config import ADMIN_ID, get_DATABASE_FILE, admin_check, admin_add

import kb
from kb import create_keyboard
import text
import DB
from DB import list_files_in_directory_data
router = Router(name=__name__)


@router.message(F.text, Command("start"))
async def start_handler(msg: Message, state: FSMContext):
    if not (await admin_check(msg.from_user.id)):
        if not await get_DATABASE_FILE():
            await msg.answer("Admin didn't run database yet, please wait...")
        else:
            async with DB.DB(await get_DATABASE_FILE()) as db:
                await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.user_kb)
    else:
        directory = 'data'
        result = await list_files_in_directory_data(directory)

        await msg.answer("Available databases in folder data:")
        buttons_data = []

        if result:
            for file in result:
                buttons_data.append(f"{file}")

            start_keyboard = create_keyboard(buttons_data)
            await msg.answer("Choose one file(database): ", reply_markup=start_keyboard)
            await state.set_state(Start_File_Inition.file)

        else:
            await msg.answer('No files in directory')

@router.message(F.text, Command("back"))
async def start_handler(msg: Message, state: FSMContext):
    if await get_DATABASE_FILE():
        await state.clear()
        if await admin_check(msg.from_user.id):
            await msg.answer("Back in menu", reply_markup=kb.admin_kb)
        else:
            await msg.answer("Back in menu", reply_markup=kb.user_kb)
    else:
        await msg.answer("Admin didn't run database yet, please wait...")

@router.message(F.text, Command("register"))
async def start_handler(msg: Message, state: FSMContext):
    if await get_DATABASE_FILE():
        if not await admin_check(msg.from_user.id):
            await state.set_state(Inition_reg.email)
            await msg.answer("Enter your email: ", reply_markup=kb.back_kb)
    else:
        await msg.answer("Admin didn't run database yet, please wait...")

@router.message(Inition_reg.email)
async def form_email(msg: Message, state: FSMContext):
    await state.update_data(email=msg.text)
    await state.set_state(Inition_reg.age)
    await msg.answer("Enter your age: ", reply_markup=kb.back_kb)


@router.message(Inition_reg.age)
async def form_age(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        age = int(msg.text)
        if 0 < age < 150:
            await state.update_data(age=int(msg.text))
            data = await state.get_data()
            user_email = data.get('email')
            user_age = data.get('age')
            try:
                async with DB.DB(await get_DATABASE_FILE()) as db:
                    await db.db_insert(msg.from_user.id, msg.from_user.username, user_email, user_age)
                    await msg.answer("You successfully registered in DB!", reply_markup=kb.user_kb)
                    await state.clear()

            except sqlite3.IntegrityError as e:
                await msg.answer("An error occurred while inserting data "
                                 "into the database, maybe you already exist in the database", reply_markup=kb.user_kb)
                await state.clear()

        else:
            await msg.answer("Enter real age", reply_markup=kb.back_kb)
            await Inition_reg.age.set()
    else:
        await msg.answer("Enter a digit", reply_markup=kb.back_kb)
        await Inition_reg.age.set()


@router.message(F.text, Command("admin_access"))
async def admin_access_handler(msg: Message):
    if not await admin_check(msg.from_user.id):
        if await admin_add(msg.from_user.id):
            if not await get_DATABASE_FILE():
                await msg.answer("Your account have admin access now", reply_markup=kb.start_kb)
                await msg.answer("You need to run database:", reply_markup=kb.start_kb)
            else:
                await msg.answer("Your account have admin access now", reply_markup=kb.admin_kb)
        else:
            await msg.answer("Something went wrong(")
    else:
        await msg.answer("You are already have admin rights")
