from aiogram.fsm.state import StatesGroup, State


class Inition(StatesGroup):
    id = State()
    username = State()
    email = State()
    age = State()


# Getting_by_id используется и для удаления(delete_object_by_id) и измененя по имени(change_username_by_id)(наверное, надо чекнуть)
class Getting_by_id(StatesGroup):
    id = State()


class Getting_by_age(StatesGroup):
    age = State()


class Getting_by_username(StatesGroup):
    username = State()


class Deleting_by_id(StatesGroup):
    id = State()
    answer = State()


class Changing_by_id(StatesGroup):
    id = State()
    answer = State()
    username = State()
    email = State()
    age = State()

class DB_Kill(StatesGroup):
    answer = State()

class Inition_reg(StatesGroup):
    id = State()
    username = State()
    email = State()
    age = State()

class Start_File_Inition(StatesGroup):
    file = State()