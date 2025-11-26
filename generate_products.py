import os
import csv
import random
from bs4 import BeautifulSoup

# === Paths ===
repo_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(repo_root)

csv_path = "products.csv"
html_path = "main.html"
images_dir = "images"
valid_exts = {".jpg", ".jpeg", ".png"}

# === Load HTML ===
if not os.path.exists(html_path):
    print(f"❌ HTML-файл '{html_path}' не найден.")
    exit()

with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, "html.parser")

# === Удаляем ВСЕ секции старых товаров ===
for sec in soup.find_all("section", class_="u-clearfix u-section-16"):
    sec.decompose()

# === Удаляем старые <nav> с меню ===
for old_nav in soup.find_all("nav", class_="u-nav"):
    old_nav.decompose()

# === Удаляем возможную кнопку scroll-to-menu ===
for scroll_btn in soup.find_all(id="scroll-to-menu"):
    scroll_btn.decompose()

# Ищем Footer
footer_tag = soup.find("footer")
if not footer_tag:
    print("❌ В main.html нет <footer>")
    exit()

# === Чтение CSV ===
with open(csv_path, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile, delimiter=",")
    # нормализуем названия колонок
    reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]

    for row in reader:
        row = {k.strip().lower(): (v.strip() if v else "") for k, v in row.items()}

        name = row.get("name", "")
        if not name:
            continue

        folder_path = os.path.join(images_dir, name)
        if not os.path.isdir(folder_path):
            print(f"⚠️ Пропущен '{name}' — нет папки изображений.")
            continue

        all_images = [
            f
            for f in sorted(os.listdir(folder_path))
            if os.path.isfile(os.path.join(folder_path, f))
            and os.path.splitext(f)[1].lower() in valid_exts
        ]

        if not all_images:
            print(f"⚠️ Пропущен '{name}' — нет изображений.")
            continue

        images = random.sample(all_images, 5) if len(all_images) > 5 else all_images

        # ============= ПОЛЯ CSV =============
        title = row.get("title", "")
        description = row.get("description", "")
        size = row.get("size", "")
        date = row.get("date", "")
        price = row.get("price", "")
        material = row.get("material", "")
        paint = row.get("paint", "")
        type_p = row.get("type", "")
        place = row.get("place", "")

        seo_title = row.get("seo title", title)
        seo_description = row.get("seo description", "")
        seo_keywords = row.get("seo keywords", "")

        # ========= Форматированный текст =========
        full_description_html = (
            f"{description}<br>"
            f"Размер: {size} ({date} {place})<br>"
            f"({material}, {paint}, {type_p})<br>"
            f"Цена: {price}"
        )

        # ========= Создаём HTML блок =========
        carousel_id = f"carousel-{name[:8]}"
        carousel_items = ""
        carousel_indicators = ""

        for i, img in enumerate(images):
            active_class = "u-active" if i == 0 else ""

            indicator = f"""
<li data-u-target="#{carousel_id}" data-u-slide-to="{i}" 
class="{active_class} u-grey-70 u-shape-circle" 
style="width: 10px; height: 10px;"></li>"""

            carousel_indicators += indicator + "\n"

            item = f"""
<div class="{active_class} u-carousel-item u-gallery-item u-carousel-item-{i+1}">
  <div class="u-back-slide">
    <img class="u-back-image u-expanded" src="images/{name}/{img}">
  </div>
  <div class="u-align-center u-over-slide u-shading u-valign-bottom"></div>
</div>"""

            carousel_items += item + "\n"

        # Блок товара
        section_html = BeautifulSoup(
            f"""
<section class="u-clearfix u-section-16" id="{name}">
  <div class="u-clearfix u-sheet u-sheet-1">

    <h3 class="u-align-center u-text u-text-title">{seo_title}</h3>
    <p class="u-align-center u-text u-text-seo-description">{seo_description}</p>

    <p class="u-align-left u-text u-text-description">{full_description_html}</p>

    <!-- SEO Keywords (hidden) -->
    <p style="display:none;" class="seo-keywords">{seo_keywords}</p>

    <div class="custom-expanded u-carousel u-gallery" id="{carousel_id}">
      <ol class="u-carousel-indicators">{carousel_indicators}</ol>
      <div class="u-carousel-inner">{carousel_items}</div>
    </div>

  </div>
</section>
""",
            "html.parser",
        )

        footer_tag.insert_before(section_html)

# === Сохраняем результат ===
with open(html_path, "w", encoding="utf-8") as f:
    f.write(str(soup))

print("✅ Товары обновлены, старые удалены, новые добавлены.")
