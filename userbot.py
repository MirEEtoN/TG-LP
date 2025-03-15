import asyncio
import logging
import os
import time
from telethon import TelegramClient, events

# Настройки авторизации
API_ID = 
API_HASH = 
SESSION_NAME = "userbot"

# База данных (эмуляция через словари)
ignored_users = set()
blacklist_users = set()
saved_templates = {}

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# Настройка логирования
LOG_FILE = "userbot.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, mode='w'), logging.StreamHandler()]
)

# Пример записи в лог
logging.info("Userbot запущен.")

# Игнор-лист
@client.on(events.NewMessage)
async def ignore_handler(event):
    if event.sender_id in ignored_users:
        await event.delete()

@client.on(events.NewMessage(pattern=r"Л \+игнор"))
async def add_ignore(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        ignored_users.add(reply.sender_id)
        await event.edit("✅ Пользователь добавлен в игнор-лист")

@client.on(events.NewMessage(pattern=r"Л -игнор"))
async def remove_ignore(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        ignored_users.discard(reply.sender_id)
        await event.edit("✅ Пользователь удалён из игнор-листа")

@client.on(events.NewMessage(pattern=r"Л игноры"))
async def list_ignores(event):
    if ignored_users:
        await event.edit(f"👥 Игнор-лист: {', '.join(map(str, ignored_users))}")
    else:
        await event.edit("📭 Игнор-лист пуст")

# Чёрный список
@client.on(events.NewMessage(pattern=r"Л \+чс"))
async def add_blacklist(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        blacklist_users.add(reply.sender_id)
        await event.edit("🚫 Пользователь добавлен в ЧС")

@client.on(events.NewMessage(pattern=r"Л -чс"))
async def remove_blacklist(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        blacklist_users.discard(reply.sender_id)
        await event.edit("✅ Пользователь удалён из ЧС")

# Удаление сообщений
@client.on(events.NewMessage(pattern=r"Л дд(\d*)"))
async def delete_messages(event):
    count = event.pattern_match.group(1)
    count = int(count) if count else 2  # По умолчанию удаляется 2 сообщения (текущее и предыдущее)
    
    async for msg in client.iter_messages(event.chat_id, from_user='me', limit=count):
        await msg.delete()
    
    await event.delete()  # Удаляем команду

# Отправка в ЛС
@client.on(events.NewMessage(pattern=r"Л влс (.+)"))
async def send_pm(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        text = event.pattern_match.group(1)
        await client.send_message(reply.sender_id, text)
        await event.edit("📩 Сообщение отправлено в ЛС")
    else:
        await event.edit("⚠ Используйте команду с реплаем на сообщение!")

# Шаблоны
@client.on(events.NewMessage(pattern=r"Л \+шаблон (\S+)"))
async def save_template(event):
    args = event.pattern_match.group(1)
    if event.is_reply:
        reply = await event.get_reply_message()
        saved_templates[args] = reply.message
        await event.edit(f"✅ Шаблон `{args}` сохранён")
    else:
        await event.edit("⚠ Используйте команду с реплаем на сообщение!")

@client.on(events.NewMessage(pattern=r"Л шаблон (\S+)"))
async def send_template(event):
    args = event.pattern_match.group(1)
    if args in saved_templates:
        await event.edit(saved_templates[args])
    else:
        await event.edit("⚠ Шаблон не найден")

@client.on(events.NewMessage(pattern=r"Л -шаблон (\S+)"))
async def delete_template(event):
    args = event.pattern_match.group(1)
    if args in saved_templates:
        del saved_templates[args]
        await event.edit(f"🗑 Шаблон `{args}` удалён")
    else:
        await event.edit("⚠ Шаблон не найден")

@client.on(events.NewMessage(pattern=r"Л шаблоны все"))
async def list_templates(event):
    if saved_templates:
        templates_list = '\n'.join([f"{i+1}. {name}" for i, name in enumerate(saved_templates.keys())])
        await event.edit(f"📂 Сохранённые шаблоны:\n{templates_list}")
    else:
        await event.edit("📭 Шаблоны отсутствуют")

# Пинг
@client.on(events.NewMessage(pattern=r"Л пинг"))
async def ping(event):
    start_time = time.time()
    await event.edit("🏓 Пингую сервер...")
    await asyncio.sleep(1)
    end_time = time.time()
    ping_time = round((end_time - start_time - 1) * 1000, 2)
    await event.edit(f"🏓 Понг! Задержка: {ping_time} мс")

# Чат информация
@client.on(events.NewMessage(pattern=r"Л чат инфо"))
async def chat_info(event):
    chat = await event.get_chat()
    users = await client.get_participants(chat)
    humans = [user.id for user in users if not user.bot]
    bots = [user.id for user in users if user.bot]
    
    # Статистика чата
    chat_name = chat.title or "Без имени"
    chat_id = chat.id
    chat_type = "Групповой чат" if chat.megagroup else "Личное сообщение"
    total_users = len(humans) + len(bots)
    active_users = len(humans)
    active_bots = len(bots)
    
    # Создаём красивый вывод
    chat_info_msg = f"📊 **Информация о чате**\n" \
                    f"📝 **Название чата**: {chat_name}\n" \
                    f"💬 **ID чата**: {chat_id}\n" \
                    f"🔹 **Тип чата**: {chat_type}\n\n" \
                    f"👥 **Частные участники**: {active_users}\n" \
                    f"🤖 **Боты**: {active_bots}\n" \
                    f"👫 **Общее количество участников**: {total_users}"

    # Отправляем сообщение с подробной информацией
    await event.edit(chat_info_msg)

# Команды
@client.on(events.NewMessage(pattern=r"Л команды"))
async def list_commands(event):
    commands = (
        "📜 Список команд:\n"
        "Л +игнор / -игнор — добавить/убрать в игнор-лист\n"
        "Л игноры — список игнорируемых пользователей\n"
        "Л +чс / -чс — добавить/убрать в ЧС\n"
        "Л дд(число) — удалить свои сообщения\n"
        "Л влс (текст) — отправить текст в ЛС\n"
        "Л +шаблон / -шаблон (имя) — сохранить/удалить шаблон\n"
        "Л шаблоны все — список шаблонов\n"
        "Л шаблон (имя) — отправить шаблон\n"
        "Л пинг — проверить задержку\n"
        "Л чат инфо — информация о чате\n"
        "Л команды — показать список команд\n"
        "Л лог — отправить файл лога\n"
        "Л админы — список администраторов чата\n"
        "Л +админ — добавить пользователя в администраторы\n"
        "Л -админ — удалить пользователя из администраторов\n"
        "Л добавить — добавить пользователя в чат\n"
        "Л кик — удалить пользователя из чата\n"
    )
    await event.edit(commands)

# Команда Л лог
@client.on(events.NewMessage(pattern=r"Л лог"))
async def send_log(event):
    if os.path.exists(LOG_FILE):
        # Отправляем лог файл в чат
        await client.send_file(event.chat_id, LOG_FILE, caption="📜 Вот файл лога:")
        await event.delete()  # Удаляем команду
    else:
        await event.edit("⚠ Лог файл не найден.")

# Административные команды
@client.on(events.NewMessage(pattern=r"Л админы"))
async def list_admins(event):
    chat = await event.get_chat()
    admins = await client.get_chat_admins(chat.id)
    admin_list = "\n".join([f"{admin.user.first_name} (@{admin.user.username})" for admin in admins])
    await event.edit(f"👥 **Список админов**:\n{admin_list}")

@client.on(events.NewMessage(pattern=r"Л \+админ"))
async def add_admin(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        user_id = reply.sender_id
        await client.add_chat_admin(event.chat_id, user_id)
        await event.edit("✅ Пользователь стал администратором")

@client.on(events.NewMessage(pattern=r"Л -админ"))
async def remove_admin(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        user_id = reply.sender_id
        await client.remove_chat_admin(event.chat_id, user_id)
        await event.edit("✅ Пользователь больше не администратор")

# Запуск клиента
with client:
    print("✅ Userbot запущен!")
    client.run_until_disconnected()
