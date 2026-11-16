"""
John Gareth Kyle C. Yumul
G3 - Level 5 - Cybersecurity
Exercise 1: Maths Quiz
"""

import random # Imports random Number
import re  # Imports regular Expression
import tkinter as tk # GUI toolkit
from tkinter import messagebox # Imports pop-up message such as "play again?"

Questions_Per_Game = 10 #The amount of questions you'll get in a game
Points_First_Try = 10 # The amount of points you will get in first attempt in each questions
Points_Second_Try = 5 # The amount of points you will get in second attempt in each questions
Max_Score = Questions_Per_Game * Points_First_Try # Total amount points got in the quiz
Feedback_Delay_Ms = 1200 # It shows how long the "Correct" or "Wrong" stays in milliseconds 

# This Dictonaries shows the level and the min and max number in each level
Difficulties = {
    "Easy": (1, 9),
    "Moderate": (10, 99),
    "Advanced": (1000, 9999),
}

# This list of tuple (minimum score, grade) shows the score depending the users result 
Grade_Boundaries = [(90, "A+"), (80, "A"), (70, "B"), (60, "C"), (50, "D"), (0, "F")]

# This allows user input to be valis such as "1_000" or "-54" but inputs such as "abc" or "4x" invalid
Integer_Pattern = re.compile(r"-?\d+")

# This class define the blueprint that bundles data (score, question number) with the functions that use it
class MathsQuiz:

    # Explain this part
    def __init__(self, root):
        self.root = root
        self.frame = None
        self.entry = None
        self.status_label = None
        self.feedback_label = None

        self.difficulty = "Easy"
        self.score = 0
        self.question_number = 0
        self.attempt = 1
        self.correct_answer = 0
        self.locked = False  # True while feedback shows; ignores extra Enter/clicks

    # ---------- screen switching ----------
    # Explain this part
    def _new_frame(self):
        """Replace the current screen. One Tk root, one swapped frame."""
        if self.frame is not None:
            self.frame.destroy()
        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True, fill="both")
        return self.frame

    # ---------- required functions ----------
    # Explain this part
    def displayMenu(self):
        """Show difficulty buttons (Easy / Moderate / Advanced)."""
        frame = self._new_frame()
        tk.Label(frame, text="DIFFICULTY LEVEL", font=("Arial", 18, "bold")).pack(pady=20)
        for number, name in enumerate(Difficulties, start=1):
            tk.Button(
                frame, text=f"{number}. {name}", width=20, font=("Arial", 12),
                command=lambda level=name: self._start_game(level),
            ).pack(pady=6)
