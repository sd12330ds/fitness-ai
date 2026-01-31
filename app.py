from flask import Flask, render_template, request, redirect, jsonify, session
import json, os, hashlib
from datetime import date
from pyngrok import ngrok

# =========================
# Flask
# =========================

app = Flask(__name__)
import os

app.secret_key = os.environ.get("SECRET_KEY", "dev-key")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_DIR = os.path.join(DATA_DIR, "logs")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# =========================
# 常數
# =========================

DAILY_KCAL_TARGET = 2650
DAILY_PROTEIN_TARGET = 130
DAILY_CARBS_TARGET = 350
DAILY_FAT_TARGET = 70

FOOD_FILE = os.path.join(DATA_DIR, "foods.json")
CUSTOM_MEAL_FILE = os.path.join(DATA_DIR, "custom_meals.json")
USER_FILE = os.path.join(DATA_DIR, "users.json")


# =========================
# 工具
# =========================

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def hash_pwd(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()


def get_log_file():
    user = session.get("user")
    return os.path.join(LOG_DIR, f"{user}.json")


# =========================
# 計算營養
# =========================

def calc_total(logs, foods):
    total = {"kcal": 0, "protein": 0, "carbs": 0, "fat": 0}

    for item in logs:
        if "grams" in item:
            nutr = foods.get(item["food"])
            if not nutr:
                continue

            f = item["grams"] / 100
            total["kcal"] += nutr["kcal"] * f
            total["protein"] += nutr["protein"] * f
            total["carbs"] += nutr["carbs"] * f
            total["fat"] += nutr["fat"] * f
        else:
            total["kcal"] += item.get("kcal", 0)
            total["protein"] += item.get("protein", 0)
            total["carbs"] += item.get("carbs", 0)
            total["fat"] += item.get("fat", 0)

    return total


# =========================
# 註冊
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():
    users = load_json(USER_FILE)

    if request.method == "POST":
        user = request.form["username"].strip()
        pwd = request.form["password"]

        if user in users:
            return "帳號已存在"

        users[user] = {"password": hash_pwd(pwd)}
        save_json(USER_FILE, users)

        save_json(os.path.join(LOG_DIR, f"{user}.json"), {})
        return redirect("/login")

    return render_template("register.html")


# =========================
# 登入
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():
    users = load_json(USER_FILE)

    if request.method == "POST":
        user = request.form["username"]
        pwd = hash_pwd(request.form["password"])

        if user not in users or users[user]["password"] != pwd:
            return "帳號或密碼錯誤"

        session["user"] = user
        return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# =========================
# 首頁
# =========================

@app.route("/", methods=["GET", "POST"])
def index():

    if "user" not in session:
        return redirect("/login")

    foods = load_json(FOOD_FILE)
    customs = load_json(CUSTOM_MEAL_FILE)

    log_file = get_log_file()
    logs = load_json(log_file)

    today = (
        request.form.get("date")
        or request.args.get("date")
        or str(date.today())
    )

    # ---------- 新增一般食物 ----------
    if request.method == "POST" and "food" in request.form:

        food = request.form.get("food", "").strip()
        meal = request.form.get("meal", "")
        grams = request.form.get("grams", "100")

        if not food or food not in foods:
            return redirect(f"/?date={today}&error=請選擇有效食物")

        if not grams.isdigit():
            grams = "100"

        logs.setdefault(today, []).append({
            "meal": meal,
            "food": food,
            "grams": int(grams)
        })

        save_json(log_file, logs)
        return redirect(f"/?date={today}")

    day_logs = logs.get(today, [])
    total = calc_total(day_logs, foods)

    return render_template(
        "index.html",
        today=today,
        foods=list(foods.keys()),
        customs=customs,
        brands=list(customs.keys()),
        logs=day_logs,
        total=total,
        error=request.args.get("error"),

        kcal_target=DAILY_KCAL_TARGET,
        protein_target=DAILY_PROTEIN_TARGET,
        carbs_target=DAILY_CARBS_TARGET,
        fat_target=DAILY_FAT_TARGET
    )


# =========================
# 新增自訂餐點
# =========================

@app.route("/add_custom", methods=["POST"])
def add_custom():

    data = request.json
    customs = load_json(CUSTOM_MEAL_FILE)

    log_file = get_log_file()
    logs = load_json(log_file)

    info = customs[data["brand"]][data["meal"]]
    ratio = float(data.get("ratio", 1))
    day = data["date"]

    logs.setdefault(day, []).append({
        "meal": data["meal_type"],
        "brand": data["brand"],
        "food": data["meal"],
        "kcal": info["kcal"] * ratio,
        "protein": info["protein"] * ratio,
        "carbs": info["carbs"] * ratio,
        "fat": info["fat"] * ratio
    })

    save_json(log_file, logs)
    return jsonify({"ok": True})


# =========================
# 刪除
# =========================

@app.route("/delete", methods=["POST"])
def delete_log():

    data = request.json
    day = data["date"]
    index = int(data["index"])

    log_file = get_log_file()
    logs = load_json(log_file)

    if day in logs and 0 <= index < len(logs[day]):
        logs[day].pop(index)

    save_json(log_file, logs)
    return jsonify({"ok": True})


# =========================

if __name__ == "__main__":
    app.run()




public_url = ngrok.connect(5000)
print("🌍 公開網址：", public_url)