import tkinter as tk
from tkinter import messagebox, ttk
import json
from datetime import date

# ===== 資料設定 =====
FOOD_FILE = "data/foods.json"  # 中文鍵值的食物 JSON
DAILY_KCAL_TARGET = 2650
DAILY_PROTEIN_TARGET = 130
DAILY_CARBS_TARGET = 350

# ===== 載入食物清單 =====
def load_food_names():
    try:
        with open(FOOD_FILE, "r", encoding="utf-8") as f:
            foods = json.load(f)
        return list(foods.keys())
    except FileNotFoundError:
        return []

foods = load_food_names()
meals = ["早餐", "午餐", "晚餐", "點心"]

# ===== 保存/刪除紀錄 =====
def save_log(food, grams, meal):
    today = str(date.today())
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
    today = str(date.today())
    try:
        with open("data/logs.json", "r", encoding="utf-8") as f:
            logs = json.load(f)
    except FileNotFoundError:
        return None

    if today not in logs or len(logs[today]) == 0:
        return None

    total = {"kcal":0, "protein":0, "carbs":0, "fat":0}
    with open(FOOD_FILE, "r", encoding="utf-8") as f:
        food_data = json.load(f)

    for item in logs[today]:
        food_name = item["food"]
        grams = item["grams"]
        if food_name in food_data:
            nutr = food_data[food_name]
            factor = grams / 100
            total["kcal"] += nutr["kcal"] * factor
            total["protein"] += nutr["protein"] * factor
            total["carbs"] += nutr["carbs"] * factor
            total["fat"] += nutr["fat"] * factor

    return total

# ===== GUI 功能 =====
def add_food():
    food = selected_food.get()
    grams = entry_grams.get()
    meal = selected_meal.get()

    if food not in foods:
        messagebox.showerror("錯誤", "食物不存在，請選擇或輸入正確食物")
        return

    if not grams.isdigit():
        messagebox.showerror("錯誤", "請輸入正確的克數")
        return

    save_log(food, int(grams), meal)
    refresh_list()
    update_total()
    entry_grams.delete(0, tk.END)

def delete_selected():
    selection = listbox_logs.curselection()
    if not selection:
        messagebox.showwarning("提醒", "請先選取一筆紀錄")
        return

    index = selection[0]
    today = str(date.today())
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

    today = str(date.today())
    if today not in logs:
        return

    for item in logs[today]:
        text = f"{item['meal']} - {item['food']} {item['grams']}g"
        listbox_logs.insert(tk.END, text)

def update_total():
    total = get_daily_total()
    if total is None:
        label_result.config(text="今天尚無紀錄")
        progress_kcal["value"] = 0
        progress_protein["value"] = 0
        progress_carbs["value"] = 0
        label_kcal_status.config(text=f"熱量 0 / {DAILY_KCAL_TARGET} kcal")
        label_protein_status.config(text=f"蛋白質 0 / {DAILY_PROTEIN_TARGET} g")
        label_carbs_status.config(text=f"碳水 0 / {DAILY_CARBS_TARGET} g")
        return

    kcal = total["kcal"]
    protein = total["protein"]
    carbs = total["carbs"]
    fat = total["fat"]

    label_result.config(
        text=f"🔥 熱量：{kcal:.1f} kcal\n💪 蛋白質：{protein:.1f} g\n🍚 碳水：{carbs:.1f} g\n🥑 脂肪：{fat:.1f} g"
    )

    # 更新進度條
    progress_kcal["value"] = min(kcal, DAILY_KCAL_TARGET)
    progress_protein["value"] = min(protein, DAILY_PROTEIN_TARGET)
    progress_carbs["value"] = min(carbs, DAILY_CARBS_TARGET)

    # 更新標籤
    label_kcal_status.config(text=f"熱量 {kcal:.1f} / {DAILY_KCAL_TARGET} kcal")
    label_protein_status.config(text=f"蛋白質 {protein:.1f} / {DAILY_PROTEIN_TARGET} g")
    label_carbs_status.config(text=f"碳水 {carbs:.1f} / {DAILY_CARBS_TARGET} g")

# ===== Tkinter GUI =====
root = tk.Tk()
root.title("健身飲食管理")
root.geometry("400x950")

# 餐別
selected_meal = tk.StringVar(value=meals[0])
tk.Label(root, text="餐別").pack(pady=5)
tk.OptionMenu(root, selected_meal, *meals).pack()

# 食物 Combobox（可打字即時篩選）
selected_food = tk.StringVar()
tk.Label(root, text="選擇食物").pack(pady=5)
combobox_food = ttk.Combobox(root, textvariable=selected_food)
combobox_food['values'] = foods
combobox_food['state'] = 'normal'
combobox_food.pack()

# ===== 自動篩選功能 =====
def on_keyrelease(event):
    value = selected_food.get().strip()
    if value == '':
        data = foods
    else:
        data = [item for item in foods if value in item]
    combobox_food['values'] = data

combobox_food.bind('<KeyRelease>', on_keyrelease)

# 克數輸入
tk.Label(root, text="輸入克數 (g)").pack(pady=5)
entry_grams = tk.Entry(root)
entry_grams.pack()

# 新增紀錄按鈕
tk.Button(root, text="新增紀錄", command=add_food).pack(pady=10)

# 今日飲食清單
tk.Label(root, text="今日飲食清單").pack(pady=5)
listbox_logs = tk.Listbox(root, width=35)
listbox_logs.pack(pady=5)
tk.Button(root, text="刪除選取", command=delete_selected).pack(pady=5)

# 熱量進度條
label_kcal_status = tk.Label(root, text=f"熱量 0 / {DAILY_KCAL_TARGET} kcal")
label_kcal_status.pack()
progress_kcal = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate", maximum=DAILY_KCAL_TARGET)
progress_kcal.pack(pady=5)

# 蛋白質進度條
label_protein_status = tk.Label(root, text=f"蛋白質 0 / {DAILY_PROTEIN_TARGET} g")
label_protein_status.pack()
progress_protein = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate", maximum=DAILY_PROTEIN_TARGET)
progress_protein.pack(pady=5)

# 碳水進度條
label_carbs_status = tk.Label(root, text=f"碳水 0 / {DAILY_CARBS_TARGET} g")
label_carbs_status.pack()
progress_carbs = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate", maximum=DAILY_CARBS_TARGET)
progress_carbs.pack(pady=5)

# 營養總覽
label_result = tk.Label(root, text="今天尚無紀錄", justify="left")
label_result.pack(pady=10)

# 啟動
refresh_list()
update_total()
root.mainloop()
