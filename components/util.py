import os, json, fnmatch
from tkinter import END, messagebox, filedialog

def initialize(root_, log_window_, log_text_, txt_):
    global root, log_window, log_text, txt
    root = root_
    log_window = log_window_
    log_text = log_text_
    txt = txt_

def copy_to_clipboard(text, silent=False):
    root.clipboard_clear()
    root.clipboard_append(str(text))
    if not silent:
        messagebox.showinfo("Copied", "Copied to clipboard")


def log_message(message):
    print(message)
    if log_window:
        log_text.config(state="normal")
        log_text.insert(END, message + "\n")
        log_text.see(END)
        log_text.config(state="disabled")


def find_world(start_dir):
    for root, dirs, _ in os.walk(start_dir):
        for dir_name in dirs:
            if fnmatch.fnmatch(dir_name, "*infinite-parkour*"):
                path = os.path.join(root, dir_name)
                log_message(f"Found world: {path}")
                return path

    log_message("Cannot find world")
    messagebox.showerror("Error", "Cannot find world. Check your path or ensure it exists.")
    return None


def save_config(custom_path):
    config_path = os.path.join(os.path.expandvars("%LOCALAPPDATA%"), "Infinite-Parkour", "updaterconfig.json")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump({"data": custom_path}, f, indent=4)
    log_message("Config saved")

def load_config():
    config_path = os.path.join(os.path.expandvars("%LOCALAPPDATA%"), "Infinite-Parkour", "updaterconfig.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            log_message("Config loaded")
            return json.load(f).get("data", "")
    return ""


def get_custom_path():
    custom_path = txt.get().strip()
    if custom_path:
        if os.path.isfile(os.path.join(custom_path, "server.properties")):
            return os.path.join(custom_path, "world")
        saves_path = os.path.join(custom_path, "saves")
    else:
        saves_path = os.path.join(os.path.expandvars("%APPDATA%"), ".minecraft", "saves")
        if not os.path.exists(saves_path):
            log_message("Default saves path not found. Please select your Minecraft folder.")
            messagebox.showerror("Error", "Default saves path not found. Please select your Minecraft folder.")
            return None
    return find_world(saves_path)


def select_file(folder=""):
    filetypes = [("Jump packs", "*.jumppack"), ("All files", "*.*")]
    file_path = filedialog.askopenfilename(initialdir=folder, filetypes=filetypes, title="Select file")
    return file_path or None


def select_directory():
    folder_path = filedialog.askdirectory(title="Select Minecraft Folder")
    if folder_path:
        txt.delete(0, END)
        txt.insert(0, folder_path)
        save_config(folder_path)