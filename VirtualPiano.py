import time
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
        self.previous_rectangle = None  # Initialize previous_rectangle attribute
        self.current_notes = set()  # To store current notes being displayed

    def create_piano(self):
        piano_width = self.winfo_reqwidth()
        piano_height = self.winfo_reqheight()
        key_width = piano_width / len(self.notes)
        key_height = piano_height

        for i, note in enumerate(self.notes):
            x1 = i * key_width
            x2 = (i + 1) * key_width

            if '#' in note:  # Black keys
                self.create_rectangle(x1, piano_height / 2, x2, piano_height, fill='black', outline='black')
                self.create_text(x1 + key_width / 2, piano_height * 5 / 6, text=note, fill='white', font=('Arial', 8))
            else:  # White keys
                self.create_rectangle(x1, piano_height / 2, x2, piano_height, fill='white', outline='black')
                self.create_text(x1 + key_width / 2, piano_height * 5 / 6, text=note, font=('Arial', 8))

    def update_piano(self, note, errorOccured):
        if errorOccured:
            return
        self.highlight_key(note)

    def highlight_key(self, note):
        self.delete(self.current_note)
        key_index = self.notes.index(note)
        piano_width = self.winfo_reqwidth()
        key_width = piano_width / len(self.notes)
        x1 = key_index * key_width
        x2 = (key_index + 1) * key_width
        y = self.winfo_reqheight() / 2  # Middle of the canvas
        self.current_note = self.create_line(x1 + key_width / 2, self.winfo_reqheight() / 2, x1 + key_width / 2,
                                             self.winfo_reqheight(), fill='red', width=key_width / 4)

    # OLD VERSIONS
    # ALL THE KEYS ARE MOVING DOWN BUT THEY ARE ONE BY ONE! NEED TO BE MORE THAN ONE IN SCREEN
    # def display_notes_sequence(self, notes_sequence):
    #     piano_width = self.winfo_reqwidth()
    #     key_width = piano_width / len(self.notes)
    #     piano_height = self.winfo_reqheight() / 2
    #
    #     for note, duration in notes_sequence:
    #         key_index = self.notes.index(note)
    #         x1 = key_index * key_width
    #         x2 = (key_index + 1) * key_width
    #
    #         # Calculate the height of the blue rectangle based on duration
    #         note_height = duration * piano_height / 2
    #
    #         # Create a blue rectangle representing the note starting at the top of the screen
    #         rectangle = self.create_rectangle(x1, 0, x2, note_height, fill='blue', outline='blue')
    #
    #         # Animate the rectangle moving downwards until it reaches the corresponding key
    #         for i in range(int(piano_height)):
    #             self.move(rectangle, 0, 1)
    #             self.master.update()
    #             time.sleep(0.01)
    #
    #         # Delete the rectangle after reaching the key
    #         self.delete(rectangle)

    # ALL NOTES ARE SHOWN AT THE START OF THE PROGRAM, NEED TO DO IT ONE BY ONE
    # def display_notes_sequence(self, notes_sequence):
    #     piano_width = self.winfo_reqwidth()
    #     key_width = piano_width / len(self.notes)
    #     piano_height = self.winfo_reqheight() / 2
    #
    #     # Create a list to hold all blue rectangles
    #     rectangles = []
    #
    #     # Track the accumulated height of the previous rectangles
    #     total_height = 0
    #
    #     for note, duration in notes_sequence:
    #         key_index = self.notes.index(note)
    #         x1 = key_index * key_width
    #         x2 = (key_index + 1) * key_width
    #
    #         # Calculate the height of the blue rectangle based on duration
    #         note_height = duration * piano_height / 2
    #
    #         # Create a blue rectangle representing the note starting at the top of the screen
    #         rectangle = self.create_rectangle(x1, total_height, x2, total_height + note_height, fill='blue',
    #                                           outline='blue')
    #         rectangles.append(rectangle)
    #
    #         # Update the total height for the next rectangle
    #         total_height += note_height
    #
    #     # Animate all rectangles moving downwards until they reach the corresponding keys
    #     for i in range(int(piano_height)):
    #         for rectangle in rectangles:
    #             self.move(rectangle, 0, 1)
    #         self.master.update()
    #         time.sleep(0.01)
    #
    #     # Delete the rectangles after reaching the keys
    #     for rectangle in rectangles:
    #         self.delete(rectangle)

    # # NOTE coming down with good length effect!!
    # def display_note(self, note, duration):
    #     piano_width = self.winfo_reqwidth()
    #     key_width = piano_width / len(self.notes)
    #     piano_height = self.winfo_reqheight() / 2
    #
    #     key_index = self.notes.index(note)
    #     x1 = key_index * key_width
    #     x2 = (key_index + 1) * key_width
    #
    #     # Calculate the height of the blue rectangle based on duration
    #     total_duration = max(duration, 0.1)  # Minimum duration to prevent division by zero
    #     note_height = total_duration * piano_height / 2
    #
    #     # Create a blue rectangle representing the note starting at the top of the screen
    #     rectangle = self.create_rectangle(x1, -note_height, x2, 0, fill='blue', outline='blue')
    #
    #     # Animate the rectangle moving downwards
    #     while self.coords(rectangle)[1] < piano_height:
    #         self.move(rectangle, 0, 1)
    #         self.master.update()
    #         time.sleep(0.01)
    #
    #     # Delete the rectangle when its top aligns with the top of the piano keys
    #     self.delete(rectangle)

    # WORKING ALMOST PERFECT!! THEY ARE APPEARING ONE AFTER ANOTHER BUT WITH A SLIGHT OVERLAP

    def display_notes_sequence3(self, notes_sequence):
        # Calculate dimensions
        piano_width = self.winfo_reqwidth()
        key_width = piano_width / len(self.notes)
        piano_height = self.winfo_reqheight() / 2

        # Schedule the display of each note
        delay = 0
        for note, duration in notes_sequence:
            self.after(delay, self.display_note1, note, duration, piano_width, key_width, piano_height)
            delay += int(duration * 3000)  # Convert duration to milliseconds

    def display_note1(self, note, duration, piano_width, key_width, piano_height):
        key_index = self.notes.index(note) if note else 0  # Set key_index to 0 if note is None
        x1 = key_index * key_width
        x2 = (key_index + 1) * key_width

        total_duration = max(duration, 0.01)  # Minimum duration to prevent division by zero
        note_height = total_duration * piano_height / 2

        fill_color = 'white' if note is None else 'blue'  # Use white color if note is None
        outline_color = 'white' if note is None else 'blue'  # Use white color if note is None
        rectangle = self.create_rectangle(x1, -note_height, x2, 0, fill=fill_color, outline=outline_color)

        self.move_rect(rectangle, piano_height + note_height)

    def move_rect(self, rectangle, distance):
        # Schedule the movement of the rectangle
        self.move(rectangle, 0, 1)
        if self.coords(rectangle)[3] < distance:
            self.after(10, lambda: self.move_rect(rectangle, distance))
        else:
            self.delete(rectangle)

    # receives notes of seconds to notes and returns notes and duration (in seconds)
    def transormDictToTuples(self, notesDict):
        result = list()

        prevNoteTime = 0
        for currNoteTime, note in notesDict.items():
            if note == '0':
                note = None
            duration = (currNoteTime - prevNoteTime) / 3
            result.append((note, duration))
            prevNoteTime = currNoteTime

        return result


