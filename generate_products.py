import os
import csv
import sys

# === Установка рабочей директории (если скрипт запущен не из корня репозитория) ===
repo_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(repo_root)

# === Параметры ===
csv_path = "products.csv"
html_path = "index.html"
images_dir = "images"
valid_exts = {".jpg", ".jpeg", ".png"}

# === Проверка HTML-файла ===
if not os.path.exists(html_path):
    print(f"❌ HTML-файл '{html_path}' не найден.")
    exit()


# === Читаем текущий HTML ===
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# === Очистка секций между </header> и <footer> ===
header_end = html_content.lower().find("</header>")
footer_start = html_content.lower().find("<footer")
if header_end != -1 and footer_start != -1 and header_end < footer_start:
    html_content = html_content[: header_end + 9] + html_content[footer_start:]

insert_index = html_content.lower().find("<footer")
if insert_index == -1:
    print("❌ Не найден <footer> index.html")
    exit()

# === Читаем CSV ===
with open(csv_path, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        name = row["Name"].strip()
        title = row["Title"].strip()
        description = row["Description"].strip()
        size = row["Size"].strip()
        paint = row["Paint"].strip()
        material = row["Material"].strip()
        type_ = row["Type"].strip()
        price = row["Price"].strip()
        place = row["Place"].strip()
        folder_path = os.path.join(images_dir, name)

        if not os.path.isdir(folder_path):
            print(f"⚠️  Пропущен '{name}' — папка '{folder_path}' не найдена.")
            continue

        images = [
            f
            for f in sorted(os.listdir(folder_path))
            if os.path.splitext(f)[1].lower() in valid_exts
        ]
        if not images:
            print(f"⚠️  Пропущен '{name}' — нет изображений.")
            continue

        # Удаление существующего блока по id="{name}"
        start_tag = f'<section class="u-clearfix u-section-16" id="{name}">'
        end_tag = "</section>"
        start_pos = html_content.find(start_tag)
        if start_pos != -1:
            end_pos = html_content.find(end_tag, start_pos)
            if end_pos != -1:
                html_content = (
                    html_content[:start_pos] + html_content[end_pos + len(end_tag) :]
                )
                insert_index = html_content.lower().find("<footer")

        carousel_id = f"carousel-{name[:8]}"
        carousel_indicators = ""
        carousel_items = ""

        for i, img_name in enumerate(images):
            active_class = "u-active" if i == 0 else ""
            indicator_li = f'<li data-u-target="#{carousel_id}" data-u-slide-to="{i}" class="{active_class} u-grey-70 u-shape-circle" style="width: 10px; height: 10px;"></li>'
            carousel_indicators += "                          " + indicator_li + "\n"

            item_div = f"""\
                          <div class="{active_class} u-carousel-item u-gallery-item u-carousel-item-{i+1}" data-image-width="960" data-image-height="1280">
                            <div class="u-back-slide">
                              <img class="u-back-image u-expanded" src="images/{name}/{img_name}">
                            </div>
                            <div class="u-align-center u-over-slide u-shading u-valign-bottom u-over-slide-{i+1}"></div>
                            <style data-mode="XL"></style>
                            <style data-mode="LG"></style>
                            <style data-mode="MD"></style>
                            <style data-mode="SM"></style>
                            <style data-mode="XS"></style>
                          </div>"""
            carousel_items += item_div + "\n"

        block = f"""
    <section class="u-clearfix u-section-16" id="{name}">
      <div class="u-clearfix u-sheet u-valign-middle-md u-valign-top-lg u-valign-top-xl u-sheet-1">
        <div class="data-layout-selected u-clearfix u-expanded-width u-layout-wrap u-layout-wrap-1">
          <div class="u-layout">
            <div class="u-layout-row">
              <div class="u-size-30">
                <div class="u-layout-col">
                  <div class="u-container-style u-layout-cell u-size-60 u-layout-cell-1">
                    <div class="u-container-layout u-valign-middle-lg u-valign-middle-sm u-valign-middle-xs u-container-layout-1">
                      <div class="custom-expanded u-carousel u-gallery u-gallery-slider u-layout-carousel u-lightbox u-no-transition u-show-text-none u-gallery-1" data-interval="5000" data-u-ride="carousel" id="{carousel_id}">
                        <ol class="u-absolute-hcenter u-carousel-indicators u-carousel-indicators-1">
{carousel_indicators}                        </ol>
                        <div class="u-carousel-inner u-gallery-inner u-gallery-inner-1" role="listbox">
{carousel_items}                        </div>
                        <a class="u-absolute-vcenter u-carousel-control u-carousel-control-prev u-grey-70 u-icon-circle u-opacity u-opacity-70 u-spacing-10 u-text-white u-carousel-control-1" href="#{carousel_id}" role="button" data-u-slide="prev">
                          <span aria-hidden="true">
                            <svg viewBox="0 0 451.847 451.847"><path d="..."/></svg></span><span class="sr-only">Previous</span>
                        </a>
                        <a class="u-absolute-vcenter u-carousel-control u-carousel-control-next u-grey-70 u-icon-circle u-opacity u-opacity-70 u-spacing-10 u-text-white u-carousel-control-2" href="#{carousel_id}" role="button" data-u-slide="next">
                          <span aria-hidden="true">
                            <svg viewBox="0 0 451.846 451.847"><path d="..."/></svg></span><span class="sr-only">Next</span>
                        </a>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="u-size-30">
                <div class="u-layout-col">
                  <div class="u-container-style u-layout-cell u-size-60 u-layout-cell-2">
                    <div class="u-container-layout u-container-layout-2">
                      <h3 class="u-align-center u-text u-text-1">{title}</h3>
                      <p class="u-align-left u-text u-text-2">{description}</p>
                      <p class="u-align-left u-text u-text-3">{size}</p>
                      <p class="u-align-left u-text u-text-4" style="font-size: smaller;">({paint}, {material}, {type_})</p>
                      <h3 class="u-align-left u-text u-text-5">{price} ₽</h3>
                      <p class="u-align-left u-text u-text-6">{place}</p>
                      <div class="u-align-center">
                        <a href="https://donate.stream/anahart" class="u-btn u-button-style u-custom-font u-heading-font u-hover-palette-1-light-1 u-palette-1-base u-radius-50 u-btn-1" style="border-radius: 100px;" title="Укажите нужную сумму и наименование товара в комментарии к донату">Оплатить</a>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>"""

        # === Вставка перед <footer> ===
        html_content = (
            html_content[:insert_index] + block + "\n" + html_content[insert_index:]
        )
        insert_index += len(block)

# === Добавление навигационного меню после </header> ===
nav_menu = "<nav class='u-nav u-unstyled' style='display:flex; justify-content:center; margin:20px 0;'><ul class='u-unstyled' style='list-style:none; padding:0; display:flex; flex-wrap:wrap; gap:15px;'>"
for name, title in [
    (row["Name"].strip(), row["Title"].strip())
    for row in csv.DictReader(open(csv_path, newline="", encoding="utf-8"))
]:
    nav_menu += f'<li><a href="#{name}">{title}</a></li>'
nav_menu += "</ul></nav>"

header_end = html_content.lower().find("</header>")
if header_end != -1:
    html_content = (
        html_content[: header_end + 9] + nav_menu + html_content[header_end + 9 :]
    )
else:
    html_content = nav_menu + html_content

# === Сохраняем результат ===
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ Все товары из CSV добавлены в index.html")
