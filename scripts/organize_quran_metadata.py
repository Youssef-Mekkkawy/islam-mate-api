import os
import shutil

DOWNLOADS = r"E:."  # Change this to where you downloaded the files
DEST = r"data\quran\metadata"
os.makedirs(DEST, exist_ok=True)

RENAME_MAP = {
    "quran-metadata-ayah.json":        "ayah.json",
    "quran-metadata-hizb.json":        "hizb.json",
    "quran-metadata-juz.json":         "juz.json",
    "quran-metadata-manzil.json":      "manzil.json",
    "quran-metadata-rub.json":         "rub.json",
    "quran-metadata-ruku.json":        "ruku.json",
    "quran-metadata-sajda.json":       "sajda.json",
    "quran-metadata-surah-name.json":  "surah_names.json",
}

for root, dirs, files in os.walk(DOWNLOADS):
    for file in files:
        if file in RENAME_MAP:
            src = os.path.join(root, file)
            dst = os.path.join(DEST, RENAME_MAP[file])
            shutil.copy2(src, dst)
            print(f"Copied: {file} -> {RENAME_MAP[file]}")
        elif file.endswith(".sqlite"):
            print(f"Skipped: {file}")

print("\nDone! Files in data/quran/metadata/:")
for f in os.listdir(DEST):
    print(f"  {f}")
