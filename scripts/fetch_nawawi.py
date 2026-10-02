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

print("Checking available editions...")
editions = fetch(f"https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions.json")
if editions:
    nawawi = [k for k in editions.keys() if "nawawi" in k.lower()]
    print(f"Nawawi editions: {nawawi}")
    forty = [k for k in editions.keys() if "forty" in k.lower() or "40" in k.lower()]
    print(f"Forty editions: {forty}")
