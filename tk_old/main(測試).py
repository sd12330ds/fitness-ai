import tkinter as tk
from tkinter import messagebox, ttk
import json
from datetime import date,datetime, timedelta

# ===== 資料設定 =====
FOOD_FILE = "data/foods.json"  # 中文鍵值的食物 JSON
CUSTOM_MEAL_FILE = "data/custom_meals.json"  # 自訂餐點 JSON
DAILY_KCAL_TARGET = 2650
DAILY_PROTEIN_TARGET = 130
DAILY_CARBS_TARGET = 350

PROTEIN_FOODS = {
    "雞胸肉（100g）": 31,
    "茶葉蛋（1 顆）": 13,
    "無糖豆漿（1 瓶）": 10,
    "牛奶（1 杯）": 8
}

# ===== 載入食物清單 =====
def load_food_names():
    try:
        with open(FOOD_FILE, "r", encoding="utf-8") as f:
            foods = json.load(f)
        return list(foods.keys())
    except FileNotFoundError:
        return []

def load_custom_meals():
    try:
        with open(CUSTOM_MEAL_FILE, "r", encoding="utf-8") as f:
            meals = json.load(f)
        return meals
    except FileNotFoundError:
        return {}

foods = load_food_names()
custom_meals = load_custom_meals()
brands = list(custom_meals.keys())
meals_list = ["早餐", "午餐", "晚餐", "點心"]

