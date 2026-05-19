import json
import re
import time
from pathlib import Path
from urllib.parse import quote

import requests

INPUT_FILE = Path("bonkler")  # your uploaded/saved HTML file
OUT_DIR = Path("bonkler_assets")
BASE_URL = "https://maker.remilia.org/thumbnail/Bonkler"

html = INPUT_FILE.read_text(encoding="utf-8", errors="replace")

match = re.search(r"source\s*=\s*JSON\.parse\(`(.+?)`\)", html, re.S)
if not match:
    raise RuntimeError("Could not find source = JSON.parse(...) in file")

source = json.loads(match.group(1))
layers = source["attributeLayers"]

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0"
})

for layer in layers:
    layer_name = layer["name"]
    names = layer["names"]

    layer_dir = OUT_DIR / layer_name
    layer_dir.mkdir(parents=True, exist_ok=True)

    for trait_name in names:
        filename = f"{layer_name}{trait_name}.webp"
        url = f"{BASE_URL}/{quote(filename)}"

        safe_name = re.sub(r'[\\/:*?"<>|]', "_", trait_name)
        out_path = layer_dir / f"{safe_name}.webp"

        if out_path.exists() and out_path.stat().st_size > 0:
            print("skip", out_path)
            continue

        print("downloading", url)

        try:
            r = session.get(url, timeout=20)
            if r.status_code == 200 and r.content:
                out_path.write_bytes(r.content)
                print("saved", out_path)
            else:
                print("failed", r.status_code, url)
        except Exception as e:
            print("error", url, e)

        time.sleep(0.1)

print("done")
