import requests

API_KEY = "sk-bad8f84b3c0545f486b9b51c404e970b"  # Вставь свой ключ

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "deepseek-coder",
    "messages": [
        {"role": "user", "content": """
У меня есть Python функция:
def get_users():
    return [1, 2, 3, 4, 5]

Она возвращает список чисел. Найди в ней баги и объясни, что не так.
"""}
    ],
    "max_tokens": 500,
    "temperature": 0.7
}

response = requests.post(
    "https://api.deepseek.com/v1/chat/completions",
    headers=headers,
    json=data
)

if response.status_code == 200:
    result = response.json()
    print("=== ОТВЕТ МОДЕЛИ ===\n")
    print(result["choices"][0]["message"]["content"])
    print("\n=== МЕТАДАННЫЕ ===")
    print(f"Модель: {result['model']}")
    print(f"Токенов использовано: {result['usage']['total_tokens']}")
else:
    print(f"Ошибка {response.status_code}: {response.text}")