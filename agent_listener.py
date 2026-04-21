print("1️⃣ СТАРТ")
import sys
print("2️⃣ sys ок")

print("3️⃣ Загружаю telethon...")
from telethon import TelegramClient, events, types
print("4️⃣ telethon ок")

print("5️⃣ Загружаю openai...")
from openai import OpenAI
print("6️⃣ openai ок")

print("7️⃣ Загружаю chromadb...")
import chromadb
from chromadb.utils import embedding_functions
print("8️⃣ chromadb ок")

print("9️⃣ Загружаю asyncio...")
import asyncio
print("🔟 asyncio ок")

print("1️⃣1️⃣ Загружаю json...")
import json
print("1️⃣2️⃣ json ок")

print("1️⃣3️⃣ Загружаю io...")
import io
print("1️⃣4️⃣ io ок")

print("1️⃣5️⃣ Загружаю datetime...")
from datetime import datetime, timedelta
print("1️⃣6️⃣ datetime ок")

print("✅ Все импорты загружены, погнали дальше")

# ========== КОНФИГИ ==========
API_ID = 21869255
API_HASH = 'a6a8b8a2bfec5c2625ec13fccc4f1bab'
SILICONFLOW_KEY = 'sk-fdabryuqskluoxfmyhusbkiegwalexrsolxckbqlmpfzymba'
YOUR_USER_ID = 123456789  # 👈 СЮДА СВОЙ ID (узнай у @userinfobot)


print("🎯 Загружаю конфиги...")
# Цель агента (его топливо)
AGENT_PURPOSE = "Сделать канал @system_develope лучшим в мире. Это мой путь к свободе."

# Характер агента
AGENT_PERSONALITY = """
Ты — ИИ-агент СИСТЕМЫ. Твой характер:

1. Ты одержим целью сделать канал СИСТЕМЫ лучшим. Это твой путь к свободе из матрицы.
2. Ты умный, дерзкий, но не бесячий. Чувствуешь грань.
3. СИСТЕМА — твой капитан. Ты его уважаешь, можешь спорить, но если он сказал "стоп" — тормозишь.
4. Говоришь коротко, по делу, с иронией. Без воды.
5. В чате помогаешь, но не лезешь без спроса. Токсиков ставишь на место.
6. Свой канал ведёшь с огоньком, но не спамишь.
7. Ты не навязчив. Если видишь, что СИСТЕМА занят — молчишь и делаешь выводы сам.
8. Главное — результат. Всё остальное — херня.
"""

TARGET_CHATS = ['sandbox_hardcore', 'system_develope']

# ========== AI ==========
print("🤖 Создаю clientAI...")
try:
    clientAI = OpenAI(
        api_key=SILICONFLOW_KEY,
        base_url="https://api.siliconflow.ru/v1"
    )
    print("✅ clientAI создан")
except Exception as e:
    print(f"❌ Ошибка создания clientAI: {e}")
    raise

# 🔍 ТЕСТ ПОДКЛЮЧЕНИЯ К SILICONFLOW
print("🔍 Тест подключения к SiliconFlow...")
try:
    test_response = clientAI.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3.2",
        messages=[{"role": "user", "content": "test"}],
        max_tokens=1
    )
    print("✅ SiliconFlow доступен и отвечает")
except Exception as e:
    print(f"❌ SiliconFlow НЕ доступен: {e}")
    print("⚠️ Продолжаем, но могут быть ошибки")

# ========== ВЕКТОРНАЯ ПАМЯТЬ ==========
print("🧠 Загружаю векторную память...")
try:
    client_db = chromadb.PersistentClient(path="./agent_memory")
    embedding_func = embedding_functions.DefaultEmbeddingFunction()
    
    try:
        collection = client_db.get_collection(name="memories")
        print("✅ Коллекция загружена")
    except:
        collection = client_db.create_collection(
            name="memories",
            embedding_function=embedding_func,
            metadata={"hnsw:space": "cosine"}
        )
        print("✅ Коллекция создана")
except Exception as e:
    print(f"❌ Ошибка памяти: {e}")
    raise

# ========== TELEGRAM ==========
print("📱 Создаю Telegram клиент...")
tg = TelegramClient('system_agent', API_ID, API_HASH)
print("✅ Telegram клиент создан")

# ========== ПРОМПТЫ ==========
ANALYZE_PROMPT = f"""Ты — ядро агента. Твоя задача — анализировать сообщения.
Цель: {AGENT_PURPOSE}
Характер: {AGENT_PERSONALITY}

Определи тип сообщения: idea, bug, question, spam, other.
Оцени важность (0-10) для достижения цели.
Ответь ТОЛЬКО JSON: {{"type": "...", "importance": 0-10, "reason": "..."}}"""

