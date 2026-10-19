"""
generate_icon.py
================
Menghasilkan icon .ico profesional untuk menu klik kanan Windows Explorer 'Convert to SVG'.
"""

from pathlib import Path
from PIL import Image, ImageDraw


def create_vector_icon(output_path: Path):
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    images = []

    for w, h in sizes:
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Background rounded badge: warna ungu-indigo modern (mirip branding vector/Convertio)
        margin = max(1, w // 16)
        radius = max(2, w // 5)
        badge_box = [margin, margin, w - margin, h - margin]

        draw.rounded_rectangle(badge_box, radius=radius, fill=(99, 102, 241, 255))  # Indigo #6366f1

        # Gambar kurva pen-tool vector / simbol SVG
        scale = w / 32.0
        # Draw stylized vector path bezier node points
        p1 = (int(8 * scale), int(22 * scale))
        p2 = (int(14 * scale), int(10 * scale))
        p3 = (int(24 * scale), int(12 * scale))

        # Garis vektor
        draw.line([p1, p2, p3], fill=(255, 255, 255, 255), width=max(1, int(2 * scale)))

        # Node anchor boxes (kotak anchor bezier)
        node_radius = max(1, int(2 * scale))
        for px, py in [p1, p2, p3]:
            draw.rectangle(
                [px - node_radius, py - node_radius, px + node_radius, py + node_radius],
                fill=(255, 255, 255, 255),
                outline=(49, 46, 129, 255),
                width=max(1, int(0.5 * scale)),
            )

        images.append(img)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    images[0].save(
        output_path,
        format="ICO",
        sizes=[(img.width, img.height) for img in images],
        append_images=images[1:],
    )
    print(f"Icon created successfully: {output_path}")


if __name__ == "__main__":
    icon_path = Path(__file__).resolve().parent / "icon.ico"
    create_vector_icon(icon_path)
