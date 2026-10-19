"""
generate_test_samples.py
========================
Membuat 4 jenis sampel uji gambar untuk validasi konversi raster ke SVG:
1. sample1_bw_logo.png: Logo monokrom hitam di atas background putih bersih.
2. sample2_transparent_icon.png: Ikon hitam di atas background transparan (RGBA).
3. sample3_noisy_shape.jpg: Gambar JPG dengan artefak kompresi.
4. sample4_donut_holes.png: Bentuk cincin dan donat dengan lubang (menguji winding rule / cutouts).
"""

from pathlib import Path
from PIL import Image, ImageDraw

SAMPLES_DIR = Path(__file__).resolve().parent / "test_samples"
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)


def create_samples():
    # 1. Sample 1: Black on White Logo
    img1 = Image.new("RGB", (200, 200), (255, 255, 255))
    draw1 = ImageDraw.Draw(img1)
    # Gambar bintang dan teks/kotak
    draw1.rectangle([40, 40, 160, 160], fill=(0, 0, 0))
    draw1.polygon([(100, 20), (120, 70), (170, 70), (130, 100), (150, 150), (100, 120), (50, 150), (70, 100), (30, 70), (80, 70)], fill=(0, 0, 0))
    path1 = SAMPLES_DIR / "sample1_bw_logo.png"
    img1.save(path1)
    print(f"Created {path1}")

    # 2. Sample 2: Transparent Icon (RGBA)
    img2 = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    draw2 = ImageDraw.Draw(img2)
    # Gambar siluet panah/gear
    draw2.ellipse([50, 50, 150, 150], fill=(0, 0, 0, 255))
    draw2.rectangle([90, 20, 110, 180], fill=(0, 0, 0, 255))
    draw2.rectangle([20, 90, 180, 110], fill=(0, 0, 0, 255))
    path2 = SAMPLES_DIR / "sample2_transparent_icon.png"
    img2.save(path2)
    print(f"Created {path2}")

    # 3. Sample 3: JPG with compression noise
    img3 = Image.new("RGB", (200, 200), (255, 255, 255))
    draw3 = ImageDraw.Draw(img3)
    draw3.polygon([(100, 30), (170, 170), (30, 170)], fill=(0, 0, 0))
    path3 = SAMPLES_DIR / "sample3_noisy_shape.jpg"
    img3.save(path3, quality=50)  # low quality JPG to create artifacts
    print(f"Created {path3}")

    # 4. Sample 4: Donut / Holes (menguji sub-path winding)
    img4 = Image.new("RGB", (200, 200), (255, 255, 255))
    draw4 = ImageDraw.Draw(img4)
    # Lingkaran luar hitam
    draw4.ellipse([30, 30, 170, 170], fill=(0, 0, 0))
    # Lubang dalam putih (menjadi lubang di SVG)
    draw4.ellipse([70, 70, 130, 130], fill=(255, 255, 255))
    path4 = SAMPLES_DIR / "sample4_donut_holes.png"
    img4.save(path4)
    print(f"Created {path4}")


if __name__ == "__main__":
    create_samples()
