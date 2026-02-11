from tkinter import Toplevel, ttk, Text, Scrollbar
from components.util import copy_to_clipboard
from components.util import select_directory
from components.jumpacks import importpack, exportpack

def toggle_log_window():
    if log_window.winfo_ismapped():
        log_window.withdraw()
    else:
        log_window.deiconify

def initialize(root, update_cb, reset_cb, updatepack_cb):
    global log_window, log_text, _update, _reset_config, _updatepack
    _update = update_cb
    _reset_config = reset_cb
    _updatepack = updatepack_cb

    log_window = Toplevel(root)
    log_window.title("Terminal Log")
    log_window.geometry("600x250")
    log_window.withdraw()

    log_label = ttk.Label(log_window, text="Terminal Log:")
    log_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

    log_text = Text(log_window, wrap="word", width=70, height=12, state="disabled")
    log_text.grid(row=1, column=0, columnspan=4, padx=10, pady=5)

    scrollbar = Scrollbar(log_window, command=log_text.yview)
    scrollbar.grid(row=1, column=4, sticky="ns", pady=5)
    log_text.config(yscrollcommand=scrollbar.set)
    return log_window, log_text


def setup_buttons(main_frame):
    btn_browse = ttk.Button(main_frame, text="Browse", command=select_directory)
    btn_browse.grid(row=1, column=1, sticky="ew")

    action_frame = ttk.LabelFrame(main_frame, text="Actions", padding=10)
    action_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="ew")

    btn_run = ttk.Button(action_frame, text="Update Pack", command=_updatepack)
    btn_run.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    btn_reset = ttk.Button(action_frame, text="Reset Config", command=_reset_config)
    btn_reset.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    btn_import = ttk.Button(action_frame, text="Import jumpack", command=importpack)
    btn_import.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

    btn_export = ttk.Button(action_frame, text="Export jumpack", command=exportpack)
    btn_export.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    btn_update = ttk.Button(action_frame, text="Update EXE", command=_update)
    btn_update.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

    btn_help = ttk.Button(
        action_frame,
        text="Discord Help Link",
        command=lambda: copy_to_clipboard("https://discord.com/users/1327055692179177494"),
    )
    btn_help.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    btn_toggle_log = ttk.Button(main_frame, text="Show/Hide Log Window", command=toggle_log_window)
    btn_toggle_log.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")
