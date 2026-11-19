#!/usr/bin/env python3
"""
BadTube Automated Build Pipeline
Compiles and patches YouTube stock APK into BadTube with Adblock, Background Audio, SponsorBlock, RYD, custom BadTube icon and GmsCore support.
"""

import os
import sys
import shutil
import subprocess
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = REPO_ROOT / "tools"
DIST_DIR = REPO_ROOT / "dist"
TEMP_DIR = REPO_ROOT / "temp_build"
ASSETS_DIR = REPO_ROOT / "assets"
LAUNCHER_BRANDING_DIR = ASSETS_DIR / "branding" / "launcher"

CLI_JAR_URL = "https://github.com/inotia00/revanced-cli/releases/download/v5.0.2/revanced-cli-5.0.2-all.jar"
PATCHES_URL = "https://github.com/inotia00/revanced-patches/releases/download/v5.14.1/patches-5.14.1.rvp"
TARGET_YT_VERSION = "20.05.46"

def download_file(url: str, dest: Path):
    if dest.exists() and dest.stat().st_size > 0:
        print(f"[+] Reusing existing: {dest.name}")
        return
    print(f"[*] Downloading {dest.name} from {url}...")
    dest.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, dest)
    print(f"[+] Download complete: {dest.name} ({dest.stat().st_size / (1024*1024):.2f} MB)")

def generate_branding_icons(source_logo: Path, out_dir: Path):
    densities = {
        "mipmap-mdpi": (48, 108),
        "mipmap-hdpi": (72, 162),
        "mipmap-xhdpi": (96, 216),
        "mipmap-xxhdpi": (144, 324),
        "mipmap-xxxhdpi": (192, 432),
    }
    src = Image.open(source_logo).convert("RGBA")
    
    for folder, (l_size, a_size) in densities.items():
        folder_path = out_dir / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        
        # Adaptive background
        bg = Image.new("RGBA", (a_size, a_size), (10, 10, 10, 255))
        bg.save(folder_path / "adaptiveproduct_youtube_background_color_108.png", "PNG")
        
        # Adaptive foreground
        fg = Image.new("RGBA", (a_size, a_size), (0, 0, 0, 0))
        target_fg_size = int(a_size * 0.68)
        scaled_logo_fg = src.resize((target_fg_size, target_fg_size), Image.Resampling.LANCZOS)
        offset_fg = ((a_size - target_fg_size) // 2, (a_size - target_fg_size) // 2)
        fg.paste(scaled_logo_fg, offset_fg, scaled_logo_fg)
        fg.save(folder_path / "adaptiveproduct_youtube_foreground_color_108.png", "PNG")
        
        # Round launcher
        round_icon = Image.new("RGBA", (l_size, l_size), (0, 0, 0, 0))
        round_mask = Image.new("L", (l_size, l_size), 0)
        draw_round = ImageDraw.Draw(round_mask)
        draw_round.ellipse((0, 0, l_size - 1, l_size - 1), fill=255)
        round_bg = Image.new("RGBA", (l_size, l_size), (10, 10, 10, 255))
        target_l_size = int(l_size * 0.72)
        scaled_logo_l = src.resize((target_l_size, target_l_size), Image.Resampling.LANCZOS)
        offset_l = ((l_size - target_l_size) // 2, (l_size - target_l_size) // 2)
        round_bg.paste(scaled_logo_l, offset_l, scaled_logo_l)
        round_icon.paste(round_bg, (0, 0), round_mask)
        round_icon.save(folder_path / "ic_launcher_round.png", "PNG")
        
        # Square launcher
        square_icon = Image.new("RGBA", (l_size, l_size), (0, 0, 0, 0))
        corner_radius = int(l_size * 0.22)
        square_mask = Image.new("L", (l_size, l_size), 0)
        draw_square = ImageDraw.Draw(square_mask)
        draw_square.rounded_rectangle((0, 0, l_size - 1, l_size - 1), radius=corner_radius, fill=255)
        square_bg = Image.new("RGBA", (l_size, l_size), (10, 10, 10, 255))
        square_bg.paste(scaled_logo_l, offset_l, scaled_logo_l)
        square_icon.paste(square_bg, (0, 0), square_mask)
        square_icon.save(folder_path / "ic_launcher.png", "PNG")

def find_apksigner():
    sdk_root = os.environ.get("ANDROID_SDK_ROOT") or os.environ.get("ANDROID_HOME")
    candidates = []
    if sdk_root:
        candidates.extend(Path(sdk_root).glob("build-tools/*/apksigner*"))
    default_win = Path(os.path.expanduser("~")) / "AppData" / "Local" / "Android" / "Sdk" / "build-tools"
    if default_win.exists():
        candidates.extend(default_win.glob("*/apksigner.bat"))
    
    candidates = [c for c in candidates if c.is_file() and not c.name.endswith(".jar")]
    if candidates:
        return str(sorted(candidates)[-1])
    
    return shutil.which("apksigner")

def build_badtube(input_apk_path: str):
    input_apk = Path(input_apk_path).resolve()
    if not input_apk.exists():
        print(f"[-] Error: Base APK not found at {input_apk}")
        sys.exit(1)

    TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    
    cli_jar = TOOLS_DIR / "revanced-cli.jar"
    patches_rvp = TOOLS_DIR / "patches.rvp"
    
    download_file(CLI_JAR_URL, cli_jar)
    download_file(PATCHES_URL, patches_rvp)
    
    # Generate branding icons
    logo_file = ASSETS_DIR / "Badtube.png"
    if logo_file.exists():
        print(f"[*] Generating branding icons from {logo_file.name}...")
        generate_branding_icons(logo_file, LAUNCHER_BRANDING_DIR)
        
    out_apk = DIST_DIR / f"BadTube-v{TARGET_YT_VERSION}.apk"
    
    print("[*] Starting BadTube bytecode patching...")
    cmd = [
        "java", "-Xmx4G", "-jar", str(cli_jar),
        "patch",
        f"-p={patches_rvp}",
        f"-o={out_apk}",
        f"-t={TEMP_DIR}",
        "--purge",
        "--unsigned",
        "-O", "appName=BadTube",
        "-e", "Custom branding name for YouTube",
        "-O", f"appIcon={LAUNCHER_BRANDING_DIR}",
        "-e", "Custom branding icon for YouTube",
        str(input_apk)
    ]
    
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"[-] Patching failed with exit code {res.returncode}")
        sys.exit(res.returncode)
        
    print("[*] Locating apksigner and keystore...")
    apksigner = find_apksigner()
    debug_keystore = Path(os.path.expanduser("~")) / ".android" / "debug.keystore"
    
    if apksigner and debug_keystore.exists():
        print(f"[+] Signing {out_apk.name} using {debug_keystore}...")
        sign_cmd = [
            str(apksigner), "sign",
            "--ks", str(debug_keystore),
            "--ks-pass", "pass:android",
            "--key-pass", "pass:android",
            "--ks-key-alias", "androiddebugkey",
            str(out_apk)
        ]
        res_sign = subprocess.run(sign_cmd)
        if res_sign.returncode == 0:
            print(f"[✓] Successfully built and signed: {out_apk}")
            return
            
    print(f"[!] Warning: Built unsigned APK at {out_apk}. Please sign before installation.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        base_apk = sys.argv[1]
    else:
        candidate = REPO_ROOT.parent / f"youtube-{TARGET_YT_VERSION.replace('.', '-')}.apk"
        if candidate.exists():
            base_apk = str(candidate)
        else:
            print("Usage: python build.py <path_to_youtube_stock_apk>")
            sys.exit(1)
            
    build_badtube(base_apk)
