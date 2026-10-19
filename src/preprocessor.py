"""
preprocessor.py
==============
Modul prapemrosesan gambar untuk Convertio Vectorizer.
Bertanggung jawab untuk:
1. Membaca berbagai format gambar (PNG, JPG, JPEG, WEBP, BMP, dll.)
2. Menangani transparansi (Alpha channel) dengan compositing ke latar belakang putih bersih.
3. Mengonversi ke grayscale dan binarisasi (thresholding) agar menghasilkan 1-bit bitmap murni.
4. Mendukung auto-invert atau manual invert jika objek berwarna terang pada latar belakang gelap.
5. Menghasilkan format PBM (Portable Bitmap P4) yang dioptimasi untuk input Potrace.
"""

from pathlib import Path
from typing import Optional, Tuple, Union
import io
from PIL import Image


class ImagePreprocessor:
    def __init__(
        self,
        threshold: int = 128,
        use_otsu: bool = False,
        invert: bool = False,
        auto_invert: bool = False,
    ):
        """
        Inisialisasi preprocessor gambar.

        :param threshold: Ambang batas luminansi (0-255). Default 128 (50% luminance).
        :param use_otsu: Jika True, hitung threshold optimal menggunakan metode Otsu.
        :param invert: Jika True, balikkan warna (jadikan putih sebagai foreground).
        :param auto_invert: Jika True, periksa warna tepi/sudut untuk mendeteksi latar belakang gelap.
        """
        self.threshold = threshold
        self.use_otsu = use_otsu
        self.invert = invert
        self.auto_invert = auto_invert

    def _calculate_otsu_threshold(self, gray_img: Image.Image) -> int:
        """Menghitung nilai threshold optimal menggunakan algoritma Otsu."""
        histogram = gray_img.histogram()
        total_pixels = gray_img.width * gray_img.height

        current_max = 0.0
        threshold_val = 128
        sum_total = sum(i * histogram[i] for i in range(256))
        sum_background = 0.0
        weight_background = 0
        weight_foreground = 0

        for t in range(256):
            weight_background += histogram[t]
            if weight_background == 0:
                continue

            weight_foreground = total_pixels - weight_background
            if weight_foreground == 0:
                break

            sum_background += t * histogram[t]
            mean_background = sum_background / weight_background
            mean_foreground = (sum_total - sum_background) / weight_foreground

            between_variance = (
                weight_background
                * weight_foreground
                * ((mean_background - mean_foreground) ** 2)
            )

            if between_variance > current_max:
                current_max = between_variance
                threshold_val = t

        return threshold_val

    def _should_auto_invert(self, gray_img: Image.Image, threshold: int) -> bool:
        """
        Memeriksa 4 sudut dan tepian gambar untuk menentukan apakah latar belakangnya hitam.
        Jika latar belakang gelap, maka perlu dibalikkan agar objek utama menjadi foreground.
        """
        w, h = gray_img.size
        sample_points = [
            (0, 0),
            (w - 1, 0),
            (0, h - 1),
            (w - 1, h - 1),
            (w // 2, 0),
            (w // 2, h - 1),
            (0, h // 2),
            (w - 1, h // 2),
        ]
        dark_samples = 0
        for x, y in sample_points:
            pixel = gray_img.getpixel((x, y))
            if pixel < threshold:
                dark_samples += 1

        # Jika lebih dari 50% titik tepi berwarna gelap, anggap background gelap
        return dark_samples > (len(sample_points) / 2)

    def process(
        self,
        image_input: Union[str, Path, Image.Image],
    ) -> Tuple[bytes, Tuple[int, int]]:
        """
        Memproses gambar input menjadi byte PBM (Portable Bitmap P4) 1-bit.

        :param image_input: Path file gambar atau objek PIL.Image.
        :return: Tuple (pbm_bytes, (width, height))
        """
        if isinstance(image_input, (str, Path)):
            img = Image.open(str(image_input))
        else:
            img = image_input

        # 1. Penanganan Transparansi (Alpha channel)
        # Convertio memperlakukan latar transparan sebagai latar putih
        if img.mode in ("RGBA", "LA") or (
            img.mode == "P" and "transparency" in img.info
        ):
            rgba = img.convert("RGBA")
            # Buat background putih bersih
            white_bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
            # Alpha composite: gabungkan gambar di atas background putih
            composite = Image.alpha_composite(white_bg, rgba)
            rgb_img = composite.convert("RGB")
        else:
            rgb_img = img.convert("RGB")

        # 2. Konversi ke Grayscale (Luminansi)
        gray_img = rgb_img.convert("L")

        # 3. Tentukan nilai threshold
        active_threshold = self.threshold
        if self.use_otsu:
            active_threshold = self._calculate_otsu_threshold(gray_img)

        # 4. Deteksi apakah perlu di-invert
        invert_flag = self.invert
        if self.auto_invert and self._should_auto_invert(gray_img, active_threshold):
            invert_flag = not invert_flag

        # 5. Binarisasi (1-bit thresholding)
        # Dalam Potrace:
        # Nilai 0 (Hitam) pada PBM adalah FOREGROUND yang akan di-trace menjadi vektor.
        # Nilai 255 (Putih) adalah BACKGROUND.
        if invert_flag:
            # Objek terang di atas gelap: pixel >= threshold dijadikan foreground
            lookup = [0 if i >= active_threshold else 255 for i in range(256)]
        else:
            # Standar: Objek gelap (black fill) di atas putih (white background)
            lookup = [0 if i < active_threshold else 255 for i in range(256)]

        binary_img = gray_img.point(lookup, mode="1")

        # 6. Simpan ke buffer format PBM P4 (binary)
        pbm_buffer = io.BytesIO()
        binary_img.save(pbm_buffer, format="PPM")  # PIL handles PBM via PPM/PBM encoder
        pbm_bytes = pbm_buffer.getvalue()

        return pbm_bytes, binary_img.size
