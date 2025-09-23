from tkinter import Tk, Label, messagebox, END, Text, Scrollbar, Toplevel
from tkinter import ttk
from tkinter.filedialog import askopenfilename, askdirectory
from os import getlogin, system, walk, remove, makedirs, chdir
from os.path import exists, join, dirname, basename
from shutil import rmtree
from zipfile import ZipFile
from sys import exit
from fnmatch import fnmatch
from json import dump, load
from urllib.request import urlopen, urlretrieve
from tarfile import open as opentar
from traceback import format_exc



def copy(url, shutup=False):
    root.clipboard_clear()
    root.clipboard_append(url)
    if not shutup:
        messagebox.showinfo("Copied", 'URL Copied to Clipboard')


def find_world(root_dir):
    for root, dirs, _ in walk(root_dir):
        for dir_name in dirs:
            if fnmatch(dir_name, '*Infinite-Parkour*'):
                return join(root, dir_name)
    print("Cannot find world")
    log_message("Cannot find world")
    messagebox.showerror('Error', "Cannot find world. Check your path or ensure it exists.")
    
    return None


def save_config(custom_path):
    f = open(f'C:/Users/{getlogin()}/Documents/parkourconfig.json', 'w', encoding='utf-8')
    dump({"data": custom_path}, f, ensure_ascii=False, indent=4)
    f.close()
    print("config saved")
    log_message("Config saved")


def load_config():
    if exists(f'C:/Users/{getlogin()}/Documents/parkourconfig.json'):
        file = open(f'C:/Users/{getlogin()}/Documents/parkourconfig.json', 'r')
        print("config loaded")
        log_message("Config loaded")
        ret = load(file).get('data', '')
        file.close()
        return ret
    return ''


def get_custom_path():
    custom_path = txt.get().strip()
    saves_path = custom_path + "/saves" if custom_path else f"C:/Users/{getlogin()}/AppData/Roaming/.minecraft/saves"
    world_path = find_world(saves_path)
    return world_path


def select_file(folder=''):
    file_path = askopenfilename(initialdir=folder)
    if file_path:
        return file_path
    else:
        return None


def select_directory():
    folder_path = askdirectory(title="Select Minecraft Folder")
    if folder_path:
        txt.delete(0, END)
        txt.insert(0, folder_path)  # Update the entry field with selected directory
        save_config(folder_path)  # Save the folder path to the config


def log_message(message):
    if log_window:
        log_text.config(state="normal")
        log_text.insert(END, message + "\n")
        log_text.see(END)  # Scroll to the end
        log_text.config(state="disabled")


def updatepack():
    log_message("Starting updater...")
    try:
        custom_path = txt.get().strip()
        saves_path = custom_path + "/saves" if custom_path else f"C:/Users/{getlogin()}/AppData/Roaming/.minecraft/saves"
        world_path = find_world(saves_path)
        if not world_path:
            return
        if custom_path:
            save_config(custom_path)

        datapack_path = join(world_path, 'datapacks', 'Infinite-Parkour-datapack-main')

        rmtree(dirname(datapack_path))
        makedirs(dirname(datapack_path))

        # --- changed section ---
        api_url = "https://api.github.com/repos/Big-Con-Gaming/Infinite-Parkour-datapack/releases/latest"
        with urlopen(api_url) as resp:
            release = load(resp)
        zip_url = release["zipball_url"]
        urlretrieve(zip_url, f'{dirname(datapack_path)}/temp.zip')
        # --- end changed section ---

        log_message(f"Downloaded zip file to {dirname(datapack_path)}/temp.zip")

        with ZipFile(f'{dirname(datapack_path)}/temp.zip', mode="r") as zipf:
            zipf.extractall(dirname(datapack_path))

        remove(f'{dirname(datapack_path)}/temp.zip')
        log_message(f"Extracted datapack to {datapack_path}")

        chdir(datapack_path)
        system(f'{datapack_path}\\build.bat')

        messagebox.showinfo("Done", 'Update complete!')
        log_message("Update complete!")

    except Exception as e:
        error_trace = format_exc()
        print(error_trace)
        copy(e, True)
        log_message("Error occurred:\n" + error_trace)
        messagebox.showerror('Error', f"{e}\nAn error occurred. Contact MrBooks36 for help. Error copied to clipboard")


def reset_config():
    if exists(f'C:/Users/{getlogin()}/Documents/parkourconfig.json'):
        remove(f'C:/Users/{getlogin()}/Documents/parkourconfig.json')
    txt.delete(0, END)
    log_message("Config reset.")


