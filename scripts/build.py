#!/usr/bin/env python3
"""
BadTube Automated Build Pipeline
Compiles and patches YouTube stock APK into BadTube with Adblock, Background Audio, SponsorBlock, RYD, and GmsCore support.
"""

import os
import sys
import shutil
import subprocess
import urllib.request
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = REPO_ROOT / "tools"
DIST_DIR = REPO_ROOT / "dist"
TEMP_DIR = REPO_ROOT / "temp_build"

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
    
    system_tool = shutil.which("apksigner")
    return system_tool

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
            
    print(f"[!] Warning: Built unsigned APK at {out_apk}. Please sign with your own key before installation.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        base_apk = sys.argv[1]
    else:
        # Check standard location
        candidate = REPO_ROOT.parent / f"youtube-{TARGET_YT_VERSION.replace('.', '-')}.apk"
        if candidate.exists():
            base_apk = str(candidate)
        else:
            print("Usage: python build.py <path_to_youtube_stock_apk>")
            sys.exit(1)
            
    build_badtube(base_apk)
