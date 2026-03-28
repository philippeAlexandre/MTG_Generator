import os
import subprocess
import requests

# To import the mana assets from Scryfall using its API
# Uses Inkscape for SVG --> PNG Conversion

OUTPUT_DIR = "assets/mana"
API_URL = "https://api.scryfall.com/symbology"
INKSCAPE_CMD = r"C:\Program Files\Inkscape\bin\inkscape.exe"

def safe_filename(symbol: str) -> str:
    return symbol.replace("/", "_").replace("{", "").replace("}", "")

def convert_svg_to_png(svg_path: str, png_path: str, size: int = 64):
    """
    Use Inkscape CLI to convert SVG → PNG at a fixed size.
    Preserves original padding and proportions.
    """
    cmd = [
        INKSCAPE_CMD,
        svg_path,
        "--export-type=png",
        f"--export-filename={png_path}",
        f"--export-width={size}",
        f"--export-height={size}",
    ]
    subprocess.run(cmd, check=True)

def download_and_convert():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Fetching symbol list from Scryfall…")
    data = requests.get(API_URL).json()
    symbols = data.get("data", [])
    print(f"Found {len(symbols)} symbols")

    for sym in symbols:
        symbol = sym["symbol"]          # e.g. "{W}", "{2/W}"
        svg_uri = sym["svg_uri"]        # direct SVG URL
        token = safe_filename(symbol)   # e.g. "W", "2_W"

        svg_path = os.path.join(OUTPUT_DIR, f"{token}.svg")
        png_path = os.path.join(OUTPUT_DIR, f"{token}.png")

        # Skip if PNG already exists
        if os.path.exists(png_path):
            print(f"[SKIP] {png_path} already exists")
            continue

        print(f"Downloading {symbol} → {svg_path}")
        resp = requests.get(svg_uri)
        resp.raise_for_status()
        with open(svg_path, "wb") as f:
            f.write(resp.content)

        print(f"Converting {svg_path} → {png_path}")
        convert_svg_to_png(svg_path, png_path, size=64)

    print("Done! All mana symbols downloaded and converted.")

if __name__ == "__main__":
    download_and_convert()