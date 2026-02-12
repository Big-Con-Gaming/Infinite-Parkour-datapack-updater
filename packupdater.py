import os
import sys
import json
import shutil
import zipfile
import traceback
import subprocess
import urllib.request
from tkinter import Tk, END, messagebox
import tkinter.ttk as ttk
from components.util import copy_to_clipboard, log_message, get_custom_path, save_config, load_config, initialize as util_initialize
from components.gui import setup_buttons, initialize as gui_initialize


def download_and_extract_release(datapack_path):
    api_url = "https://api.github.com/repos/Big-Con-Gaming/Infinite-Parkour-datapack/releases/latest"
    zip_path = os.path.join(datapack_path, "temp.zip")

    os.makedirs(datapack_path, exist_ok=True)

    try:
        with urllib.request.urlopen(api_url) as resp:
            release = json.load(resp)

        zip_url = release["zipball_url"]

        urllib.request.urlretrieve(zip_url, zip_path)
        log_message(f"Downloaded zip file to {zip_path}")

        with zipfile.ZipFile(zip_path, "r") as zipf:
            zipf.extractall(datapack_path)

        log_message(f"Extracted datapack to {datapack_path}")

        extracted_items = os.listdir(datapack_path)
        if len(extracted_items) == 2 and "temp.zip" in extracted_items:
            extracted_items.remove("temp.zip")

        if len(extracted_items) == 1:
            top_dir = os.path.join(datapack_path, extracted_items[0])
            if os.path.isdir(top_dir):
                for item in os.listdir(top_dir):
                    shutil.move(os.path.join(top_dir, item), datapack_path)
                shutil.rmtree(top_dir)

    except Exception as e:
        log_message(f"Error downloading or extracting release: {e}")
        raise

    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)

def download_and_extract_latest_commit(datapack_path):
    zip_url = "https://github.com/Big-Con-Gaming/Infinite-Parkour-datapack/archive/refs/heads/main.zip"
    zip_path = os.path.join(datapack_path, "temp.zip")

    os.makedirs(datapack_path, exist_ok=True)

    try:

        urllib.request.urlretrieve(zip_url, zip_path)
        log_message(f"Downloaded zip file to {zip_path}")

        with zipfile.ZipFile(zip_path, "r") as zipf:
            zipf.extractall(datapack_path)

        log_message(f"Extracted datapack to {datapack_path}")

        extracted_items = os.listdir(datapack_path)
        if len(extracted_items) == 2 and "temp.zip" in extracted_items:
            extracted_items.remove("temp.zip")

        if len(extracted_items) == 1:
            top_dir = os.path.join(datapack_path, extracted_items[0])
            if os.path.isdir(top_dir):
                for item in os.listdir(top_dir):
                    shutil.move(os.path.join(top_dir, item), datapack_path)
                shutil.rmtree(top_dir)

    except Exception as e:
        log_message(f"Error downloading or extracting release: {e}")
        raise

    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)

def updatepack(dev_build=False):
    log_message("Starting updater...")
    try:
        custom_path = txt.get().strip()

        world_path, server = get_custom_path()
        if not world_path:
            return

        if custom_path:
            save_config(custom_path)

        datapacks_dir = os.path.join(world_path, "datapacks") if not server else os.path.join(world_path, "world", "datapacks")
        datapack_path = os.path.join(datapacks_dir, "infinite_parkour")

        if os.path.exists(datapacks_dir):
            shutil.rmtree(datapacks_dir)
        os.makedirs(datapacks_dir, exist_ok=True)
        if dev_build:
            download_and_extract_latest_commit(datapack_path)
        else:
            download_and_extract_release(datapack_path)

        os.chdir(datapack_path)
        subprocess.run([os.path.join(datapack_path, "build.bat")], shell=True, check=True)
        if dev_build:
            messagebox.showinfo("Done", "Latest commit downloaded!")
            log_message("Latest commit downloaded!")
        else:
            messagebox.showinfo("Done", "Update complete!")
            log_message("Update complete!")

    except Exception as e:
        error_trace = traceback.format_exc()
        print(error_trace)
        copy_to_clipboard(error_trace, True)
        log_message("Error occurred:\n" + error_trace)
        messagebox.showerror("Error", f"{e}\nAn error occurred.\nError copied to clipboard.")
    finally:
        os.chdir('c:\\')


def reset_config():
    config_path = os.path.join(os.path.expandvars("LOCALAPPDATA"), "Infinite-Parkour", "updaterconfig.json")
    if os.path.exists(config_path):
        os.remove(config_path)
    txt.delete(0, END)
    log_message("Config reset.")



def main():
    global root, txt, log_window, log_text

    root = Tk()
    root.title("Infinite Parkour - Pack Manager")
    root.geometry("400x260")
    root.resizable(False, False)
    log_window, log_text = gui_initialize(root, reset_config, updatepack)

    main_frame = ttk.Frame(root, padding=10)
    main_frame.grid(row=0, column=0, sticky="nsew")

    ttk.Label(main_frame, text="Minecraft Folder Path:").grid(row=0, column=0, columnspan=2, sticky="w")

    txt = ttk.Entry(main_frame, width=50)
    util_initialize(root, log_window, log_text, txt)
    txt.grid(row=1, column=0, sticky="ew", padx=(0, 5))
    txt.insert(0, load_config())

    setup_buttons(main_frame)

    root.mainloop()


if __name__ == "__main__":
    main()
