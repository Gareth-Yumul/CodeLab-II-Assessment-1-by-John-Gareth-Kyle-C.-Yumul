"""
John Gareth Kyle C. Yumul
G3 - Level 5 - Cybersecurity
Exercise 2: Alexa Tell Me a Joke
"""
import random  # Shuffle the jokes into a random order
import tkinter as tk  # GUI toolkit
from pathlib import Path  # Build the joke file's path from this script's location
from tkinter import messagebox  # Error message pop-up if the joke file can't be loaded

# This allows to connect the python file to the txt file
Jokes_File = Path(__file__).parent / "randomJokes.txt"

# Reads the jokes.txt file and returns a list of (setup, punchline) pairs, skipping bad lines
def load_jokes(path):
    jokes = []
    with open(path, encoding="utf-8-sig") as file:
        for line in file:
            line = line.strip()
            if line.startswith("-"):
                line = line[1:].strip()
            if "?" not in line:  # No questions mark jokes means nothing to split
                continue
            setup, _, punchline = line.partition("?")
            setup, punchline = setup.strip(), punchline.strip()
            if not setup or not punchline:
                continue
            jokes.append((setup + "?", punchline))
    if not jokes: # If file has no usable jokes 
        raise ValueError("No usable jokes found in the file.")
    return jokes

# Holds the joke list and the widgets and decides which joke to show next
class JokeApp:
    def __init__(self, root, jokes): #Builds the window widget and put it at a starting state 
        self.root = root # Main window
        self.jokes = jokes # The list of (setup, punchline) pairs
        self.order = []  # This shuffled the jokes which indicate the current round
        self.position = -1  # where we are in self.order; -1 = nothing shown yet

        # Label that shows the joke's setup
        self.setup_label = tk.Label(root, text="Press the button to hear a joke.", font=("Times New Roman", 16, "bold"), wraplength=440, justify="center")
        self.setup_label.pack(pady=(25, 10), padx=20)

        # Label for the punchline
        self.punchline_label = tk.Label(root, text="", font=("Times New Roman", 16, "italic"), wraplength=440, justify="center")
        self.punchline_label.pack(pady=10, padx=20)

        # Containers for the buttons that sit in 2x2 grid
        buttons = tk.Frame(root)
        buttons.pack(pady=15)

        # Starts the session, then disables the Alexa tell me a Joke" button allowing the "Next Joke" to take over
        self.tell_button = tk.Button(buttons, text="Alexa tell me a Joke", width=20, command=self.tell_joke)
        self.tell_button.grid(row=0, column=0, padx=6, pady=4)

        # Disabled until a joke is on screen so that there is nothing to reveal yet
        self.punchline_button = tk.Button(buttons, text="Show Punchline", width=20, state="disabled", command=self.show_punchline)
        self.punchline_button.grid(row=0, column=1, padx=6, pady=4)
        self.next_button = tk.Button(buttons, text="Next Joke", width=20, state="disabled", command=self.next_joke)
        self.next_button.grid(row=1, column=0, padx=6, pady=4)
        tk.Button(buttons, text="Quit", width=20, command=root.destroy).grid(row=1, column=1, padx=6, pady=4)
        
    # Moves to the next joke in shuffled order then resuffles when the first rounf is finish
    def _advance(self):
        self.position += 1
        if self.position >= len(self.order):
            last = self.order[-1] if self.order else None
            self.order = random.sample(range(len(self.jokes)), len(self.jokes))
            
            # This allows the joke not to appear twice in a row across two rounds
            if len(self.order) > 1 and self.order[0] == last:
                self.order[0], self.order[1] = self.order[1], self.order[0]
            self.position = 0

    # It dispalys the current joke's setup and hides any old punchline
    def _show_joke(self):
        setup, _ = self.jokes[self.order[self.position]]
        self.setup_label.config(text=setup)
        self.punchline_label.config(text="")
        self.punchline_button.config(state="normal")

    # This handles the "Alexa tell me a joke" button, it shows first the firts joke then it disables the button handing it over to the "Next Joke" button for the following jokes
    def tell_joke(self):
        self._advance()
        self._show_joke()
        self.tell_button.config(state="disabled")
        self.next_button.config(state="normal")

    # This handles the "Show Punchline" button, it reveals the current joke's punchline when joke is displayed
    def show_punchline(self):
        if self.position < 0:
            return
        _, punchline = self.jokes[self.order[self.position]]
        self.punchline_label.config(text=punchline)
        self.punchline_button.config(state="disabled")

    # This handles the "Next Joke" button, it allows to move to the next joke in the shuffled round
    def next_joke(self):
        self._advance()
        self._show_joke()
        
# Creates the window, loads the txt file, and starts the app (or shows an error if no jokes found)
def main():
    root = tk.Tk()
    root.title("Alexa tell me a Joke")
    root.geometry("520x320")
    root.resizable(False, False)

    # This loads the file and if file has no jokes an error will pop-up and quit instead of crashing down
    try:
        jokes = load_jokes(Jokes_File)
    except (OSError, ValueError) as error: # ValueError: no jokes that can be used, together with poor encoding while OSError: file missing or unreadable
        root.withdraw()  # THis avoid flashing a blank window behind the error dialog
        messagebox.showerror("Could not load jokes", f"{Jokes_File.name}: {error}")
        root.destroy()
        return
    
    # This builds the app on the window then starts the event loop and waits for clicks
    JokeApp(root, jokes)
    root.mainloop()

#Explain this part
if __name__ == "__main__":
    main()
