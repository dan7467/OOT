import tkinter as tk


class VirtualPiano(tk.Canvas):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.notes = ['C2', 'C#2', 'D2', 'D#2', 'E2', 'F2', 'F#2', 'G2', 'G#2', 'A2', 'B#2', 'B2',
                      'C3', 'C#3', 'D3', 'D#3', 'E3', 'F3', 'F#3', 'G3', 'G#3', 'A3', 'B#3', 'B3',
                      'C4', 'C#4', 'D4', 'D#4', 'E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'B#4', 'B4',
                      'C5', 'C#5', 'D5', 'D#5', 'E5', 'F5', 'F#5', 'G5', 'G#5', 'A5', 'B#5', 'B5',
                      'C6', 'C#6', 'D6', 'D#6', 'E6', 'F6', 'F#6', 'G6', 'G#6', 'A6', 'B#6', 'B6',
                      'C7']
        self.current_note = None
        self.create_piano()

    def create_piano(self):
        key_width = self.winfo_reqwidth() / len(self.notes)
        key_height = self.winfo_reqheight()

        for i, note in enumerate(self.notes):
            x1 = i * key_width
            x2 = (i + 1) * key_width

            if '#' in note:
                self.create_rectangle(x1, 0, x2, key_height / 1.5, fill='black', outline='black')
                self.create_text(x1 + key_width / 2, key_height / 3, text=note, fill='white', font=('Arial', 8))
            else:
                self.create_rectangle(x1, 0, x2, key_height, fill='white', outline='black')
                self.create_text(x1 + key_width / 2, key_height / 2, text=note, font=('Arial', 8))

    def update_piano(self, note):
        self.highlight_key(note)

    def highlight_key(self, note):
        self.delete(self.current_note)
        key_index = self.notes.index(note)
        key_width = self.winfo_reqwidth() / len(self.notes)
        x1 = key_index * key_width
        x2 = (key_index + 1) * key_width
        y = self.winfo_reqheight() / 2  # Middle of the canvas
        self.current_note = self.create_line(x1 + key_width / 2, 0, x1 + key_width / 2,
                                             self.winfo_reqheight(), fill='red', width=key_width / 4)


def testPiano(root):
    root.title("Virtual Piano")

    piano = VirtualPiano(root, width=1600, height=200)  # Adjust width here
    piano.pack(fill=tk.BOTH, expand=True)

    return piano


def displayNotes(root, piano):
    # Example of real-time update
    notes_sequence = ['C2', 'D2', 'E2', 'F2', 'G2', 'A2', 'Bb2', 'B2', 'C3']
    for note in notes_sequence:
        piano.update_piano(note)
        root.update()
        root.after(1000)  # Simulating real-time with a delay of 1 second


if __name__ == "__main__":
    root = tk.Tk()
    piano = testPiano(root)
    displayNotes(root, piano)
    root.mainloop()
