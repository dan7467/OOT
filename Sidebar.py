import tkinter as tk
class Sidebar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#B31312", width=200, height=800)
        self.create_sidebar_buttons()

    def create_sidebar_buttons(self):

         btn = tk.Button(self, text="Home", bg="#1DB954", fg="#B31312", bd=0, relief="flat",
                        font=("Helvetica", 12), command=self.on_sidebar_button_click)
         btn.pack(fill="x", pady=5, padx=10),

         btn_AddSong = tk.Button(self, text="Add Song", bg="#1DB954", fg="#B31312", bd=0, relief="flat",
                    font=("Helvetica", 12), command=self.on_add_Song)
         btn_AddSong.pack(fill="x", pady=5, padx=10)

    def on_sidebar_button_click(self):
        self.master.main_content.refresh_content()

    def on_add_Song(self):
        self.master.main_content.addSong()
