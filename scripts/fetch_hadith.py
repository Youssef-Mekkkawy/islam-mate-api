"""
Download Hadith data from fawazahmed0/hadith-api
License: Unlicense (Public Domain) - no restrictions
CDN: jsdelivr.net
"""

import requests
import json
import os
import time

CDN = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions"
OUTPUT_DIR = "data/hadith"
os.makedirs(OUTPUT_DIR, exist_ok=True)

COLLECTIONS = [
    {"id": "bukhari",   "en": "eng-bukhari",   "ar": "ara-bukhari",   "name": "Sahih al-Bukhari",      "arabic_name": "صحيح البخاري"},
    {"id": "muslim",    "en": "eng-muslim",    "ar": "ara-muslim",    "name": "Sahih Muslim",           "arabic_name": "صحيح مسلم"},
    {"id": "abudawud",  "en": "eng-abudawud",  "ar": "ara-abudawud",  "name": "Sunan Abi Dawud",        "arabic_name": "سنن أبي داود"},
    {"id": "tirmidhi",  "en": "eng-tirmidhi",  "ar": "ara-tirmidhi",  "name": "Jami at-Tirmidhi",       "arabic_name": "جامع الترمذي"},
    {"id": "ibnmajah",  "en": "eng-ibnmajah",  "ar": "ara-ibnmajah",  "name": "Sunan Ibn Majah",        "arabic_name": "سنن ابن ماجه"},
    {"id": "nasai",     "en": "eng-nasai",     "ar": "ara-nasai",     "name": "Sunan an-Nasai",         "arabic_name": "سنن النسائي"},
    {"id": "nawawi40",  "en": "eng-nawawi40",  "ar": "ara-nawawi40",  "name": "An-Nawawi 40 Hadith",    "arabic_name": "الأربعون النووية"},
    {"id": "malik",     "en": "eng-malik",     "ar": "ara-malik",     "name": "Muwatta Malik",          "arabic_name": "موطأ مالك"},
]


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
    if not en_data or not ar_data:
        return None

    en_hadiths = en_data.get("hadiths", [])
    ar_hadiths = ar_data.get("hadiths", [])

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
        "name": {"en": en_data.get("metadata", {}).get("name", ""), "ar": ar_data.get("metadata", {}).get("name", "")},
        "total": len(merged),
        "hadiths": merged
    }


index = []

for col in COLLECTIONS:
    print(f"\nDownloading: {col['name']}")

    en_file = f"{OUTPUT_DIR}/{col['id']}_en.json"
    ar_file = f"{OUTPUT_DIR}/{col['id']}_ar.json"
    merged_file = f"{OUTPUT_DIR}/{col['id']}.json"

    if os.path.exists(merged_file):
        print(f"  Already exists — skipping")
        with open(merged_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        index.append({
            "id": col["id"],
            "name": {"en": col["name"], "ar": col["arabic_name"]},
            "total": data.get("total", 0),
            "file": f"{col['id']}.json"
        })
        continue

    print(f"  Fetching English...")
    en_data = fetch(f"{CDN}/{col['en']}.json")
    time.sleep(1)

    print(f"  Fetching Arabic...")
    ar_data = fetch(f"{CDN}/{col['ar']}.json")
    time.sleep(1)

    if not en_data:
        print(f"  Skipping {col['id']} - no English data")
        continue

    merged = merge_ar_en(en_data, ar_data, col["id"])
    if not merged:
        print(f"  Skipping {col['id']} - merge failed")
        continue

    with open(merged_file, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    index.append({
        "id": col["id"],
        "name": {"en": col["name"], "ar": col["arabic_name"]},
        "total": merged["total"],
        "file": f"{col['id']}.json"
    })

    print(f"  Saved {merged['total']} hadiths")

with open(f"{OUTPUT_DIR}/index.json", "w", encoding="utf-8") as f:
    json.dump({
        "total_collections": len(index),
        "collections": index
    }, f, ensure_ascii=False, indent=2)

print(f"\nDone!")
print(f"Collections: {len(index)}")
for col in index:
    print(f"  {col['name']['en']}: {col['total']} hadiths")
print(f"\nUpload to HuggingFace:")
print(f"hf upload elprofessorai/islam-mate-data data/hadith data/hadith --repo-type=dataset")
