import requests
import json
import os
import time

CDN = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions"
OUTPUT_DIR = "data/hadith"

def fetch(url):
    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            return response.json()
        print(f"  HTTP {response.status_code}: {url}")
        return None
    except Exception as e:
        print(f"  Failed: {e}")
        return None

def merge_ar_en(en_data, ar_data, collection_id):
    if not en_data:
        return None
    en_hadiths = en_data.get("hadiths", [])
    ar_hadiths = ar_data.get("hadiths", []) if ar_data else []
    ar_map = {h.get("hadithnumber"): h for h in ar_hadiths}
    merged = []
    for en_hadith in en_hadiths:
        num = en_hadith.get("hadithnumber")
        ar_hadith = ar_map.get(num, {})
        merged.append({
            "number": num,
            "grade": en_hadith.get("grades", [{}])[0].get("grade", "") if en_hadith.get("grades") else "",
            "text": {
                "en": en_hadith.get("text", ""),
                "ar": ar_hadith.get("text", "")
            },
            "reference": {
                "book": en_data.get("metadata", {}).get("name", ""),
                "hadith_number": num
            }
        })
    return {
        "collection": collection_id,
        "name": {
            "en": en_data.get("metadata", {}).get("name", "An-Nawawi 40 Hadith"),
            "ar": "الأربعون النووية"
        },
        "total": len(merged),
        "hadiths": merged
    }

print("Downloading Nawawi 40...")
en_data = fetch(f"{CDN}/eng-nawawi.json")
time.sleep(1)
ar_data = fetch(f"{CDN}/ara-nawawi.json")
time.sleep(1)

if en_data:
    merged = merge_ar_en(en_data, ar_data, "nawawi40")
    with open(f"{OUTPUT_DIR}/nawawi40.json", "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"Saved {merged['total']} hadiths")

    index_path = f"{OUTPUT_DIR}/index.json"
    with open(index_path, "r", encoding="utf-8") as f:
        index = json.load(f)

    nawawi_exists = any(c["id"] == "nawawi40" for c in index["collections"])
    if not nawawi_exists:
        index["collections"].append({
            "id": "nawawi40",
            "name": {"en": "An-Nawawi 40 Hadith", "ar": "الأربعون النووية"},
            "total": merged["total"],
            "file": "nawawi40.json"
        })
        index["total_collections"] = len(index["collections"])
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        print("Index updated")
else:
    print("Failed to download Nawawi")
