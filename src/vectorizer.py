"""
vectorizer.py
=============
Core Vectorizer Engine (Convertio Reverse Engineering).
Mengeksekusi pipeline:
1. Prapemrosesan gambar via ImagePreprocessor (transparansi, thresholding, binarisasi).
2. Konversi bitmap ke SVG kurva Bézier halus via Potrace dengan parameter yang sama persis dengan Convertio.
3. Post-processing SVG (opsi warna, viewBox, dan pembersihan tag jika diperlukan).
"""

from pathlib import Path
from typing import Optional, Union, Tuple
import os
import subprocess
import re

from preprocessor import ImagePreprocessor


class ConvertioVectorizer:
    def __init__(
        self,
        potrace_path: Optional[Union[str, Path]] = None,
        alphamax: float = 1.0,
        opttolerance: float = 0.2,
        turdsize: int = 2,
        fill_color: str = "#000000",
        threshold: int = 128,
        use_otsu: bool = False,
        invert: bool = False,
        auto_invert: bool = False,
        tight: bool = False,
    ):
        """
        Inisialisasi ConvertioVectorizer.

        :param potrace_path: Path ke executable potrace.exe. Jika None, auto-detect di folder bin/.
        :param alphamax: Parameter sudut kurva (default Convertio = 1.0).
        :param opttolerance: Toleransi optimasi kurva Bézier (default Convertio = 0.2).
        :param turdsize: Filter penekan noise/bintik piksel (default Convertio = 2).
        :param fill_color: Warna isi vektor (default #000000).
        :param threshold: Ambang batas luminansi (default 128).
        :param use_otsu: Menggunakan thresholding otomatis Otsu jika True.
        :param invert: Membalikkan binarisasi jika True.
        :param auto_invert: Mendeteksi otomatis background hitam jika True.
        :param tight: Menghapus margin kosong di sekeliling gambar jika True.
        """
        self.potrace_path = self._resolve_potrace_path(potrace_path)
        self.alphamax = alphamax
        self.opttolerance = opttolerance
        self.turdsize = turdsize
        self.fill_color = fill_color
        self.tight = tight

        self.preprocessor = ImagePreprocessor(
            threshold=threshold,
            use_otsu=use_otsu,
            invert=invert,
            auto_invert=auto_invert,
        )

    def _resolve_potrace_path(self, custom_path: Optional[Union[str, Path]]) -> Path:
        """Menemukan lokasi binary potrace.exe."""
        if custom_path:
            p = Path(custom_path).resolve()
            if p.exists():
                return p
            raise FileNotFoundError(f"Binary Potrace tidak ditemukan di: {p}")

        # Cari di folder bin/ sejajar dengan direktori root proyek
        current_dir = Path(__file__).resolve().parent
        candidates = [
            current_dir.parent / "bin" / "potrace.exe",
            current_dir / "bin" / "potrace.exe",
            Path(os.getcwd()) / "bin" / "potrace.exe",
        ]

        for cand in candidates:
            if cand.exists():
                return cand.resolve()

        # Coba cek di PATH sistem
        import shutil
        system_potrace = shutil.which("potrace")
        if system_potrace:
            return Path(system_potrace)

        raise FileNotFoundError(
            "Executable 'potrace.exe' tidak ditemukan di folder bin/ maupun di PATH sistem. "
            "Pastikan binary telah diletakkan di folder bin/."
        )

    def trace_pbm_to_svg(self, pbm_bytes: bytes, image_size: Tuple[int, int]) -> str:
        """
        Mengalirkan byte PBM ke potrace.exe dan mengembalikan string SVG.
        """
        cmd = [
            str(self.potrace_path),
            "--svg",
            "--alphamax", str(self.alphamax),
            "--opttolerance", str(self.opttolerance),
            "--turdsize", str(self.turdsize),
            "--color", self.fill_color,
            "-o", "-",  # output to stdout
        ]

        if self.tight:
            cmd.append("--tight")

        # Eksekusi proses tanpa menampilkan window terminal (khusus Windows)
        creationflags = 0
        if os.name == "nt":
            creationflags = subprocess.CREATE_NO_WINDOW

        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=creationflags,
        )

        stdout, stderr = proc.communicate(input=pbm_bytes)

        if proc.returncode != 0:
            err_msg = stderr.decode("utf-8", errors="replace")
            raise RuntimeError(f"Gagal memproses Potrace: {err_msg}")

        svg_content = stdout.decode("utf-8", errors="replace")
        return svg_content

    def convert_image(
        self,
        input_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
    ) -> Path:
        """
        Mengonversi gambar raster ke file SVG di folder yang sama (atau lokasi yang ditentukan).

        :param input_path: Path ke file gambar (.png, .jpg, dll.)
        :param output_path: Path output .svg. Jika None, otomatis menggunakan nama yang sama
                            di direktori file input.
        :return: Path ke file SVG yang dihasilkan.
        """
        in_p = Path(input_path).resolve()
        if not in_p.exists():
            raise FileNotFoundError(f"File input tidak ditemukan: {in_p}")

        if output_path is None:
            out_p = in_p.with_suffix(".svg")
        else:
            out_p = Path(output_path).resolve()

        # 1. Prapemrosesan gambar menjadi 1-bit PBM
        pbm_bytes, size = self.preprocessor.process(in_p)

        # 2. Vektorisasi via Potrace Engine
        svg_content = self.trace_pbm_to_svg(pbm_bytes, size)

        # 3. Tulis hasil SVG ke file target
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            f.write(svg_content)

        return out_p
