import zipfile
import os
import glob

OUTPUT_APK = "build/web/chainfall.apk" # Target name expected by index.html

print(f"Repacking {OUTPUT_APK}...")

# Create new zip (overwrite)
with zipfile.ZipFile(OUTPUT_APK, 'w', zipfile.ZIP_DEFLATED) as z:
    # 1. Add Python files to ROOT
    for py_file in glob.glob("*.py"):
        if "pygbag" in py_file or "repack" in py_file or "pack_assets" in py_file: continue
        print(f"Adding {py_file} to root")
        z.write(py_file, py_file)

    # 2. Add Assets to assets/ folder
    for root, dirs, files in os.walk("assets"):
        for f in files:
            full_path = os.path.join(root, f)
            # Maintain assets/ structure
            print(f"Adding {full_path}")
            z.write(full_path, full_path)

print("Repack complete.")
