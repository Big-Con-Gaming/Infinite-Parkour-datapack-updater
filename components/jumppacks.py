import shutil
import os
import traceback
import tarfile
from tkinter import messagebox
from components.util import get_custom_path, log_message, select_file, copy_to_clipboard


CACHE_DIR = os.path.join(os.path.expandvars("%LOCALAPPDATA%"), "Infinite-Parkour", "jumppack_cache")
EXCLUDED_FILES = {
    "command_storage_infinite_parkour.dat",
    "command_storage_infinite-parkour.dat",
    "command_storage_minecraft.dat",
    "command_storage_jumppack_0.2_showcase.dat",
    "command_storage_jumppack_base.dat",
}


def cache_jumppacks():
    log_message("Caching jumppacks...")
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
        pack_name = filename.replace("command_storage_", "").replace(".dat", ".jumppack")
        output_path = os.path.join(CACHE_DIR, pack_name)

        try:
            with tarfile.open(output_path, "w:gz") as tar:
                tar.add(source, arcname=filename)
            log_message(f"Cached jumppack: {output_path}")
        except Exception as e:
            log_message(f"Failed to cache {filename}: {e}")

def load_pack(pack):
    if not pack:
        return

    if not pack.lower().endswith(".jumppack"):
        messagebox.showerror("Error", "Please select a valid .jumppack file.")
        return

    world_path = get_custom_path()
    if not world_path or not os.path.isdir(world_path):
        messagebox.showerror("Error", "Cannot find world. Please ensure the path is correct and the world exists.")
        return

    data_path = os.path.join(world_path, "data")
    os.makedirs(data_path, exist_ok=True)

    log_message(f"Importing pack to: {data_path}")

    try:
        with tarfile.open(pack, "r:gz") as tar:
            members = tar.getmembers()

            if not members:
                raise RuntimeError("Jumppack is empty.")

            if len(members) != 1:
                raise RuntimeError("Jumppack format invalid. Expected exactly one file inside.")

            pack_base = os.path.splitext(os.path.basename(pack))[0]
            output_filename = f"command_storage_{pack_base}.dat"
            output_path = os.path.join(data_path, output_filename)

            if os.path.exists(output_path):
                messagebox.showerror(
                    "Error",
                    f"A jumppack named '{pack_base}' already exists in this world."
                )
                return

            member = members[0]

            extracted = tar.extractfile(member)
            if extracted is None:
                raise RuntimeError("Failed to read jumppack content.")

            with open(output_path, "wb") as target:
                target.write(extracted.read())

    except Exception as e:
        raise RuntimeError(f"Failed to import jumppack: {e}")

    messagebox.showinfo("Done", "Your jumppack has been imported.")
    log_message(f"Imported pack: {pack}")
    return True

def importpack():
    try:
        pack = select_file()
        load_pack(pack)

    except Exception as e:
        error_trace = traceback.format_exc()
        messagebox.showerror("Error", f"An error occurred.\n{e}")
        copy_to_clipboard(error_trace, True)
        log_message("Error occurred while importing pack:\n" + error_trace)


def exportpack():
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        cache_jumppacks()
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
        messagebox.showerror("Error", f"An error occurred.\n{e}")
        copy_to_clipboard(error_trace, True)
        log_message("Error occurred while exporting pack:\n" + error_trace)
