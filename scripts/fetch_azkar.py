"""
Fetch Azkar data from hisnmuslim.com official API
Downloads AR + EN JSON + Audio files
"""

import requests
import json
import os
import time

AR_INDEX = "http://www.hisnmuslim.com/api/ar/husn_ar.json"
EN_INDEX = "http://www.hisnmuslim.com/api/en/husn_en.json"
AR_TEXT_BASE = "http://www.hisnmuslim.com/api/ar/{}.json"
EN_TEXT_BASE = "http://www.hisnmuslim.com/api/en/{}.json"

OUTPUT_DIR = "data/azkar"
AUDIO_DIR = "data/azkar/audio"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)


def fetch(url):
    try:
        response = requests.get(url, timeout=10)
        content = response.content.decode("utf-8-sig")
        return json.loads(content)
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None


def download_audio(url, filepath):
    if not url:
        return False
    if os.path.exists(filepath):
        return True
    try:
        response = requests.get(url, timeout=30, stream=True)
        if response.status_code == 200:
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"  Downloaded: {os.path.basename(filepath)}")
            return True
        return False
    except Exception as e:
        print(f"  Audio failed: {e}")
        return False


def slugify(title: str) -> str:
    replacements = {
        "أذكار الصباح والمساء": "morning_evening",
        "أذكار النوم": "sleep",
        "أذكار الاستيقاظ من النوم": "waking_up",
        "الأذكار بعد السلام من الصلاة": "after_prayer",
        "دعاء الاستفتاح": "opening_prayer",
        "دعاء الركوع": "ruku",
        "دعاء السجود": "sujood",
        "دعاء قنوت الوتر": "witr",
        "دعاء السفر": "travel",
        "دعاء دخول المنزل": "entering_home",
        "الذكر عند الخروج من المنزل": "leaving_home",
        "دعاء دخول المسجد": "entering_mosque",
        "دعاء الخروج من المسجد": "leaving_mosque",
        "دعاء الطعام": "food",
        "الدعاء عند الفراغ من الطعام": "after_food",
        "دعاء الهم والحزن": "anxiety",
        "دعاء الكرب": "distress",
        "دعاء المريض": "illness",
        "دعاء الغضب": "anger",
        "الاستغفار و التوبة": "forgiveness",
    }
    for ar, slug in replacements.items():
        if ar in title:
            return slug
    import re
    safe = re.sub(r'[^\w]', '_', title)
    return f"cat_{safe[:30]}"


print("Fetching Arabic index...")
ar_index = fetch(AR_INDEX)
if not ar_index:
    exit(1)

print("Fetching English index...")
en_index = fetch(EN_INDEX)
if not en_index:
    exit(1)

ar_categories = ar_index.get("العربية", [])
en_categories = en_index.get("English", [])
en_map = {item["ID"]: item for item in en_categories}

print(f"Found {len(ar_categories)} categories")

all_azkar = []

for ar_cat in ar_categories:
    cat_id = ar_cat["ID"]
    ar_title = ar_cat["TITLE"]
    cat_audio_url = ar_cat.get("AUDIO_URL", "")
    en_cat = en_map.get(cat_id, {})
    en_title = en_cat.get("TITLE", ar_title)
    slug = slugify(ar_title)

    print(f"\n[{cat_id}] {ar_title}")

    cat_audio_filename = ""
    if cat_audio_url:
        cat_audio_filename = f"{cat_id:03d}_{slug}.mp3"
        download_audio(cat_audio_url, f"{AUDIO_DIR}/{cat_audio_filename}")
        time.sleep(0.2)

    ar_text_data = fetch(AR_TEXT_BASE.format(cat_id))
    time.sleep(0.3)
    en_text_data = fetch(EN_TEXT_BASE.format(cat_id))
    time.sleep(0.3)

    if not ar_text_data:
        print(f"  Skipping - no data")
        continue

    ar_key = ar_title
    en_key = en_title

    ar_items = ar_text_data.get(ar_key, [])
    if not ar_items:
        keys = list(ar_text_data.keys())
        ar_items = ar_text_data.get(keys[0], []) if keys else []

    en_items = []
    if en_text_data:
        en_keys = list(en_text_data.keys())
        en_items = en_text_data.get(en_key, [])
        if not en_items and en_keys:
            en_items = en_text_data.get(en_keys[0], [])

    en_items_map = {item.get("ID"): item for item in en_items}

    azkar_list = []
    for ar_item in ar_items:
        item_id = ar_item.get("ID")
        en_item = en_items_map.get(item_id, {})
        item_audio_url = ar_item.get("AUDIO_URL", "")

        item_audio_filename = ""
        if item_audio_url:
            item_audio_filename = f"{cat_id:03d}_{item_id:03d}.mp3"
            download_audio(item_audio_url, f"{AUDIO_DIR}/{item_audio_filename}")
            time.sleep(0.2)

        azkar_list.append({
            "id": item_id,
            "repeat": ar_item.get("COUNT", 1),
            "source": ar_item.get("FADL", ""),
            "transliteration": "",
            "audio_url": item_audio_url,
            "audio_file": item_audio_filename,
            "translations": {
                "ar": {
                    "text": ar_item.get("ARABIC_TEXT", ar_item.get("TEXT", "")),
                    "description": ar_item.get("FADL", "")
                },
                "en": {
                    "text": en_item.get("TEXT", ""),
                    "description": en_item.get("FADL", "")
                }
            }
        })

    category_data = {
        "id": cat_id,
        "slug": slug,
        "audio_url": cat_audio_url,
        "audio_file": cat_audio_filename,
        "title": {
            "ar": ar_title,
            "en": en_title
        },
        "azkar": azkar_list
    }

    filename = f"{OUTPUT_DIR}/{cat_id:03d}_{slug}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(category_data, f, ensure_ascii=False, indent=2)

    all_azkar.append({
        "id": cat_id,
        "slug": slug,
        "title": {"ar": ar_title, "en": en_title},
        "audio_url": cat_audio_url,
        "audio_file": cat_audio_filename,
        "count": len(azkar_list),
        "file": f"{cat_id:03d}_{slug}.json"
    })

    print(f"  Saved {len(azkar_list)} azkar")

with open(f"{OUTPUT_DIR}/index.json", "w", encoding="utf-8") as f:
    json.dump({"total": len(all_azkar), "categories": all_azkar}, f, ensure_ascii=False, indent=2)

print(f"\nDone! {len(all_azkar)} categories")
