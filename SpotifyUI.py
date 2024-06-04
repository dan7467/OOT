import tkinter as tk
from MainContent import MainContent
from Sidebar import Sidebar


class SpotifyUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Spotify-like UI")
        self.geometry("1200x800")

        # Configure the grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Initialize Sidebar
        self.sidebar = Sidebar(self)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        # Initialize Main Content Area
        self.main_content = MainContent(self)
        self.main_content.grid(row=0, column=1, sticky="nsew")