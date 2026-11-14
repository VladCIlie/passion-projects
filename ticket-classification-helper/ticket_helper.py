"""
Ticket Classification Helper

A small always-on-top Tkinter utility for agents who must classify large
volumes of tickets in an ITSM tool (e.g. ServiceNow). Pick values from three
dropdowns, then press the global hotkey (Cmd/Ctrl + Shift + 1, because it was designed while using a MAC, sorry) while focused
on the ticket form: the tool formats the classification text, puts it on the
clipboard, pastes it into the focused field and navigates the form (Tab x3,
Enter) so a full classification takes one keystroke.

Edit the three *_OPTIONS lists below to match your ticketing taxonomy.

Dependencies: pyautogui, pyperclip, pynput
"""

import sys
import time
import tkinter as tk
from tkinter import ttk

import pyautogui
import pyperclip
from pynput import keyboard


# Taxonomy - edit these to match your organization's ticket schema.

QUALITY_OPTIONS = [
]

PROCESS_OPTIONS = [
]

PRODUCT_OPTIONS = [
]

#This is the part where we build the gui base elements

class TicketClassificationHelper:
    def __init__(self, root):
        self.root = root

        self.root.title("Ticket Classification Helper")
        self.root.geometry("700x350") #Adjust this depending on your need
        self.root.resizable(False, False)

        self.action_running = False

        self.quality_var = tk.StringVar(value=QUALITY_OPTIONS[0])
        self.process_var = tk.StringVar(value=PROCESS_OPTIONS[0])
        self.product_var = tk.StringVar(value=PRODUCT_OPTIONS[0])

        self.status_var = tk.StringVar(
            value="Click inside the notes field and press Cmd+Shift+1"
        )

        self.build_ui()
        self.start_hotkey()

    # UI

    def build_ui(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Ticket Classification Helper",
            font=("Segoe UI", 18, "bold"),
        ).pack(pady=(0, 20))

        self.create_dropdown(frame, "Quality", self.quality_var, QUALITY_OPTIONS)
        self.create_dropdown(frame, "Process", self.process_var, PROCESS_OPTIONS)
        self.create_dropdown(frame, "Product", self.product_var, PRODUCT_OPTIONS)

        ttk.Label(
            frame,
            text="Global shortcut: Cmd + Shift + 1",
            font=("Segoe UI", 10, "bold"),
        ).pack(pady=(20, 10))

        ttk.Label(
            frame,
            textvariable=self.status_var,
            foreground="blue",
            wraplength=650,
            justify="center",
        ).pack()

        ttk.Button(frame, text="Close", command=self.close_app).pack(pady=20)

    def create_dropdown(self, parent, label_text, variable, values):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=6)

        ttk.Label(row, text=f"{label_text}:", width=12).pack(side="left")

        combo = ttk.Combobox(
            row,
            textvariable=variable,
            values=values,
            state="readonly",
            width=45,
        )
        combo.pack(side="left", padx=10)

    # Hotkey

    def start_hotkey(self):
        self.hotkey_listener = keyboard.GlobalHotKeys(
            {"<cmd>+<shift>+1": self.hotkey_pressed}
        )
        self.hotkey_listener.start()

    def hotkey_pressed(self):
        self.root.after(0, self.perform_action)

    # Automation

    def perform_action(self):
        if self.action_running:
            return

        self.action_running = True

        try:
            text = (
                f"Quality: {self.quality_var.get()}\n"
                f"Process: {self.process_var.get()}\n"
                f"Product: {self.product_var.get()}"
            )

            pyperclip.copy(text)

            # Release possibly stuck modifier keys first - otherwise a
            # leftover Cmd/Ctrl press produces a stray "v" in the form.
            # I actually did not find a way to fi this completely
            self.release_modifiers()

            # Give the hotkey handler time to fully finish before typing.
            time.sleep(0.40)

            self.paste_clipboard()
            time.sleep(0.30)

            for _ in range(3):
                pyautogui.press("tab")
                time.sleep(0.15)

            time.sleep(0.10)
            pyautogui.press("enter")

            self.status_var.set("Classification posted successfully.")

        except Exception as error:
            self.status_var.set(f"Error: {error}")

        finally:
            self.action_running = False


    def release_modifiers(self):
        for key in ("command", "shift", "ctrl", "alt"):
            try:
                pyautogui.keyUp(key)
            except Exception:
                pass

    def paste_clipboard(self):
        modifier = "command" if sys.platform == "darwin" else "ctrl"

        modifier_down = False
        try:
            pyautogui.keyDown(modifier)
            modifier_down = True

            time.sleep(0.08)
            pyautogui.press("v")
            time.sleep(0.08)

        finally:
            if modifier_down:
                pyautogui.keyUp(modifier)


    def close_app(self):
        try:
            self.hotkey_listener.stop()
        except Exception:
            pass

        self.root.destroy()


if __name__ == "__main__":
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.05

    root = tk.Tk()
    app = TicketClassificationHelper(root)
    root.mainloop()
