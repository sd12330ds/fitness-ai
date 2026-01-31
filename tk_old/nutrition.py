import json
from datetime import date

FOOD_FILE = "data/foods.json"
LOG_FILE = "data/logs.json"


def load_foods():
    with open(FOOD_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_nutrition(food_name, grams):
    foods = load_foods()

    if food_name not in foods:
        raise ValueError("找不到這個食物")

    food = foods[food_name]
    factor = grams / 100

    return {
        "kcal": food["kcal"] * factor,
        "protein": food["protein"] * factor,
        "carbs": food["carbs"] * factor,
        "fat": food["fat"] * factor
    }


def save_log(food_name, grams,meal):
    today = str(date.today())
    nutrition = calculate_nutrition(food_name, grams)

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = {}

    if today not in logs:
        logs[today] = []

    logs[today].append({
        "meal": meal,
        "food": food_name,
        "grams": grams,
        **nutrition
    })

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)


def get_daily_total(target_date=None):
    if target_date is None:
        target_date = str(date.today())

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except FileNotFoundError:
        return None

    if target_date not in logs:
        return None

    total = {
        "kcal": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0
    }

    for item in logs[target_date]:
        for key in total:
            total[key] += item[key]

    return total

def delete_log(target_date, index):
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except FileNotFoundError:
        return

    if target_date not in logs:
        return

    if index < 0 or index >= len(logs[target_date]):
        return

    logs[target_date].pop(index)

    if not logs[target_date]:
        del logs[target_date]

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

