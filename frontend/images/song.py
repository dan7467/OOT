# import tkinter as tk
# from tkinter import ttk
# from tkinter.messagebox import showinfo
# from PIL import Image, ImageTk  # You need to install Pillow for image handling: `pip install Pillow`
# import os
#
# class SpotifyUI(tk.Tk):
#     def __init__(self):
#         super().__init__()
#
#         self.title("Spotify-like UI")
#         self.geometry("1200x800")
#
#         # Configure the grid layout
#         self.grid_rowconfigure(0, weight=1)
#         self.grid_columnconfigure(1, weight=1)
#
#         # Initialize Sidebar
#         self.sidebar = Sidebar(self)
#         self.sidebar.grid(row=0, column=0, sticky="ns")
#
#         # Initialize Main Content Area
#         self.main_content = MainContent(self)
#         self.main_content.grid(row=0, column=1, sticky="nsew")
#
# class Sidebar(tk.Frame):
#     def __init__(self, parent):
#         super().__init__(parent, bg="#1DB954", width=200, height=800)
#         self.create_sidebar_buttons()
#
#     def create_sidebar_buttons(self):
#         buttons = ["Home", "Search", "Your Library"]
#         for button in buttons:
#             btn = tk.Button(self, text=button, bg="#1DB954", fg="white", bd=0, relief="flat",
#                             font=("Helvetica", 12), command=self.on_sidebar_button_click)
#             btn.pack(fill="x", pady=5, padx=10)
#
#     def on_sidebar_button_click(self):
#         self.master.main_content.refresh_content()
#
# class MainContent(tk.Frame):
#     def __init__(self, parent):
#         super().__init__(parent, bg="#121212")
#         self.create_main_content()
#
#     def create_main_content(self):
#         self.songs = [
#             {"img": "./images/example.png", "title": "Song 1", "artist": "Artist 1"},
#             {"img": "./images/example.png", "title": "Song 2", "artist": "Artist 2"},
#             {"img": "./images/example.png", "title": "Song 3", "artist": "Artist 3"},
#             {"img": "./images/example.png", "title": "Song 4", "artist": "Artist 4"},
#             {"img": "./images/example.png", "title": "Song 5", "artist": "Artist 5"},
#             {"img": "./images/example.png", "title": "Song 6", "artist": "Artist 6"},
#         ]
#         self.refresh_content()
#
#     def refresh_content(self):
#         for widget in self.winfo_children():
#             widget.destroy()
#         columns_per_row = 3  # Number of columns per row
#         for idx, song in enumerate(self.songs):
#             row = idx // columns_per_row
#             column = idx % columns_per_row
#             song_component = SongComponent(self, song)
#             song_component.grid(row=row, column=column, pady=20, padx=20, sticky="n")
#
#     def display_play_page(self, song):
#         for widget in self.winfo_children():
#             widget.destroy()
#
#         play_frame = tk.Frame(self, bg="#121212")
#         play_frame.pack(expand=True, fill="both")
#
#         try:
#             img = Image.open(song["img"])
#             img = img.resize((200, 200), Image.LANCZOS)
#             img = ImageTk.PhotoImage(img)
#         except FileNotFoundError:
#             showinfo("Error", f"Image file '{song['img']}' not found.")
#             return
#         except Exception as e:
#             showinfo("Error", f"Unable to open image: {e}")
#             return
#
#         img_label = tk.Label(play_frame, image=img, bg="#121212")
#         img_label.image = img  # Keep a reference to avoid garbage collection
#         img_label.pack(pady=20)
#
#         song_title = tk.Label(play_frame, text=song["title"], fg="white", bg="#121212", font=("Helvetica", 24))
#         song_title.pack(pady=10)
#
#         song_artist = tk.Label(play_frame, text=song["artist"], fg="gray", bg="#121212", font=("Helvetica", 18))
#         song_artist.pack(pady=5)
#
#         play_button = tk.Button(play_frame, text="Play", command=lambda: showinfo("Playing", f"Playing {song['title']}"), bg="#1DB954", fg="white", font=("Helvetica", 14))
#         play_button.pack(pady=20)
#
# class SongComponent(tk.Frame):
#     def __init__(self, parent, song):
#         super().__init__(parent, bg="#121212", bd=1, relief="flat", padx=10, pady=10)
#         self.song = song
#         self.create_song_template()
#
#     def create_song_template(self):
#         try:
#             img = Image.open(self.song["img"])
#             img = img.resize((128, 128), Image.LANCZOS)  # Larger image size
#             img = ImageTk.PhotoImage(img)
#         except FileNotFoundError:
#             showinfo("Error", f"Image file '{self.song['img']}' not found.")
#             return
#         except Exception as e:
#             showinfo("Error", f"Unable to open image: {e}")
#             return
#
#         img_label = tk.Label(self, image=img, bg="#121212")
#         img_label.image = img  # Keep a reference to avoid garbage collection
#         img_label.pack(side="top", pady=10)  # Increased padding
#
#         text_frame = tk.Frame(self, bg="#121212")
#         text_frame.pack(side="top", pady=10)  # Increased padding
#
#         song_title = tk.Label(text_frame, text=self.song["title"], fg="white", bg="#121212", font=("Helvetica", 16))
#         song_title.pack(anchor="center")
#
#         song_artist = tk.Label(text_frame, text=self.song["artist"], fg="gray", bg="#121212", font=("Helvetica", 14))
#         song_artist.pack(anchor="center")
#
#         self.bind("<Button-1>", self.on_click)
#         img_label.bind("<Button-1>", self.on_click)
#         text_frame.bind("<Button-1>", self.on_click)
#         song_title.bind("<Button-1>", self.on_click)
#         song_artist.bind("<Button-1>", self.on_click)
#
#     def on_click(self, event):
#         self.master.display_play_page(self.song)
#
# if __name__ == "__main__":
#     app = SpotifyUI()
#     app.mainloop()
