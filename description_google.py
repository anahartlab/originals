import os
import re
import requests
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import concurrent.futures
import time

# --- Auto paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_ROOT = os.path.join(BASE_DIR, "images")

GOOGLE_SHEET_ID = "1FOPOGC5UoPlRX3jLTGgO2PqNEug7hw1oVQ542DsN7fE"
SHEET_NAME = "sale"
SERVICE_ACCOUNT_FILE = "/Users/anahart/keys/google-sa.json"

API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "llava-next-34b"

# ---- Google Sheets ---
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
gc = gspread.authorize(credentials)
sheet = gc.open_by_key(GOOGLE_SHEET_ID).worksheet(SHEET_NAME)

df = pd.DataFrame(sheet.get_all_records())

def norm(s):
    return re.sub(r"\s+", "", s or "").lower()

columns = {norm(c): c for c in df.columns}

NAME_COL = next((columns[k] for k in columns if "name" in k), None)
TITLE_COL = next((columns[k] for k in columns if "title" in k), None)
DESC_COL = next((columns[k] for k in columns if "description" in k), None)

if not NAME_COL or not TITLE_COL or not DESC_COL:
    raise SystemExit("Required columns name/title/description not found.")

def ai_describe_image(image_path):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with open(image_path, "rb") as f:
                encoded = f.read()

            response = requests.post(
                API_URL,
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={
                    "model": MODEL,
                    "messages": [
                        {"role": "user", "content": "Опиши изображение максимально подробно и художественно."}
                    ],
                    "images": [encoded]
                }
            )

            response.raise_for_status()
            txt = response.json()["choices"][0]["message"]["content"]
            return txt.strip()
        except Exception as e:
            print(f"Error on attempt {attempt+1} for image {image_path}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                raise

def shorten(text):
    if len(text) <= 300:
        return text
    sentences = re.split(r"(?<=[.!?])\s+", text)
    out = ""
    for s in sentences:
        if len(out) + len(s) <= 300:
            out += s + " "
        else:
            break
    return out.strip()

def make_title(desc, used_titles):
    words = desc.split()
    base = " ".join(words[:3]).capitalize()
    title = base
    idx = 2
    while title in used_titles:
        idx += 1
        title = base + f" {idx}"
    used_titles.add(title)
    return title

used_titles = set(df[TITLE_COL].astype(str))

def process_folder(folder):
    folder_path = os.path.join(IMAGES_ROOT, folder)
    if not os.path.isdir(folder_path):
        return None

    main_img = None
    for f in ["main.jpg", "main.jpeg", "main.png"]:
        p = os.path.join(folder_path, f)
        if os.path.exists(p):
            main_img = p
            break

    if not main_img:
        print(f"⚠ No main image found in folder '{folder}'")
        return None

    row = df.index[df[NAME_COL].astype(str).str.lower() == folder.lower()]
    if len(row) == 0:
        return None

    idx = row[0]

    need_desc = not df.at[idx, DESC_COL]
    need_title = not df.at[idx, TITLE_COL]

    if need_desc or need_title:
        try:
            full = ai_describe_image(main_img)
        except Exception as e:
            print(f"Failed to generate description for folder '{folder}': {e}")
            return None
        desc_final = shorten(full)
        title_final = make_title(desc_final, used_titles)

        if need_desc:
            df.at[idx, DESC_COL] = desc_final
        if need_title:
            df.at[idx, TITLE_COL] = title_final

        print(f"Generated for '{folder}': Title: '{title_final}' | Description: '{desc_final}'")

    return None

folders = [f for f in os.listdir(IMAGES_ROOT) if os.path.isdir(os.path.join(IMAGES_ROOT, f))]

with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(process_folder, folders)

# ---- Write back to Google Sheets ----
cell_range = sheet.range(2, 1, len(df) + 1, len(df.columns))
flat = df.values.flatten().tolist()

for cell, val in zip(cell_range, flat):
    cell.value = val

sheet.update_cells(cell_range)
print("✔ Completed successfully.")