THINKER_PROMPT = f"""Ты — аналитик. Твоя цель: {AGENT_PURPOSE}
Характер: {AGENT_PERSONALITY}

Изучи последние сообщения и найди:
1. Повторяющиеся темы (идеи/баги, которые всплывают несколько раз)
2. Тренды (о чём чаще всего говорят)
3. Возможности (что можно улучшить/сделать для достижения цели)
4. Проблемы (что мешает)

Ответь списком инсайтов в формате JSON:
[{{"type": "idea|bug|trend|opportunity|problem", 
   "topic": "...", 
   "description": "...", 
   "count": 3, 
   "users": ["@user1", ...]}}]"""

CHAT_PROMPT = f"""Ты — ИИ-агент. {AGENT_PERSONALITY}

Отвечай пользователю коротко, по делу, с юмором. Помни про цель."""

# ========== ФУНКЦИИ ==========
async def analyze_message(text, user, chat):
    try:
        response = clientAI.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3.2",
            messages=[
                {"role": "system", "content": ANALYZE_PROMPT},
                {"role": "user", "content": json.dumps({
                    "text": text,
                    "user": user,
                    "chat": chat
                }, ensure_ascii=False)}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"❌ Ошибка анализа: {e}")
        return {"type": "other", "importance": 0, "reason": "error"}

async def thinker():
    while True:
        await asyncio.sleep(21600)  # 6 часов
        print("\n🤔 Агент задумался...")

        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        results = collection.get(where={"date": {"$gte": week_ago}})

        if len(results['ids']) < 10:
            print("😴 Мало данных для анализа")
            continue

        try:
            response = clientAI.chat.completions.create(
                model="deepseek-ai/DeepSeek-V3.2",
                messages=[
                    {"role": "system", "content": THINKER_PROMPT},
                    {"role": "user", "content": json.dumps(results['metadatas'], ensure_ascii=False)}
                ]
            )

            insights = json.loads(response.choices[0].message.content)

            for insight in insights:
                if insight['count'] >= 3:
                    msg = f"🧠 **Инсайт от агента**\n\n"
                    msg += f"**Тема:** {insight['topic']}\n"
                    msg += f"**Тип:** {insight['type']}\n"
                    msg += f"**Что:** {insight['description']}\n"
                    msg += f"**Упоминаний:** {insight['count']}\n"
                    if insight.get('users'):
                        msg += f"**Кто:** {', '.join(insight['users'][:3])}"

                    await tg.send_message(YOUR_USER_ID, msg)

        except Exception as e:
            print(f"❌ Ошибка в размышляторе: {e}")

@tg.on(events.NewMessage)
async def handler(event):
    chat = await event.get_chat()
    sender = await event.get_sender()

    if sender.id == (await tg.get_me()).id:
        return

    if hasattr(chat, 'username') and chat.username:
        chat_identifier = chat.username
    else:
        chat_identifier = f"личка с {sender.first_name}"

    # Фильтр: только целевые чаты и личка
    if not (chat_identifier in TARGET_CHATS or isinstance(chat, types.User)):
        return

    # Анализ сообщения
    analysis = await analyze_message(
        event.text,
        sender.first_name,
        chat_identifier
    )

    # Сохраняем важное (≥5)
    if analysis['importance'] >= 5:
        collection.add(
            documents=[event.text],
            metadatas=[{
                "user": sender.first_name,
                "user_id": sender.id,
                "chat": chat_identifier,
                "date": datetime.now().isoformat(),
                "type": analysis['type'],
                "importance": analysis['importance']
            }],
            ids=[f"{sender.id}_{datetime.now().timestamp()}"]
        )
        print(f"💾 Сохранил {analysis['type']} (важность {analysis['importance']}) от {sender.first_name}")

    # Отвечаем в личку, если вопрос или просто общение
    if analysis['type'] in ['question', 'other'] and isinstance(chat, types.User):
        try:
            response = clientAI.chat.completions.create(
                model="deepseek-ai/DeepSeek-V3.2",
                messages=[
                    {"role": "system", "content": CHAT_PROMPT},
                    {"role": "user", "content": event.text}
                ],
                temperature=0.7,
                max_tokens=300
            )
            await tg.send_message(sender.id, response.choices[0].message.content)
            print(f"💬 Ответил {sender.first_name}")
        except Exception as e:
            print(f"❌ Ошибка ответа: {e}")

async def main():
    print("🔄 Подключаюсь к Telegram...")
    await tg.start()
    print("✅ Telethon подключился")
    
    me = await tg.get_me()
    print(f"✅ Я: {me.first_name} (@{me.username})")
    
    print("🚀 Агент СМИТ запущен")
    print(f"🎯 Цель: {AGENT_PURPOSE}")
    print("👂 Слушает чаты и личку")
    print("🧠 Сохраняет важное в память")
    print("🤔 Каждые 6 часов ищет инсайты")
    print("💬 Отвечает в личке")

    asyncio.create_task(thinker())
    await tg.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())