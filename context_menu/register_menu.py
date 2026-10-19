"""
register_menu.py
================
Skrip instalasi & uninstalasi Context Menu Windows Explorer ("Convert to SVG").
Menggunakan HKEY_CURRENT_USER sehingga:
1. TIDAK MEMERLUKAN HAK AKSES ADMINISTRATOR (Bisa diinstall langsung oleh user).
2. Bersih, aman, dan dapat dihapus kembali secara instan.
3. Terintegrasi langsung dengan klik kanan file .png, .jpg, .jpeg, .webp, .bmp di Windows Explorer.
"""

import sys
import os
from pathlib import Path
import winreg

MENU_KEY_NAME = "ConvertToSVG"
MENU_LABEL = "Convert to SVG"
EXTENSIONS = ["image", ".png", ".jpg", ".jpeg", ".webp", ".bmp"]


def get_paths():
    root_dir = Path(__file__).resolve().parent.parent
    cli_path = (root_dir / "src" / "cli.py").resolve()
    icon_path = (root_dir / "context_menu" / "icon.ico").resolve()

    # Gunakan pythonw.exe agar tidak ada window CMD hitam yang berkedip saat klik kanan
    python_exe = sys.executable
    pythonw_exe = Path(python_exe).parent / "pythonw.exe"
    if not pythonw_exe.exists():
        pythonw_exe = Path(python_exe)

    return {
        "root": root_dir,
        "cli": cli_path,
        "icon": icon_path,
        "pythonw": pythonw_exe,
    }


def register_context_menu():
    paths = get_paths()
    print("=" * 60)
    print("Memasang Windows Explorer Context Menu: 'Convert to SVG'")
    print("=" * 60)
    print(f"Runner CLI : {paths['cli']}")
    print(f"PythonW    : {paths['pythonw']}")
    print(f"Icon       : {paths['icon']}")

    command_str = f'"{paths["pythonw"]}" "{paths["cli"]}" --gui "%1"'

    success_count = 0
    for ext in EXTENSIONS:
        try:
            base_path = f"Software\\Classes\\SystemFileAssociations\\{ext}\\shell\\{MENU_KEY_NAME}"

            # Buat key menu utama
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, base_path) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, MENU_LABEL)
                if paths["icon"].exists():
                    winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, str(paths["icon"]))

            # Buat sub-key command
            cmd_path = f"{base_path}\\command"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, cmd_path) as cmd_key:
                winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, command_str)

            print(f"[OK] Terdaftar untuk asosiasi: {ext}")
            success_count += 1
        except Exception as e:
            print(f"[FAILED] Gagal mendaftarkan untuk {ext}: {e}")

    print("=" * 60)
    if success_count > 0:
        print("[SUKSES] Menu klik kanan 'Convert to SVG' berhasil dipasang!")
        print("Silakan klik kanan pada file gambar (.png/.jpg) di Windows Explorer.")
    else:
        print("[ERROR] Gagal memasang menu konteks.")
    print("=" * 60)


def unregister_context_menu():
    print("=" * 60)
    print("Menghapus Windows Explorer Context Menu: 'Convert to SVG'")
    print("=" * 60)

    removed_count = 0
    for ext in EXTENSIONS:
        base_path = f"Software\\Classes\\SystemFileAssociations\\{ext}\\shell\\{MENU_KEY_NAME}"
        cmd_path = f"{base_path}\\command"

        # Hapus sub-key command terlebih dahulu
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, cmd_path)
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"[NOTE] Gagal menghapus subkey command {ext}: {e}")

        # Hapus key utama
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, base_path)
            print(f"[OK] Dihapus dari asosiasi: {ext}")
            removed_count += 1
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"[NOTE] Gagal menghapus key {ext}: {e}")

    print("=" * 60)
    print(f"[SELESAI] Context menu telah dibersihkan ({removed_count} entri dihapus).")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() in ("--uninstall", "-u", "uninstall", "remove"):
        unregister_context_menu()
    else:
        register_context_menu()