# ===== 保存/刪除紀錄 =====
def save_log(food, grams, meal):
    today = selected_date.get()
    try:
        with open("data/logs.json", "r", encoding="utf-8") as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = {}

    if today not in logs:
        logs[today] = []

    logs[today].append({
        "meal": meal,
        "food": food,
        "grams": grams
    })

    with open("data/logs.json", "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

def delete_log(today, index):
    try:
        with open("data/logs.json", "r", encoding="utf-8") as f:
            logs = json.load(f)
    except FileNotFoundError:
        return

    if today in logs and 0 <= index < len(logs[today]):
        logs[today].pop(index)
        with open("data/logs.json", "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
            
            
# ===== 計算今日總營養 =====
def get_daily_total():
    today = selected_date.get()

    try:
        with open("data/logs.json", "r", encoding="utf-8") as f:
            logs = json.load(f)
    except FileNotFoundError:
        return None

    if today not in logs or not logs[today]:
        return None

    total = {
        "kcal": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0
    }

    # 一般食物資料
    with open(FOOD_FILE, "r", encoding="utf-8") as f:
        food_data = json.load(f)

    for item in logs[today]:

        # ============================
        # ✅ 一般食物（用克數算）
        # ============================
        if "grams" in item:
            food_name = item["food"]
            grams = item["grams"]

            if food_name in food_data:
                nutr = food_data[food_name]
                factor = grams / 100

                total["kcal"] += nutr["kcal"] * factor
                total["protein"] += nutr["protein"] * factor
                total["carbs"] += nutr["carbs"] * factor
                total["fat"] += nutr["fat"] * factor

        # ============================
        # ✅ 自訂餐點（直接加）
        # ============================
        else:
            total["kcal"] += item.get("kcal", 0)
            total["protein"] += item.get("protein", 0)
            total["carbs"] += item.get("carbs", 0)
            total["fat"] += item.get("fat", 0)

    return total


# ===== GUI 功能 =====
def add_food():
    food = selected_food.get()
    grams = entry_grams.get().strip()
    meal = selected_meal.get()

    # 如果沒輸入克數，就用 100g 當作一份
    if grams == "":
        # 直接從 JSON 裡拿營養值
        with open(FOOD_FILE, "r", encoding="utf-8") as f:
            food_data = json.load(f)

        if food not in food_data:
            messagebox.showerror("錯誤", "食物不存在，請選擇或輸入正確食物")
            return

        nutr = food_data[food]
        
        kcal = nutr["kcal"]
        protein = nutr["protein"]
        carbs = nutr["carbs"]
        fat = nutr["fat"]

        # 存進 logs.json
        today = selected_date.get()
        try:
            with open("data/logs.json", "r", encoding="utf-8") as f:
                logs = json.load(f)
        except FileNotFoundError:
            logs = {}

        if today not in logs:
            logs[today] = []

        logs[today].append({
            "meal": meal,
            "food": food,
            "kcal": kcal,
            "protein": protein,
            "carbs": carbs,
            "fat": fat
        })

        with open("data/logs.json", "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

        refresh_list()
        update_total()
        return

    # 如果有輸入克數（舊邏輯）
    if not grams.isdigit():
        messagebox.showerror("錯誤", "請輸入正確的克數或留空使用 100g")
        return

    save_log(food, int(grams), meal)
    refresh_list()
    update_total()
    entry_grams.delete(0, tk.END)


def add_custom_meal_record():
    meal = selected_meal.get()
    custom = selected_custom.get()
    try:
        ratio = float(entry_ratio.get())
    except ValueError:
        messagebox.showerror("錯誤", "請輸入正確比例")
        return

    data = custom_meals[selected_brand.get()][custom]
    kcal = data["kcal"] * ratio
    protein = data["protein"] * ratio
    carbs = data["carbs"] * ratio
    fat = data["fat"] * ratio

    today = selected_date.get()
    try:
        with open("data/logs.json", "r", encoding="utf-8") as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = {}

    if today not in logs:
        logs[today] = []

    logs[today].append({
        "meal": meal,
        "brand": selected_brand.get(),
        "food": custom,
        "kcal": kcal,
        "protein": protein,
        "carbs": carbs,
        "fat": fat
    })

    with open("data/logs.json", "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

    messagebox.showinfo("成功", f"已新增 {custom} (比例 {ratio})")
    refresh_list()
    update_total()

def delete_selected():
    selection = listbox_logs.curselection()
    if not selection:
        messagebox.showwarning("提醒", "請先選取一筆紀錄")
        return
    index = selection[0]
    today = selected_date.get()
    delete_log(today, index)
    refresh_list()
    update_total()

def refresh_list():
    listbox_logs.delete(0, tk.END)
    try:
        with open("data/logs.json", "r", encoding="utf-8") as f:
            logs = json.load(f)
    except FileNotFoundError:
        return

    today = selected_date.get()
    if today not in logs:
        return

    for item in logs[today]:
        
        # ======================
        # 一般食物（克數）
        # ======================
        if "grams" in item:
            text = f"{item['meal']} - {item['food']} ({item['grams']}g)"
            
        # ======================
        # 自訂餐點（kcal）
        # ======================
        
        else:
            text = f"{item['meal']} - {item.get('brand','')} {item['food']} ({item.get('kcal', 0):.0f} kcal)"
        listbox_logs.insert(tk.END, text)

def update_total():
    total = get_daily_total()

    # ======================
    # 尚無紀錄
    # ======================
    if total is None:
        label_result.config(text="今天尚無紀錄")

        progress_kcal["value"] = 0
        progress_protein["value"] = 0
        progress_carbs["value"] = 0

        label_kcal_status.config(
            text=f"熱量 0 / {DAILY_KCAL_TARGET} kcal",
            fg="black"
        )

        label_protein_status.config(
            text=f"蛋白質 0 / {DAILY_PROTEIN_TARGET} g",
            fg="black"
        )

        label_carbs_status.config(
            text=f"碳水 0 / {DAILY_CARBS_TARGET} g",
            fg="black"
        )

        
        return

    # ======================
    # 有資料
    # ======================
    kcal = total["kcal"]
    protein = total["protein"]
    carbs = total["carbs"]

    label_result.config(
        text=(
            f"🔥 熱量：{kcal:.1f} kcal\n"
            f"💪 蛋白質：{protein:.1f} g\n"
            f"🍚 碳水：{carbs:.1f} g"
        )
    )

    # ===== 進度條 =====
    progress_kcal["value"] = min(kcal, DAILY_KCAL_TARGET)
    progress_protein["value"] = min(protein, DAILY_PROTEIN_TARGET)
    progress_carbs["value"] = min(carbs, DAILY_CARBS_TARGET)

    # ===== 標籤 =====
    label_kcal_status.config(
        text=f"熱量 {kcal:.1f} / {DAILY_KCAL_TARGET} kcal",
        fg="black"
    )

    label_carbs_status.config(
        text=f"碳水 {carbs:.1f} / {DAILY_CARBS_TARGET} g",
        fg="black"
    )

    # ======================
    # ⭐ 蛋白質判斷（重點）
    # ======================
    label_protein_status.config(
    text=f"蛋白質 {protein:.1f} / {DAILY_PROTEIN_TARGET} g"
    )
    
    if protein < DAILY_PROTEIN_TARGET:
        remain = DAILY_PROTEIN_TARGET - protein

        label_protein_status.config(
            text=f"蛋白質 {protein:.1f} / {DAILY_PROTEIN_TARGET} g（尚缺 {remain:.1f} g）",
            fg="red"
        )

        # ===== 建議補充食物 =====
        suggest_text = "👉 建議補充：\n"
    
        for food, p in PROTEIN_FOODS.items():
            amount = remain / p
            if amount <= 3:  # 不顯示太誇張的數量
                suggest_text += f"• {food} 約 {amount:.1f} 份\n"
    
        label_food_suggest.config(text=suggest_text)
    
    else:
        label_protein_status.config(
            text=f"蛋白質 {protein:.1f} / {DAILY_PROTEIN_TARGET} g（已達標）",
            fg="green"
        )
    
        label_food_suggest.config(
            text="✅ 今天蛋白質攝取非常充足！"
        )



# ===== Tkinter GUI =====
root = tk.Tk()
root.title("健身飲食管理")
root.geometry("900x750")

selected_date = tk.StringVar(value=str(date.today()))
selected_meal = tk.StringVar(value=meals_list[0])
selected_food = tk.StringVar()
selected_custom = tk.StringVar(value=list(custom_meals.keys())[0] if custom_meals else "")

# ===============================
# 主框架（左右）
# ===============================
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

left_frame = tk.Frame(main_frame)
left_frame.pack(side="left", fill="y", padx=15, pady=10)

right_frame = tk.Frame(main_frame)
right_frame.pack(side="right", fill="both", expand=True, padx=15, pady=10)

# ===============================
# 左側：輸入區
# ===============================
tk.Label(left_frame, text="餐別").pack(anchor="w")
tk.OptionMenu(left_frame, selected_meal, *meals_list).pack(fill="x")

tk.Label(left_frame, text="選擇食物（克數計算）").pack(anchor="w", pady=(10, 0))
combobox_food = ttk.Combobox(left_frame, textvariable=selected_food, values=foods)
combobox_food.pack(fill="x")

def on_keyrelease(event):
    value = selected_food.get().strip()
    combobox_food["values"] = foods if value == "" else [f for f in foods if value in f]

combobox_food.bind("<KeyRelease>", on_keyrelease)

tk.Label(left_frame, text="輸入克數 (g)").pack(anchor="w")
entry_grams = tk.Entry(left_frame)
entry_grams.pack(fill="x")

tk.Button(left_frame, text="新增食物紀錄", command=add_food).pack(fill="x", pady=5)
# ===== 自訂餐點 — 餐廳選單 =====
tk.Label(left_frame, text="餐廳 / 類別").pack(anchor="w", pady=(15, 0))
selected_brand = tk.StringVar(value=brands[0] if brands else "")
combobox_brand = ttk.Combobox(left_frame, textvariable=selected_brand, values=brands, state="normal")
combobox_brand.pack(fill="x")


def on_brand_keyrelease(event):
    value = selected_brand.get().strip()

    if value == "":
        data = brands
    else:
        data = [b for b in brands if value in b]

    combobox_brand["values"] = data

combobox_brand.bind('<KeyRelease>', on_brand_keyrelease)

tk.Label(left_frame, text="餐點（自訂）").pack(anchor="w")
combobox_custom = ttk.Combobox(left_frame, textvariable=selected_custom, state="normal")

combobox_custom.pack(fill="x")

def on_custom_keyrelease(event):
    brand = selected_brand.get().strip()
    value = selected_custom.get().strip()

    if brand in custom_meals:
        all_meals = list(custom_meals[brand].keys())
    else:
        all_meals = []

    if value == "":
        data = all_meals
    else:
        data = [m for m in all_meals if value in m]

    combobox_custom["values"] = data

combobox_custom.bind('<KeyRelease>', on_custom_keyrelease)


def update_custom_meals(*args):
    brand = selected_brand.get()
    if brand in custom_meals:
        meal_names = list(custom_meals[brand].keys())
    else:
        meal_names = []
    combobox_custom["values"] = meal_names
    if meal_names:
        selected_custom.set(meal_names[0])
    else:
        selected_custom.set("")

selected_brand.trace("w", update_custom_meals)
update_custom_meals()


tk.Label(left_frame, text="份量比例（預設 1）").pack(anchor="w")
entry_ratio = tk.Entry(left_frame)
entry_ratio.insert(0, "1")
entry_ratio.pack(fill="x")

tk.Button(
    left_frame,
    text="新增自訂餐點紀錄",
    command=add_custom_meal_record
).pack(fill="x", pady=5)

# ===============================
# 右側：顯示區
# ===============================
tk.Label(right_frame, text="今日飲食清單").pack(anchor="w")
listbox_logs = tk.Listbox(right_frame, height=12)
listbox_logs.pack(fill="both", expand=True)

tk.Button(right_frame, text="刪除選取", command=delete_selected).pack(fill="x", pady=5)

label_kcal_status = tk.Label(right_frame, text=f"熱量 0 / {DAILY_KCAL_TARGET} kcal")
label_kcal_status.pack(anchor="w")
progress_kcal = ttk.Progressbar(
    right_frame, maximum=DAILY_KCAL_TARGET, length=400
)
progress_kcal.pack(fill="x")

label_protein_status = tk.Label(right_frame, text=f"蛋白質 0 / {DAILY_PROTEIN_TARGET} g")
label_protein_status.pack(anchor="w")
progress_protein = ttk.Progressbar(
    right_frame, maximum=DAILY_PROTEIN_TARGET
)



progress_protein.pack(fill="x")

label_carbs_status = tk.Label(right_frame, text=f"碳水 0 / {DAILY_CARBS_TARGET} g")
label_carbs_status.pack(anchor="w")
progress_carbs = ttk.Progressbar(
    right_frame, maximum=DAILY_CARBS_TARGET
)
progress_carbs.pack(fill="x")

label_result = tk.Label(right_frame, text="今天尚無紀錄", justify="left")
label_result.pack(anchor="w", pady=10)

label_food_suggest = tk.Label(
    right_frame,
    text="",
    justify="left",
    fg="#444"
)
label_food_suggest.pack(anchor="w", pady=5)

# ===============================
# 日期查詢
# ===============================
tk.Label(right_frame, text="📅 查詢日期").pack(anchor="w")

date_frame = tk.Frame(right_frame)
date_frame.pack(anchor="w")

entry_date = tk.Entry(date_frame, textvariable=selected_date, width=12)
entry_date.pack(side="left", padx=5)

def refresh_by_date():
    refresh_list()
    update_total()

def set_today():
    selected_date.set(str(date.today()))
    refresh_by_date()

def move_day(offset):
    d = datetime.strptime(selected_date.get(), "%Y-%m-%d").date()
    selected_date.set(str(d + timedelta(days=offset)))
    refresh_by_date()

tk.Button(date_frame, text="◀ 前一天", command=lambda: move_day(-1)).pack(side="left")
tk.Button(date_frame, text="今天", command=set_today).pack(side="left")
tk.Button(date_frame, text="後一天 ▶", command=lambda: move_day(1)).pack(side="left")

# ===============================
# 啟動
# ===============================
refresh_list()
update_total()
root.mainloop()

