import aiofiles

BOT_TOKEN = "6700094754:AAHWweOYVhFn51xygNiWM53-z2F5PXYroMY"
ADMIN_ID = 630768021


async def get_DATABASE_FILE():
    async with aiofiles.open('config/DATABASE_FILE.txt', 'r') as f:
        DATABASE_FILE = ''
        DATABASE_FILE += await f.readline()
        return DATABASE_FILE


async def admin_check(id):
    async with aiofiles.open("config/adminidlist.txt",
                             'r') as file:

        line = await file.readline()
        while line:
            if line.strip():
                if int(line) == id:
                    return True

            line = await file.readline()

        return False


async def admin_add(id):
    async with aiofiles.open("config/adminidlist.txt",
                             'a+') as file:
        id = str(id)
        await file.write('\n')
        await file.write(id)
        return True


async def admin_delete(id):
    async with aiofiles.open("config/adminidlist.txt",
                             'r') as file:
        lines = await file.readlines()

    async with aiofiles.open("config/adminidlist.txt",
                             'w') as file:
        for line in lines:
            line = line.strip()
            if line:
                if int(line) != id:
                    await file.write(line)

    return True


async def admin_clear():
    async with aiofiles.open("config/adminidlist.txt",
                             'w+') as file:
        await file.write('')
        
        return True
#fuckin git)