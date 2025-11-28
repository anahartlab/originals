#!/usr/bin/env python3
# replace_header.py
import os, re, shutil, datetime

HTML_DIR = "."  # папка с html (текущая)
HEADER_FILE = (
    "header.txt"  # файл с новым header (должен содержать <header>...</header>)
)
BACKUP_SUFFIX = ".bak"  # суффикс бэкапа (будет добавлена метка времени)


def read_header():
    if not os.path.exists(HEADER_FILE):
        raise SystemExit(f"❌ Не найден {HEADER_FILE}")
    txt = open(HEADER_FILE, "r", encoding="utf-8").read()
    if "<header" not in txt.lower() or "</header>" not in txt.lower():
        raise SystemExit("❌ header.txt должен содержать тег <header>...</header>")
    return txt


def backup_path(path):
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{path}{BACKUP_SUFFIX}.{ts}"


def replace_header_in_file(path, new_header):
    txt = open(path, "r", encoding="utf-8").read()
    pattern = re.compile(r"(?is)(<header\b.*?>).*?(</header>)")
    if not pattern.search(txt):
        return False
    # делаем бэкап
    shutil.copy2(path, backup_path(path))
    new_txt = pattern.sub(new_header, txt, count=1)
    open(path, "w", encoding="utf-8").write(new_txt)
    return True


def main():
    new_header = read_header()
    files = [
        f
        for f in os.listdir(HTML_DIR)
        if f.lower().endswith(".html") and os.path.isfile(os.path.join(HTML_DIR, f))
    ]
    if not files:
        print("⚠️ HTML файлов не найдено в папке.")
        return
    replaced = 0
    skipped = []
    for fn in files:
        path = os.path.join(HTML_DIR, fn)
        ok = replace_header_in_file(path, new_header)
        if ok:
            print(f"✅ Обновлён: {fn}")
            replaced += 1
        else:
            print(f"— Пропущен (header не найден): {fn}")
            skipped.append(fn)
    print(f"\nГотово. Обновлено: {replaced}. Пропущено: {len(skipped)}.")


if __name__ == "__main__":
    main()
