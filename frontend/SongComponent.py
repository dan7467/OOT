
import tkinter as tk
from tkinter.messagebox import showinfo
from PIL import Image, ImageTk
class SongComponent(tk.Frame):
    def __init__(self, parent, song):
        super().__init__(parent, bg="#EEEEEE", bd=1, relief="flat", padx=10, pady=10)
        self.song = song
        self.create_song_template()

    def create_song_template(self):
        try:
            img = Image.open(self.song["img"])
            img = img.resize((128, 128), Image.LANCZOS)  # Larger image size
            img = ImageTk.PhotoImage(img)
        except FileNotFoundError:
            showinfo("Error", f"Image file '{self.song['img']}' not found.")
            return
        except Exception as e:
            showinfo("Error", f"Unable to open image: {e}")
            return

        img_label = tk.Label(self, image=img, bg="#EEEEEE")
        img_label.image = img  # Keep a reference to avoid garbage collection
        img_label.pack(side="top", pady=10)  # Increased padding

        text_frame = tk.Frame(self, bg="#EEEEEE")
        text_frame.pack(side="top", pady=10)  # Increased padding

        song_title = tk.Label(text_frame, text=self.song["title"], fg="#B31312", bg="#EEEEEE", font=("Helvetica", 16))
        song_title.pack(anchor="center")

        song_artist = tk.Label(text_frame, text=self.song["artist"], fg="#B31312", bg="#EEEEEE", font=("Helvetica", 14))
        song_artist.pack(anchor="center")

        self.bind("<Button-1>", self.on_click)
        img_label.bind("<Button-1>", self.on_click)
        text_frame.bind("<Button-1>", self.on_click)
        song_title.bind("<Button-1>", self.on_click)
        song_artist.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        self.master.display_play_page(self.song)