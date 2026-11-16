"""
John Gareth Kyle C. Yumul
G3 - Level 5 - Cybersecurity
Exercise 1: Maths Quiz
"""

import random # Imports random Number
import re  # Imports regular Expression
import tkinter as tk # GUI toolkit
from tkinter import messagebox # Imports pop-up message such as "play again?"

Questions_Per_Game = 10
Points_First_Try = 10
Points_Second_Try = 5
Max_Score = Questions_Per_Game * Points_First_Try
Feedback_Delay_Ms = 1200

# It includes all level. Easy starts at 1 not 0: "single digit" is ambiguous and 0 makes trivial questions. Advanced is 1000-9999 so every number genuinely has 4 digits
Difficulties = {
    "Easy": (1, 9),
    "Moderate": (10, 99),
    "Advanced": (1000, 9999),
}

# (minimum score, grade) highest first. "Over 90" in the brief is read as >= 90, because scores come in multiples of 5 and 90 is reachable
Grade_Boundaries = [(90, "A+"), (80, "A"), (70, "B"), (60, "C"), (50, "D"), (0, "F")]

# Optional leading minus, then digits only. Stricter than int() which also accepts things like "1_000" and "+5"
Integer_Pattern = re.compile(r"-?\d+")

class MathsQuiz:
    # Holds all quiz state because Tkinter callbacks can't share locals

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
        self.locked = False # True while feedback shows it ignores extra Enter/clicks

    # Screen Switch

    def _new_frame(self):
        # Replace the current screen. One Tk root and one swapped frame
        if self.frame is not None:
            self.frame.destroy()
        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True, fill="both")
        return self.frame

    # Requires Function

    def displayMenu(self):
        # Show difficulty buttons (Easy, Moderate, and Advanced)
        frame = self._new_frame()
        tk.Label(frame, text="Difficulty Level", font=("Times New Roman", 18, "bold")).pack(pady=20)
        for number, name in enumerate(Difficulties, start=1):
            tk.Button(frame, text=f"{number}. {name}", width=20, font=("Times New Roman", 12), command=lambda level=name: self._start_game(level),).pack(pady=6)

    @staticmethod
    def randomInt(difficulty):
        # Return one random int whose digit count matches the difficulty
        low, high = Difficulties[difficulty]
        return random.randint(low, high)

    @staticmethod
    def decideOperation():
        # Randomly return '+' or '-'
        return random.choice(["+", "-"])

    def displayProblem(self):
        # Generate and show a question making it clear and focus the Entry 
        self.question_number += 1
        self.attempt = 1
        self.locked = False

        a = self.randomInt(self.difficulty)
        b = self.randomInt(self.difficulty)
        operation = self.decideOperation()
        self.correct_answer = a + b if operation == "+" else a - b

        frame = self._new_frame()
        self.status_label = tk.Label(frame, font=("Times New Roman", 11))
        self.status_label.pack(pady=10)
        self._update_status()

        tk.Label(frame, text=f"{a} {operation} {b} =", font=("Times New Roman", 24, "bold")).pack(pady=15)

        self.entry = tk.Entry(frame, font=("Times New Roman", 16), width=10, justify="center")
        self.entry.pack()
        self.entry.focus_set()
        self.entry.bind("<Return>", self.handle_submit)

        self.feedback_label = tk.Label(frame, text="", font=("Times New Roman", 12), wraplength=380)
        self.feedback_label.pack(pady=12)

        tk.Button(frame, text="Submit", width=12, font=("Times New Roman", 12), command=self.handle_submit).pack()

    def isCorrect(self, user_answer, correct_answer):
        # Check the answer then show an appropriate message that returns True/False. Scoring and moving on are done by handle_submit so this stays a simple check with feedback.
        if user_answer == correct_answer:
            self._set_feedback("Correct!", "green")
            return True
        if self.attempt == 1:
            self._set_feedback("Wrong - you have one more try.", "red")
        else:
            self._set_feedback(f"Wrong. The answer was {correct_answer}.", "red")
        return False

    def displayResults(self):
        # Show the score out of 100 a grade and ask to play again
        frame = self._new_frame()
        tk.Label(frame, text="Quiz Complete!", font=("Times New Roman", 20, "bold")).pack(pady=20)
        tk.Label(frame, text=f"Score: {self.score} / {Max_Score}", font=("Times New Roman", 16)).pack()
        tk.Label(frame, text=f"Rank: {self.grade_for(self.score)}", font=("Times New Roman", 16)).pack(pady=8)

        self.root.update_idletasks()  # Draw the results before the dialog opens
        if messagebox.askyesno("Play again?", "Would you like to play again?"):
            self.displayMenu()
        else:
            self.root.destroy()

    # Helpers
    def _start_game(self, difficulty):
        self.difficulty = difficulty
        self.score = 0
        self.question_number = 0
        self.displayProblem()

    def handle_submit(self, event=None):
        # Validate input, check it, award points, and advance
        if self.locked:
            return

        text = self.entry.get().strip()
        if not Integer_Pattern.fullmatch(text):
            # Bad input never costs an attempt
            self._set_feedback("Please enter a whole number like: 42 or -54.", "orange")
            return

        if self.isCorrect(int(text), self.correct_answer):
            self.score += Points_First_Try if self.attempt == 1 else Points_Second_Try
            self._finish_question()
        elif self.attempt == 1:
            self.attempt = 2
            self.entry.delete(0, tk.END)
        else:
            self._finish_question()  # Second miss: 0 points then answer will be shown
    
    def _finish_question(self):
        # Lock input so extra Enter presses are ignored, then pause briefly so the user can read the feedback before the next screen
        self.locked = True
        self._update_status()
        self.root.after(Feedback_Delay_Ms, self._next_step)

    def _next_step(self):
        # Show the next question, or the results after the last one
        if self.question_number < Questions_Per_Game:
            self.displayProblem()
        else:
            self.displayResults()

    def _update_status(self):
        # Refresh the "Question x/10  Score: y" line at the top
        self.status_label.config(text=f"Question {self.question_number}/{Questions_Per_Game} Score: {self.score}")

    def _set_feedback(self, message, colour):
        # Show a coloured message under the Entry box
        self.feedback_label.config(text=message, fg=colour)

    @staticmethod
    def grade_for(score):
        # Return the first grade whose minimum score the user has reached
        return next(grade for cutoff, grade in Grade_Boundaries if score >= cutoff)

def main():
    # Create the single window, show the menu, and start the event loop
    root = tk.Tk()
    root.title("Maths Quiz")
    root.geometry("420x340")
    root.resizable(False, False)
    MathsQuiz(root).displayMenu()
    root.mainloop()

if __name__ == "__main__":
    main()