def testPiano(root):
    root.title("Virtual Piano")

    piano = VirtualPiano(root, width=1600, height=800)  # Adjust width and height here
    piano.pack(fill=tk.BOTH, expand=True)

    return piano


# def displayNotes(root, piano):
#     # Example of real-time update
#     notes_sequence = ['C2', 'D2', 'E2', 'F2', 'G2', 'A2', 'B#2', 'B2', 'C3']
#     for note in notes_sequence:
#         piano.update_piano(note)
#         root.update()
#         root.after(1000)  # Simulating real-time with a delay of 1 second


if __name__ == "__main__":
    root = tk.Tk()
    piano = testPiano(root)
    # displayNotes(root, piano)

    # notes_sequence = [('C4', 0.1), ('D4', 0.2), ('E4', 0.8), ('D4', 0.05)
    # , ('C4', 0.1), ('D4', 0.2), ('E4', 0.8), ('D4', 0.05)]
    # piano.display_notes_sequence(notes_sequence)

    # piano.display_note('C4', 1)
    # Example of notes sequence with two notes

    # then it will be shown for 6 seconds (so if I want something to be shown to 1.2 seconds I need to write below 0.4
    notes_sequence = [('C3', 2), (None, 1), ('D3', 0.3), ('D#3', 0.1), ('E3', 0.8),
                      ('F3', 3), ('F#3', 0.05), (None, 0.3), ('G#3', 0.1), ('A3', 0.8)]
    piano.display_notes_sequence3(notes_sequence)

    root.mainloop()
