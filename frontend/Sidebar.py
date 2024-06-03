import tkinter as tk
class Sidebar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#1DB954", width=200, height=800)
        self.create_sidebar_buttons()

    def create_sidebar_buttons(self):
        buttons = ["Home", "Search", "Your Library"]
        for button in buttons:
            btn = tk.Button(self, text=button, bg="#1DB954", fg="white", bd=0, relief="flat",
                            font=("Helvetica", 12), command=self.on_sidebar_button_click)
            btn.pack(fill="x", pady=5, padx=10)

    def on_sidebar_button_click(self):
        self.master.main_content.refresh_content()