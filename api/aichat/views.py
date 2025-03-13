import json
import os
import re
import sqlite3

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")


def extract_valid_sql(sql_text):
    """
    Извлекает подстроку, которая выглядит как SQL-запрос, начиная с "select" и заканчивая на ";".
    Если запрос не содержит ";" – возвращает всю строку от первого "select".
    """
    pattern = re.compile(r"(select.*?;)", re.IGNORECASE | re.DOTALL)
    match = pattern.search(sql_text)
    if match:
        return match.group(1).strip()
    else:
        # Если нет точки с запятой, попробуем найти первое вхождение "select"
        lower_text = sql_text.lower()
        if "select" in lower_text:
            idx = lower_text.find("select")
            return sql_text[idx:].strip()
        else:
            return ""


def generate_sql_query_mistral(question, schema_description):
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json",
    }

    prompt = (
        f"You are an expert SQL generator. Given the following database schema:\n\n"
        f"{schema_description}\n\n"
        f"Generate a valid SQL query to answer the following question without any explanation, "
        f"and include a semicolon at the end of the query:\n\n"
        f'"{question}"'
    )

    payload = {
        "model": "mistral-tiny",
        "messages": [{"role": "user", "content": prompt}],
    }

    response = requests.post(
        "https://api.mistral.ai/v1/chat/completions", headers=headers, json=payload
    )

    if response.status_code == 200:
        sql_text = response.json()["choices"][0]["message"]["content"].strip()
        print(f"Raw generated text: {sql_text}")
        sql_query = extract_valid_sql(sql_text)
        return sql_query
    else:
        return None


def clean_sql_query(sql_query):
    # Убираем обрамляющие символы Markdown, если они есть, и лишние переносы строк
    sql_query = re.sub(r"```.*?```", "", sql_query, flags=re.DOTALL).strip()
    sql_query = sql_query.replace("\n", " ").strip()
    return sql_query


def execute_sql_query(query):
    cleaned_query = clean_sql_query(query)
    print(f"Executing query: {cleaned_query}")

    conn = sqlite3.connect(
        r"C:\Users\eseev\OneDrive\Рабочий стол\django_api\api\db.sqlite3"
    )
    cursor = conn.cursor()
    try:
        cursor.execute(cleaned_query)
        results = cursor.fetchall()
    except Exception as e:
        results = f"Ошибка при выполнении запроса: {e}"
    finally:
        conn.close()
    return results


SCHEMA_DESCRIPTION = (
    "Table api_django_product: id (INTEGER), name (TEXT), description (TEXT), price (DECIMAL), stock (INTEGER)\n"
    "Table api_django_order: id (INTEGER), user_id (INTEGER), total_price (DECIMAL), pub_date (DATE)\n"
    "Table api_django_order_products: id (INTEGER), order_id (INTEGER), product_id (INTEGER), quantity (INTEGER)\n"
    "Table users_customer: id (INTEGER), user_id (INTEGER), address (TEXT)\n"
    "Table users_user: id (INTEGER), username (TEXT), email (TEXT), role (TEXT)"
)


@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])  # Проверка на аутентификацию через токен
def chat_with_ai(request):
    if request.method == "POST":
        try:
            # Переводим тело запроса в JSON
            data = json.loads(request.body)
            user_message = data.get("message", "")

            # Проверка, есть ли сообщение
            if user_message:
                # Генерация SQL-запроса
                sql_query = generate_sql_query_mistral(user_message, SCHEMA_DESCRIPTION)
                print(f"Generated SQL Query: {sql_query}")

                # Проверка, начинается ли запрос с SELECT
                if sql_query and sql_query.lower().startswith("select"):
                    # Выполнение SQL-запроса
                    results = execute_sql_query(sql_query)
                    reply = f"SQL-запрос:\n{sql_query}\n\nРезультат:\n{results}"
                else:
                    reply = "Failed to generate a valid SELECT SQL query."
                return JsonResponse({"reply": reply})

            # Если сообщение пустое
            return JsonResponse({"reply": "Пустой запрос."})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)



