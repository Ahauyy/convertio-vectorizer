<div align="center">

# Convertio Vectorizer (PNG to SVG)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://microsoft.com/windows)
[![Tests: Passing](https://img.shields.io/badge/tests-6%20passed-brightgreen.svg)](tests/)

**High-fidelity raster-to-SVG vectorizer reverse-engineered from [Convertio](https://convertio.co/png-svg/) with seamless Windows Explorer right-click integration.**

[English](#english-overview) • [Bahasa Indonesia](#panduan-bahasa-indonesia)

</div>

---

## English Overview

**Convertio Vectorizer** transforms raster images (`.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`) with black fills and light/transparent backgrounds into clean, scalable vector graphics (`.svg`). 

Under the hood, Convertio's cloud engine relies on Peter Selinger's mathematical **Potrace algorithm**. This project reconstructs that exact tracing logic locally and integrates it directly into the **Windows Explorer Context Menu**—allowing you to convert any image into an SVG simply by right-clicking it.

### ✨ Key Features
- **Exact Convertio Logic**: Reconstructs Convertio's raster-to-vector curve fitting pipeline (`alphamax=1.0`, `opttolerance=0.2`, `turdsize=2`).
- **Smooth Bézier Curves**: Mathematical cubic Bézier curves (`C` and `c` SVG paths) that scale losslessly without pixelation.
- **Smart Transparency Handling**: Seamlessly composites RGBA transparency onto pure white backgrounds.
- **Inner Cutout & Hole Preservation**: Preserves geometric cutouts (e.g., donut shapes or inner loops of letters like B, O, P) using non-zero / evenodd path winding rules.
- **1-Click Right-Click Context Menu**: Converts images directly in your active directory in milliseconds without terminal popups (`pythonw.exe` silent execution).
- **No Administrator Rights Needed**: Installs safely into `HKEY_CURRENT_USER`.

---

## Panduan Bahasa Indonesia

### 🚀 Keunggulan Utama

1. **Logika Matematis Identik dengan Convertio:**
   - Menggunakan mesin kurva **Potrace Core Engine** yang sama persis dengan backend Convertio.
   - Menghasilkan kurva kubik Bézier yang halus tanpa sudut bergerigi atau distorsi.
   - Filter bintik noise (*turdsize*) untuk membersihkan artefak kompresi JPG.
2. **Sangat Praktis Digunakan:**
   - Cukup **Klik Kanan** pada file gambar di Windows Explorer mana pun -> pilih **"Convert to SVG"**.
   - File `.svg` langsung tercipta seketika di folder yang sama di samping file gambar Anda.
   - Berjalan *silent* di background menggunakan `pythonw.exe` tanpa jendela terminal hitam yang mengganggu.
3. **Instalasi 1-Klik Tanpa Butuh Hak Akses Administrator:**
   - Menggunakan registri `HKEY_CURRENT_USER\Software\Classes\SystemFileAssociations`.
   - Aman, bersih, dan dapat dihapus kapan saja dengan 1 klik.

---

## 📂 Struktur Proyek

```
convertio-vectorizer/
├── bin/
│   └── potrace.exe                # Core binary Potrace 1.16 Win64
├── src/
│   ├── __init__.py
│   ├── preprocessor.py            # ImagePreprocessor (Alpha, Grayscale, Thresholding, PBM)
│   ├── vectorizer.py              # ConvertioVectorizer (Potrace pipeline, curve parameters)
│   └── cli.py                     # CLI runner & Windows Explorer background execution
├── context_menu/
│   ├── icon.ico                   # Icon visual untuk context menu Explorer
│   ├── generate_icon.py           # Generator icon multi-resolusi
│   ├── register_menu.py           # Skrip manajemen registri Windows
│   ├── install_context_menu.bat   # 1-Klik Pasang menu klik kanan
│   └── uninstall_context_menu.bat # 1-Klik Hapus menu klik kanan
├── tests/
│   ├── test_vectorizer.py         # Automated test suite (6 unit & integration tests)
│   ├── generate_test_samples.py   # Generator gambar uji
│   └── test_samples/              # Folder file sampel uji (.png, .jpg, transparan)
├── docs/
│   └── WATERFALL_SPEC.md          # Spesifikasi teknis model Waterfall
├── pyproject.toml                 # Konfigurasi packaging proyek
├── requirements.txt               # Daftar dependensi Python
├── LICENSE                        # Lisensi MIT
└── README.md                      # Dokumentasi lengkap
```

---

## 🛠️ Cara Penggunaan

### 1. Menggunakan Klik Kanan di Windows Explorer (Rekomendasi)

1. Jalankan `context_menu/install_context_menu.bat` (atau `python context_menu/register_menu.py`).
2. Buka folder mana saja di komputer Anda yang berisi file gambar (`.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`).
3. **Klik Kanan** pada gambar tersebut:
   - **Windows 10:** Opsi **"Convert to SVG"** langsung terlihat dengan icon vektor.
   - **Windows 11:** Opsi terlihat di menu klik kanan langsung atau pada **"Show more options"** (shortcut: `Shift + F10` atau tahan tombol `Shift` saat klik kanan).
4. Klik **"Convert to SVG"**.
5. File `.svg` langsung tercipta di samping file gambar tersebut dalam hitungan milidetik!

### 2. Menggunakan Command Line (CLI)

```bash
# Konversi satu file (otomatis membuat [nama].svg di folder yang sama)
python src/cli.py path/ke/gambar.png

# Konversi banyak file sekaligus (batch)
python src/cli.py logo1.png logo2.jpg icon.webp

# Kustomisasi threshold luminansi (0-255, default 128)
python src/cli.py gambar.png --threshold 140

# Gunakan deteksi threshold otomatis (Otsu method)
python src/cli.py gambar.png --otsu

# Menentukan path output khusus
python src/cli.py logo.png -o hasil/logo_vector.svg
```

### 3. Menggunakan Python API

```python
from pathlib import Path
from vectorizer import ConvertioVectorizer

# Inisialisasi vectorizer
v = ConvertioVectorizer()

# Konversi gambar ke SVG
svg_path = v.convert_image("C:/path/ke/logo.png")
print(f"SVG berhasil dibuat: {svg_path}")
```

---

## 🧪 Pengujian & Verifikasi (Fase 4 Waterfall)

Jalankan rangkaian tes otomatis dengan:
```bash
python -m unittest tests/test_vectorizer.py
```

Hasil pengujian (6/6 Pass):
- ✅ **Test 1:** Pra-pemrosesan bitmap 1-bit PBM P4 binary berhasil.
- ✅ **Test 2:** PNG hitam-putih menghasilkan kurva Bézier `<path>` valid.
- ✅ **Test 3:** PNG dengan latar belakang transparan (RGBA) berhasil di-composite ke kanvas putih bersih.
- ✅ **Test 4:** JPG dengan noise kompresi berhasil dibersihkan dengan filter *turdsize*.
- ✅ **Test 5:** Objek berlubang (*donut / cutouts*) mempertahankan rongga dengan *sub-path winding* `evenodd`.
- ✅ **Test 6:** Eksekusi background `pythonw.exe` menghasilkan SVG secara instan tanpa window konsol.

---

## 🗑️ Cara Menghapus Menu Konteks

Jika sewaktu-waktu Anda ingin menghapus menu klik kanan tersebut:
Cukup jalankan file `context_menu/uninstall_context_menu.bat` (atau `python context_menu/register_menu.py --uninstall`). Registri Windows akan dibersihkan kembali secara total tanpa sisa.

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah lisensi [MIT](LICENSE).
Dikembangkan oleh **Axell Satria Elarie** ([@Ahauyy](https://github.com/Ahauyy)).
