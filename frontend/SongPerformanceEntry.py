import tkinter as tk
from tkinter import messagebox


class SongPerformanceEntry(tk.Frame):
    def __init__(self, parent, number, grade, delete_callback, index, view_callback):
        print("init")
        super().__init__(parent)
        self.number = number
        # self.date = date
        self.grade = grade
        self.delete_callback = delete_callback
        self.index = index
        self.viewGraph_callback = view_callback
        self.create_widgets()

    def create_widgets(self):
        print("create_widgt")
        # print("number"+self.number)
        # print("grade: "+ self.grade)
        self.number_label = tk.Label(self, text=self.number)
        self.number_label.grid(row=0, column=0, padx=10, pady=5)

        # self.date_label = tk.Label(self, text=self.date)
        # self.date_label.grid(row=0, column=1, padx=10, pady=5)

        self.grade_label = tk.Label(self, text=self.grade)
        self.grade_label.grid(row=0, column=2, padx=10, pady=5)

        self.delete_button = tk.Button(self, text='Delete', command=self.on_delete)
        self.delete_button.grid(row=0, column=3, padx=10, pady=5)

        self.viewGraph_button = tk.Button(self, text='View Graph', command=self.on_viewGraph)
        self.viewGraph_button.grid(row=0, column=4, padx=10, pady=5)

    def on_delete(self):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this performance?"):
            self.delete_callback(self.index)


    def on_viewGraph(self):
        self.viewGraph_callback(self.index)
