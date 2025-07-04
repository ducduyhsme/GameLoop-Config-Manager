import os
import shutil
import sys
import subprocess
import time

# =========================
# AndroidTBox Config Manager Script
# =========================
# This script lets you save configs to a custom directory and import/export AndroidTBox TVM_100.xml configs.
# It stores the chosen config directory in config_dir.txt for later use.
# It guides the user step by step and pauses for user input at every stage.

# --- 🟦 [ADDED] ---
# === Force Administrator Privilege at the very start ===
# This block relaunches the script with admin rights if not already admin.
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("Requesting administrator privileges...")
    # Relaunch the script with admin rights
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join([f'"{arg}"' for arg in sys.argv]), None, 1
    )
    sys.exit(0)
# --- 🟦 [END ADDED] ---

# --- 🟦 [ADDED] ---
# === Fix config_dir.txt location to be persistent for .exe conversions ===
# Use %APPDATA%\AndroidTBoxConfigManager\config_dir.txt for both .py and .exe versions
appdata = os.getenv('APPDATA')
persistent_config_folder = os.path.join(appdata, "AndroidTBoxConfigManager")
if not os.path.exists(persistent_config_folder):
    os.makedirs(persistent_config_folder)
config_dir_file = os.path.join(persistent_config_folder, "config_dir.txt")
# --- 🟥 [REMOVED]: use of script_dir/config_dir.txt, which doesn't work with .exe converters ---
# --- 🟦 [END ADDED] ---

# -------------------------
# 1. Check if first time use: config_dir.txt stores config directory
# -------------------------
# --- 🟦 [CHANGED] ---  
# Now uses persistent_config_folder location for config_dir.txt
if not os.path.exists(config_dir_file):
    config_dir = input("Where you want to save configs?\nEnter full path (no trailing slash): ").strip()
    if not config_dir:
        print("[ERROR] No directory entered. Exiting...")
        input("Press Enter to exit...")
        sys.exit(1)
    with open(config_dir_file, "w", encoding="utf-8") as f:
        f.write(config_dir)
else:
    with open(config_dir_file, "r", encoding="utf-8") as f:
        config_dir = f.read().strip()

# Ensure target config directory exists
if not os.path.exists(config_dir):
    try:
        os.makedirs(config_dir)
    except Exception as e:
        print(f"[ERROR] Cannot create directory '{config_dir}': {str(e)}")
        input("Press Enter to exit...")
        sys.exit(1)

# Get AndroidTBox appdata path
androidtbox_folder = os.path.join(appdata, "AndroidTBox")
tvm_100_path = os.path.join(androidtbox_folder, "TVM_100.xml")

# -------------------------
# 2. Main menu: import or export
# -------------------------
while True:
    print("\nSelect import or export config")
    print("1. Import")
    print("2. Export")
    choice = input("Enter your choice (1 or 2): ").strip()
    if choice in ('1', '2'):
        break
    print("Invalid choice. Please select 1 or 2.")

# If export, go to step 3
if choice == "2":
    # 3. Ask for config name
    configname = input("Enter the config name: ").strip()
    if not configname:
        print("Config name cannot be empty.")
        input("Press Enter to exit...")
        sys.exit(1)
    # 4. Copy TVM_100.xml to config dir with new name
    if not os.path.exists(tvm_100_path):
        print(f"[ERROR] '{tvm_100_path}' not found!")
        input("Press Enter to exit...")
        sys.exit(1)
    dest_path = os.path.join(config_dir, f"{configname}.xml")
    try:
        shutil.copyfile(tvm_100_path, dest_path)
    except Exception as e:
        print(f"[ERROR] Failed to copy config file: {str(e)}")
        input("Press Enter to exit...")
        sys.exit(1)
    print("Done! Press Enter to turn off window")
    input()
    sys.exit(0)

# -------------------------
# If import, go to step 6
# 6. List all .xml files in config directory
# -------------------------
xml_files = [f for f in os.listdir(config_dir) if f.lower().endswith('.xml')]
if not xml_files:
    print(f"No config files found in '{config_dir}'")
    input("Press Enter to exit...")
    sys.exit(1)

print("\nAvailable configs:")
for idx, fname in enumerate(xml_files, start=1):
    print(f"{idx}. {fname}")

# 6. Prompt user to select a file
while True:
    sel = input(f"Choose your desired config (enter a number 1-{len(xml_files)}): ").strip()
    if sel.isdigit():
        sel_int = int(sel)
        if 1 <= sel_int <= len(xml_files):
            break
    print("Invalid selection.")

selected_file = xml_files[sel_int - 1]
selected_path = os.path.join(config_dir, selected_file)

# 7. Copy selected file to AndroidTBox, replacing TVM_100.xml
try:
    if not os.path.exists(androidtbox_folder):
        os.makedirs(androidtbox_folder)
    if os.path.exists(tvm_100_path):
        os.remove(tvm_100_path)
    shutil.copyfile(selected_path, tvm_100_path)
except Exception as e:
    print(f"[ERROR] Failed to copy selected config: {str(e)}")
    input("Press Enter to exit...")
    sys.exit(1)

# =========================
# 7.1: Shut down "Gameloop" process (AppMarket.exe)
# =========================
gameloop_exe = os.path.join(os.environ.get('ProgramFiles', r'C:\Program Files'), r'TxGameAssistant\AppMarket\AppMarket.exe')

print("\nShutting down GameLoop (AppMarket.exe) process if running...")
try:
    subprocess.run(['taskkill', '/f', '/im', 'AppMarket.exe'], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except Exception as e:
    print(f"[INFO] Could not kill AppMarket.exe: {e}")

# =========================
# 7.1.1: Check and shut down "AndroidEmulatorEx.exe" if running
# =========================
androidemulator_exe = os.path.join(os.environ.get('ProgramFiles', r'C:\Program Files'), r'TxGameAssistant\ui\AndroidEmulatorEx.exe')
print("Checking and shutting down AndroidEmulatorEx.exe process if running...")
try:
    result = subprocess.run(['tasklist', '/fi', 'imagename eq AndroidEmulatorEx.exe'], capture_output=True, text=True)
    if "AndroidEmulatorEx.exe" in result.stdout:
        subprocess.run(['taskkill', '/f', '/im', 'AndroidEmulatorEx.exe'], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("AndroidEmulatorEx.exe was running and has been terminated.")
    else:
        print("AndroidEmulatorEx.exe is not running.")
except Exception as e:
    print(f"[INFO] Could not check or kill AndroidEmulatorEx.exe: {e}")

# =========================
# 7.2: Rerun AppMarket.exe
# =========================
print("Restarting GameLoop (AppMarket.exe)...")
try:
    subprocess.Popen([gameloop_exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except Exception as e:
    print(f"[ERROR] Could not start AppMarket.exe: {e}")

# =========================
# 7.3: Notify user to wait and allow closure
# =========================
print("")
print("")
print("Wait a moment to reset GameLoop")
print("(You can close the window by pressing any key)")
time.sleep(2)  # Give GameLoop a couple seconds to start up

input()

# =========================
# 8. Done message (removed, now shown after GameLoop steps above)
# =========================
