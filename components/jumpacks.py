import shutil
import os
import traceback
import tarfile
from tkinter import messagebox
from components.util import get_custom_path, log_message, select_file, copy_to_clipboard


CACHE_DIR = os.path.join(os.path.expandvars("%LOCALAPPDATA%"), "Infinite-Parkour", "jumpack_cache")
EXCLUDED_FILES = {
    "command_storage_infinite_parkour.dat",
    "command_storage_infinite-parkour.dat",
    "command_storage_minecraft.dat",
    "command_storage_jumppack_0.2_showcase.dat",
    "command_storage_jumppack_base.dat",
}


def cache_jumpacks():
    print("Caching jumpacks...")
    world_path = get_custom_path()
    if not world_path:
        return

    data_path = os.path.join(world_path, "data")
    if not os.path.isdir(data_path):
        log_message("Data folder not found in world.")
        return

    shutil.rmtree(CACHE_DIR, ignore_errors=True)
    os.makedirs(CACHE_DIR, exist_ok=True)

    for filename in os.listdir(data_path):
        if not filename.startswith("command_storage_") or not filename.endswith(".dat"):
            continue
        if filename in EXCLUDED_FILES:
            continue

        source = os.path.join(data_path, filename)
        pack_name = filename.replace("command_storage_", "").replace(".dat", ".jumpack")
        output_path = os.path.join(CACHE_DIR, pack_name)

        try:
            with tarfile.open(output_path, "w:gz") as tar:
                tar.add(source, arcname=filename)
            log_message(f"Cached jumpack: {output_path}")
        except Exception as e:
            log_message(f"Failed to cache {filename}: {e}")


def importpack():
    try:
        pack = select_file()
        if not pack:
            return
        if not pack.lower().endswith(".jumpack"):
            messagebox.showerror("Error", "Please select a valid .jumpack file.")
            return

        world_path = get_custom_path()
        if not world_path or not os.path.isdir(world_path):
            messagebox.showerror("Error", "Cannot find world. Please ensure the path is correct and the world exists.")
            return

        data_path = os.path.join(world_path, "data")
        os.makedirs(data_path, exist_ok=True)
        print(f"Importing pack to: {data_path}")

        with tarfile.open(pack, "r:gz") as tar:
            members = tar.getmembers()
            if not members:
                raise RuntimeError("Jumpack is empty.")
            for member in members:
                tar.extract(member, os.path.join(data_path, f'command_storage_{os.path.splitext(os.path.basename(pack))[0]}.dat'))

        messagebox.showinfo("Done", "Your jumpack has been imported.")
        log_message(f"Imported pack: {pack}")
        cache_jumpacks()

    except Exception as e:
        error_trace = traceback.format_exc()
        print(error_trace)
        messagebox.showerror("Error", f"An error occurred.\n{e}")
        copy_to_clipboard(error_trace, True)
        log_message("Error occurred while importing pack:\n" + error_trace)


def exportpack():
    cache_jumpacks()
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        pack = select_file(folder=CACHE_DIR)
        if not pack:
            return

        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        output_path = os.path.join(downloads, os.path.basename(pack))
        shutil.copy(pack, output_path)

        messagebox.showinfo("Done", "Export complete. File saved to Downloads.")
        log_message(f"Exported pack to: {output_path}")

    except Exception as e:
        error_trace = traceback.format_exc()
        print(error_trace)
        messagebox.showerror("Error", f"An error occurred.\n{e}")
        copy_to_clipboard(error_trace, True)
        log_message("Error occurred while exporting pack:\n" + error_trace)
