# Waterfall Development Specification: Convertio Vectorizer

Dokumentasi resmi alur pengembangan proyek menggunakan model **Waterfall** (Fase 1 s.d. 5).

---

## 1. Fase 1: Analisis Kebutuhan & Reverse Engineering
- **Target URL**: `https://convertio.co/png-svg/`
- **Tujuan**: Mengonversi gambar raster (`.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`) menjadi format vektor matematis `.svg` dengan akurasi dan karakteristik identik Convertio.
- **Hasil Reverse Engineering**:
  - Convertio menggunakan algoritma **Potrace Core Engine** untuk transformasi bitmap bi-level menjadi kurva kubik Bézier.
  - Parameter kurva identik:
    - Corner threshold (`alphamax`): `1.0`
    - Curve optimization tolerance (`opttolerance`): `0.2`
    - Speckle filter (`turdsize`): `2`
    - Nilai threshold luminansi default: `128` (50% luminance).

---

## 2. Fase 2: Perancangan Sistem & Arsitektur
- **Struktur Pipeline**:
  1. `ImagePreprocessor`: Menangani compositing alpha RGBA ke kanvas putih murni, konversi grayscale, dan binarisasi 1-bit PBM binary format (`P4`).
  2. `ConvertioVectorizer`: Mengalirkan PBM ke executable Potrace secara *headless* via stdin/stdout stream.
  3. `Windows Registry Shell Extension`: Menyediakan integrasi menu klik kanan di Windows Explorer via `HKCU\Software\Classes\SystemFileAssociations`.

---

## 3. Fase 3: Implementasi
- Binary Potrace 1.16 Win64 ditempatkan di `bin/potrace.exe`.
- Modul Python di `src/` (`preprocessor.py`, `vectorizer.py`, `cli.py`, `__init__.py`).
- Skrip Windows Context Menu di `context_menu/` (`install_context_menu.bat`, `uninstall_context_menu.bat`, `register_menu.py`, `icon.ico`).

---

## 4. Fase 4: Pengujian & Verifikasi
- 6 pengujian otomatis dijalankan via `unittest`:
  - `test_01_preprocessor_pbm`: Uji header dan ukuran PBM P4.
  - `test_02_convert_bw_png`: Uji konversi PNG hitam-putih.
  - `test_03_convert_transparent_png`: Uji konversi gambar RGBA transparan.
  - `test_04_convert_noisy_jpg`: Uji filtrasi noise kompresi JPG.
  - `test_05_convert_donut_holes`: Uji sub-path winding cutouts.
  - `test_06_cli_execution`: Uji eksekusi runner command-line.
- Seluruh 6 pengujian lolos 100%.

---

## 5. Fase 5: Deployment & Publikasi
- Pembuatan installer 1-klik untuk pengguna akhir.
- Konfigurasi open-source: `LICENSE` (MIT), `.gitignore`, `pyproject.toml`, `requirements.txt`.
- Publikasi repositori ke GitHub: `https://github.com/Ahauyy/convertio-vectorizer`.
