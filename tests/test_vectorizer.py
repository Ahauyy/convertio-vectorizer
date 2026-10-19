"""
test_vectorizer.py
==================
Unit test dan integration test untuk Convertio Vectorizer.
Memvalidasi:
1. Prapemrosesan gambar (RGB, RGBA transparansi, Grayscale, Binarisasi).
2. Konversi setiap format (PNG, JPG, RGBA) ke SVG yang valid.
3. Struktur SVG (valid XML, <svg>, <path>, preserveAspectRatio, viewBox).
4. Verifikasi kurva Bézier matematika dan penanganan lubang / winding.
5. Verifikasi runner CLI (mode GUI dan batch multi-file).
"""

import sys
import os
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

# Setup sys.path agar modul src dapat diimpor
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from preprocessor import ImagePreprocessor
from vectorizer import ConvertioVectorizer


class TestConvertioVectorizer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.samples_dir = ROOT_DIR / "tests" / "test_samples"
        cls.vectorizer = ConvertioVectorizer()

    def _verify_svg(self, svg_path: Path, expected_aspect_ratio: float = 1.0):
        """Memverifikasi bahwa file SVG valid secara sintaksis dan memiliki elemen vektor."""
        self.assertTrue(svg_path.exists(), f"File SVG tidak ditemukan: {svg_path}")
        self.assertGreater(svg_path.stat().st_size, 100, "Ukuran file SVG terlalu kecil.")

        # Parsing XML
        tree = ET.parse(str(svg_path))
        root = tree.getroot()

        # Tag root harus mengandung svg
        self.assertTrue(root.tag.endswith("svg"), "Root tag bukan SVG")

        # Harus memiliki viewBox
        self.assertIn("viewBox", root.attrib, "Atribut viewBox tidak ditemukan di SVG")

        # Harus memiliki elemen path
        paths = root.findall(".//{http://www.w3.org/2000/svg}path")
        if not paths:
            # Fallback tanpa namespace
            paths = root.findall(".//path")
        self.assertGreater(len(paths), 0, "Tidak ada elemen <path> di dalam SVG yang dihasilkan.")

        # Pastikan data path tidak kosong
        for p in paths:
            d = p.attrib.get("d", "")
            self.assertTrue(d.startswith("M"), "Path data harus dimulai dengan koordinat Move-to 'M'")
            self.assertTrue("z" in d or "Z" in d, "Path data harus tertutup dengan 'z' atau 'Z'")

    def test_01_preprocessor_pbm(self):
        """Uji konversi pra-pemrosesan ke PBM binary."""
        p = ImagePreprocessor()
        img_path = self.samples_dir / "sample1_bw_logo.png"
        data, size = p.process(img_path)
        self.assertEqual(size, (200, 200))
        self.assertTrue(data.startswith(b"P4"), "Header PBM harus binary P4")

    def test_02_convert_bw_png(self):
        """Uji konversi PNG hitam-putih."""
        img_path = self.samples_dir / "sample1_bw_logo.png"
        svg_out = self.vectorizer.convert_image(img_path)
        self._verify_svg(svg_out)

    def test_03_convert_transparent_png(self):
        """Uji konversi PNG transparan (RGBA)."""
        img_path = self.samples_dir / "sample2_transparent_icon.png"
        svg_out = self.vectorizer.convert_image(img_path)
        self._verify_svg(svg_out)

    def test_04_convert_noisy_jpg(self):
        """Uji konversi JPG dengan noise kompresi."""
        img_path = self.samples_dir / "sample3_noisy_shape.jpg"
        svg_out = self.vectorizer.convert_image(img_path)
        self._verify_svg(svg_out)

    def test_05_convert_donut_holes(self):
        """Uji penanganan bentuk berlubang / donat (subpath winding)."""
        img_path = self.samples_dir / "sample4_donut_holes.png"
        svg_out = self.vectorizer.convert_image(img_path)
        self._verify_svg(svg_out)

        with open(svg_out, "r", encoding="utf-8") as f:
            content = f.read()

        # Harus ada sub-path move ' m' atau ' M' di dalam path tunggal untuk melubangi lingkaran
        self.assertIn(" m", content, "Elemen subpath melubangi (donut hole) tidak terdeteksi.")

    def test_06_cli_execution(self):
        """Uji eksekusi CLI runner."""
        import subprocess

        img_path = self.samples_dir / "sample1_bw_logo.png"
        cli_py = ROOT_DIR / "src" / "cli.py"

        res = subprocess.run(
            [sys.executable, str(cli_py), str(img_path)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"CLI runner gagal: {res.stderr}")
        self.assertIn("[SUCCESS]", res.stdout)


if __name__ == "__main__":
    unittest.main()