def update():
    system('start cmd /c updaterinstaller.exe headless')
    exit()


def importpack():
    try:
        pack = select_file()
        if pack is None or '.jumpack' not in pack:
            return

        chdir(get_custom_path() + '/data')
        file = opentar(pack)
        file.extractall(filter='fully_trusted')
        file.close()

        messagebox.showinfo('Done', 'Your jumpack has been imported. Add it with the book in your hotbar in the world')
        log_message(f"Imported pack: {pack}")

    except Exception as e:
        error_trace = format_exc()
        print(error_trace)
        messagebox.showerror('Error', f"An error occurred.\n{e}")
        copy(e, True)
        log_message("Error occurred while importing pack:\n" + error_trace)
    


def exportpack():
    try:
        pack = select_file(folder=get_custom_path() + '/data')
        if not pack or 'command_storage' not in pack:
            return

        chdir(dirname(pack))
        tar = opentar(f'C:/Users/{getlogin()}/Downloads/My.jumpack', 'w:gz')
        tar.add(basename(pack))
        tar.close()

        messagebox.showinfo('Done', 'Done! You can find your jumpack in your downloads folder.')
        log_message(f"Exported pack to: C:/Users/{getlogin()}/Downloads/My.jumpack")

    except Exception as e:
        error_trace = format_exc()
        print(error_trace)
        messagebox.showerror('Error', f"An error occurred.\n{e}")
        copy(error_trace, True)
        log_message("Error occurred while exporting pack:\n" + error_trace)


def toggle_log_window():
    global log_window
    if log_window.winfo_ismapped():
        log_window.withdraw()  # Hide the log window
    else:
        log_window.deiconify()  # Show the log window
        


# GUI Setup
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, _):
        if self.tip_window or not self.text:
            return
        x, y, _, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + cy + 25
        self.tip_window = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = Label(tw, text=self.text, justify='left',
                      background="#ffffe0", relief="solid", borderwidth=1,
                      font=("tahoma", "9", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, _):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()


root = Tk()
root.title("Infinite Parkour - Pack Manager")
root.geometry('400x260')
root.resizable(False, False)

main_frame = ttk.Frame(root, padding=10)
main_frame.grid(row=0, column=0, sticky="nsew")

# Entry Field & Path Selection
ttk.Label(main_frame, text="Minecraft Folder Path:").grid(row=0, column=0, columnspan=2, sticky="w")

txt = ttk.Entry(main_frame, width=50)
txt.grid(row=1, column=0, sticky="ew", padx=(0, 5))
txt.insert(0, load_config())

btn_browse = ttk.Button(main_frame, text="Browse", command=select_directory)
btn_browse.grid(row=1, column=1, sticky="ew")
Tooltip(btn_browse, "Select your .minecraft folder")

# Action Buttons
action_frame = ttk.LabelFrame(main_frame, text="Actions", padding=10)
action_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="ew")

btn_run = ttk.Button(action_frame, text="Update Pack", command=updatepack)
btn_run.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
Tooltip(btn_run, "Download and install the latest version")

btn_reset = ttk.Button(action_frame, text="Reset Config", command=reset_config)
btn_reset.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

btn_import = ttk.Button(action_frame, text="Import jumpack", command=importpack)
btn_import.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

btn_export = ttk.Button(action_frame, text="Export jumpack", command=exportpack)
btn_export.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

btn_update = ttk.Button(action_frame, text="Update EXE", command=update)
btn_update.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

btn_help = ttk.Button(action_frame, text="Discord Help Link", command=lambda: copy('https://discord.com/users/1327055692179177494'))
btn_help.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

# Log Viewer Button
btn_toggle_log = ttk.Button(main_frame, text="Show/Hide Log Window", command=toggle_log_window)
btn_toggle_log.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

# Log Window Setup
log_window = Toplevel(root)
log_window.title("Terminal Log")
log_window.geometry('600x250')
log_window.withdraw()

log_label = ttk.Label(log_window, text="Terminal Log:")
log_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

log_text = Text(log_window, wrap="word", width=70, height=12, state="disabled")
log_text.grid(row=1, column=0, columnspan=4, padx=10, pady=5)

scrollbar = Scrollbar(log_window, command=log_text.yview)
scrollbar.grid(row=1, column=4, sticky="ns", pady=5)
log_text.config(yscrollcommand=scrollbar.set)

root.mainloop()