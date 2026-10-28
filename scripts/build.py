"""Package only public files for GitHub Pages; Python standard library only."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "_site"
OUTPUT.mkdir(exist_ok=True)
for name in ("index.html", "404.html", "robots.txt", "sitemap.xml", ".nojekyll"):
    shutil.copy2(ROOT / name, OUTPUT / name)
for name in ("assets", "css", "js", "html"):
    shutil.copytree(ROOT / name, OUTPUT / name, dirs_exist_ok=True)
print(f"Site packaged in {OUTPUT}")
