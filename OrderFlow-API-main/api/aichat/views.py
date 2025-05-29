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
    "Table api_django_category: id (bigint), name (character varying)\n"
    "Table api_django_discount: id (bigint), code (character varying), discount_percentage (integer), valid_from (date), valid_to (date), is_active (boolean)\n"
    "Table api_django_order: id (bigint), pub_date (date), total_price (numeric), user_id (bigint), discount_id (bigint)\n"
    "Table api_django_order_products: id (bigint), order_id (bigint), product_id (bigint)\n"
    "Table api_django_orderproduct: id (bigint), quantity (integer), order_id (bigint), product_id (bigint)\n"
    "Table api_django_product: id (bigint), name (character varying), description (text), price (numeric), pub_date (date), stock (integer), category_id (bigint), video (character varying), image (character varying)\n"
    "Table api_django_productreview: id (bigint), rating (integer), comment (text), sentiment (character varying), created_at (timestamp with time zone), video (character varying), customer_id (bigint), product_id (bigint), image (character varying)\n"
    "Table api_django_purchasehistory: id (bigint), purchase_date (timestamp with time zone), product_id (bigint), user_id (bigint), order_id (bigint), price (numeric), quantity (integer)\n"
    "Table auth_group: id (integer), name (character varying)\n"
    "Table auth_group_permissions: id (bigint), group_id (integer), permission_id (integer)\n"
    "Table auth_permission: id (integer), name (character varying), content_type_id (integer), codename (character varying)\n"
    "Table django_admin_log: id (integer), action_time (timestamp with time zone), object_id (text), object_repr (character varying), action_flag (smallint), change_message (text), content_type_id (integer), user_id (bigint)\n"
    "Table django_content_type: id (integer), app_label (character varying), model (character varying)\n"
    "Table django_migrations: id (bigint), app (character varying), name (character varying), applied (timestamp with time zone)\n"
    "Table django_session: session_key (character varying), session_data (text), expire_date (timestamp with time zone)\n"
    "Table users_customer: id (bigint), phone_number (character varying), address (character varying), contact_name (character varying), company_name (character varying), country (character varying), user_id (bigint)\n"
    "Table users_employee: id (bigint), first_name (character varying), last_name (character varying), phone (character varying), salary (numeric), user_id (bigint)\n"
    "Table users_supplier: id (bigint), name (character varying), contact_name (character varying), contact_phone (character varying), address (text), created_at (timestamp with time zone), user_id (bigint)\n"
    "Table users_user: id (bigint), password (character varying), last_login (timestamp with time zone), is_superuser (boolean), is_staff (boolean), is_active (boolean), date_joined (timestamp with time zone), username (character varying), email (character varying), first_name (character varying), last_name (character varying), role (character varying)\n"
    "Table users_user_groups: id (bigint), user_id (bigint), group_id (integer)\n"
    "Table users_user_user_permissions: id (bigint), user_id (bigint), permission_id (integer)\n"
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
