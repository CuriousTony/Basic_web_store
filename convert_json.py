# конвертер json-файла под формат модели Bouquet

import json
import os
from urllib.parse import quote
from urllib.request import urlretrieve
from urllib.error import URLError, HTTPError

INPUT_FILE = "pions.json"
OUTPUT_FILE = "pions_fixture.json"
MEDIA_DIR = "media/bouquets"

os.makedirs(MEDIA_DIR, exist_ok=True)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

result = []
for idx, item in enumerate(data, 1):
    try:
        raw_url = item["image_url"]
        encoded_url = quote(raw_url, safe=":/?&=")

        filename = f"pion_bouquet_{idx}.jpg"
        filepath = os.path.join(MEDIA_DIR, filename)
        urlretrieve(encoded_url, filepath)

        entry = {
            "model": "catalog.bouquet",
            "pk": None,
            "fields": {
                "name": item["title"],
                "consists": item["composition"],
                "price": float(item["price"]),
                "pic1": f"bouquets/{filename}",
                "pic2": "",
                "is_bestseller": False
            }
        }
        result.append(entry)

    except (KeyError, URLError, HTTPError) as e:
        print(f"Ошибка обработки элемента {idx}: {str(e)}")
        continue

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"Успешно обработано: {len(result)}/{len(data)} записей")
