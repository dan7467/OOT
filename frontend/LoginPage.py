import tkinter as tk

from filesAccess import DBAccess
from frontend.MainContent import MainContent
from frontend.Sidebar import Sidebar


class LoginPage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.userName = None
        self.title("Login")
        self.geometry("1600x900")

        self.label = tk.Label(self, text="Enter your name:",fg="#B31312")
        self.label.pack()

        self.name_entry = tk.Entry(self,fg="#B31312")
        self.name_entry.pack()

        self.login_button = tk.Button(self, text="Login", command=self.save_name,fg="#B31312")
        self.login_button.pack()

    def save_name(self):
        name = self.name_entry.get()
        if name:
            # Save the name to a file or database
            self.userName = name
            #self.dbAccess = DBAccess(name)
            # Close the login window and open the Spotify UI
            for widget in self.winfo_children():
                widget.destroy()
            self.startApp()


    def startApp(self):
        self.title("OutOfTune")
        # Configure the grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Initialize Sidebar
        self.sidebar = Sidebar(self)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        # Initialize Main Content Area
        self.main_content = MainContent(self, self.userName)
        self.main_content.grid(row=0, column=1, sticky="nsew")