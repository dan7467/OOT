# song_item.py
import tkinter as tk
from tkinter import ttk, PhotoImage


def songItem(root, imgLink: str):
    # Create a frame to contain the song item
    frame = ttk.Frame(root)  # Attach the frame to the root window
    frame.pack(padx=10, pady=10)

    imgFrame =ttk.Frame(root,width=10,height=10)
    imgFrame.pack()
    # Load the image
    img = PhotoImage(file=imgLink)

    # Keep a reference to prevent garbage collection
    imgFrame.img = img  # Store the image in the frame's namespace

    # Create a label to display the image
    imglabel = tk.Label(imgFrame, image=img)
    imglabel.pack()

    # Create labels for song name and singer
    songName = ttk.Label(frame, text="ndo",width=100)
    songName.pack()

    singer = ttk.Label(frame, text="Liam Payne")
    singer.pack()
