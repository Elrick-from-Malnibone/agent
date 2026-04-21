from telethon import TelegramClient
import asyncio


async def main():
    api_id = 21869255
    api_hash = 'a6a8b8a2bfec5c2625ec13fccc4f1bab'

    client = TelegramClient('system_agent', api_id, api_hash)

    await client.start()

    print("✅ Агент готов!")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())