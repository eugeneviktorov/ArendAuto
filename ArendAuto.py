from aiogram.utils import executor
from create_bot import dp

async def on_start(_):
    print('Bot is Run!')

from handler import client, client_admin
client_admin.admin_handlers_register(dp)
client.client_handlers_register(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_start)