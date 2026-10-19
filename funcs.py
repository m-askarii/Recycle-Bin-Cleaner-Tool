import os
import subprocess
import sys
from pathlib import Path
from collections import Counter
#-------------------------------------------------------------------------------
def line():
    print(40 * "-")
#-------------------------------------------------------------------------------
def is_windows():
    return os.name == "nt"
#-------------------------------------------------------------------------------
def get_extension_counts():
    ps_command = (
        "$shell = New-Object -ComObject Shell.Application; "
        "$bin = $shell.NameSpace(0xA); "
        "if ($bin) { "
        "    $bin.Items() | ForEach-Object { "
        "        if ($_.IsFolder) { '[FOLDER]' } "
        "        else { [System.IO.Path]::GetExtension($_.Name).ToLower() } "
        "    } "
        "}"
    )

    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_command],
        capture_output=True, text=True
    )

    extensions = [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    ]

    extensions = [ext if ext else "(no extension)" for ext in extensions]

    return Counter(extensions)
#-------------------------------------------------------------------------------
def show_extension_summary(counts):

    if not counts:
        print("\n[INFO] The Recycle Bin appears to be empty or unreadable.\n")
        line()
        print()
        return 0

    print("\n📂 Files in Recycle Bin by Extension:")
    print()

    for ext, num in counts.most_common():
        print(f"   {ext:<20} ->     {num} file(s)")

    total = sum(counts.values())
    print(f"\n   TOTAL: {total} file(s)\n")
    return total

#-------------------------------------------------------------------------------
def run_clear_recycle_bin():

    ps_cmd = "Clear-RecycleBin -Force -ErrorAction Stop"


    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_cmd],
        capture_output=True, text=True
    )

    return result.returncode, result.stderr.strip()
#-------------------------------------------------------------------------------
def main():

    if not is_windows():
        print("[ERROR] This tool only works on Windows 10/11.")
        return

    print("========================================")
    print("      🧹RecycleBinCleaner v1.0")
    print("========================================")

    counts = get_extension_counts()
    total = show_extension_summary(counts)
    if total == 0:
        print("Recycle bin is empty or an error in program.")
        print()
        return

    requ = input("Are you sure you want to empty the Recycle Bin? (if yes, y) >>> ")

    if "y" not in requ.lower():
        print("Canceled. No item deleted.")
        return

    print("\n[WORKING] Cleaning Recycle Bin, please wait...")
    code, err = run_clear_recycle_bin()

    # مرحله ۵: گزارش نتیجه
    if code == 0:
        print("[SUCCESS] Recycle Bin has been emptied successfully.")
        return
    else:
        print(f"[WARNING] PowerShell finished with code {code}.")

        if err:
            print("Details:", err)
            return
