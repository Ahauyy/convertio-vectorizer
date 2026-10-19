"""
cli.py
======
Command Line Interface & Windows Explorer Context Menu Runner.
Menerima argumen path file gambar, memproses konversi ke SVG via ConvertioVectorizer,
dan menyimpannya di folder yang sama dengan file aslinya.
"""

import sys
import os
from pathlib import Path
import argparse
import ctypes

# Tambahkan src ke sys.path jika dijalankan langsung
sys.path.insert(0, str(Path(__file__).resolve().parent))

from vectorizer import ConvertioVectorizer


def show_windows_alert(title: str, message: str, is_error: bool = False):
    """Menampilkan kotak dialog Windows native jika dijalankan dari GUI context menu."""
    icon_type = 0x10 if is_error else 0x40  # 0x10 = MB_ICONERROR, 0x40 = MB_ICONINFORMATION
    ctypes.windll.user32.MessageBoxW(0, message, title, icon_type | 0x0)


def main():
    parser = argparse.ArgumentParser(
        description="Convertio PNG/JPG to SVG Vectorizer (Windows Explorer Right-Click Integration)"
    )
    parser.add_argument(
        "images",
        nargs="+",
        help="Path ke satu atau lebih file gambar (.png, .jpg, .jpeg, .webp, .bmp)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Path output khusus (hanya jika mengonversi 1 file)",
    )
    parser.add_argument(
        "--threshold",
        "-t",
        type=int,
        default=128,
        help="Threshold luminansi binarisasi (0-255, default: 128)",
    )
    parser.add_argument(
        "--otsu",
        action="store_true",
        help="Gunakan algoritma Otsu untuk deteksi threshold otomatis",
    )
    parser.add_argument(
        "--invert",
        "-i",
        action="store_true",
        help="Balikkan warna binarisasi (jadikan putih sebagai foreground)",
    )
    parser.add_argument(
        "--auto-invert",
        action="store_true",
        help="Deteksi otomatis apakah background berwarna gelap",
    )
    parser.add_argument(
        "--color",
        "-c",
        default="#000000",
        help="Warna isi vektor SVG (default: #000000)",
    )
    parser.add_argument(
        "--alphamax",
        type=float,
        default=1.0,
        help="Parameter kelengkungan sudut (default: 1.0)",
    )
    parser.add_argument(
        "--opttolerance",
        type=float,
        default=0.2,
        help="Toleransi kurva Bézier (default: 0.2)",
    )
    parser.add_argument(
        "--turdsize",
        type=int,
        default=2,
        help="Pembersihan noise/bintik piksel (default: 2)",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Mode GUI/Context Menu (tampilkan dialog Windows jika error)",
    )

    args = parser.parse_args()

    try:
        vectorizer = ConvertioVectorizer(
            alphamax=args.alphamax,
            opttolerance=args.opttolerance,
            turdsize=args.turdsize,
            fill_color=args.color,
            threshold=args.threshold,
            use_otsu=args.otsu,
            invert=args.invert,
            auto_invert=args.auto_invert,
        )
    except Exception as e:
        if args.gui:
            show_windows_alert("Convertio SVG Error", f"Gagal menginisialisasi engine: {e}", is_error=True)
        else:
            print(f"[ERROR] Gagal inisialisasi: {e}", file=sys.stderr)
        sys.exit(1)

    success_count = 0
    errors = []

    for img_path_str in args.images:
        img_path = Path(img_path_str)
        if not img_path.exists():
            msg = f"File tidak ditemukan: {img_path}"
            errors.append(msg)
            print(f"[SKIP] {msg}", file=sys.stderr)
            continue

        target_out = None
        if args.output and len(args.images) == 1:
            target_out = Path(args.output)

        try:
            out_file = vectorizer.convert_image(img_path, target_out)
            success_count += 1
            print(f"[SUCCESS] {img_path.name} -> {out_file.name}")
        except Exception as e:
            msg = f"{img_path.name}: {e}"
            errors.append(msg)
            print(f"[ERROR] {msg}", file=sys.stderr)

    if errors and args.gui:
        show_windows_alert(
            "Convertio SVG Error",
            f"Terjadi kesalahan saat konversi:\n" + "\n".join(errors),
            is_error=True,
        )

    sys.exit(0 if success_count > 0 else 1)


if __name__ == "__main__":
    main()
