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
    
    def __init__(self, root): #init runs automatically when i write MathsQuiz(root).self means "particular quiz object"
        self.root = root # Stores the main window
        self.frame = None # The current screen and it's empty until one is built
        self.entry = None # This is the answer box and it only exist during a question
        self.status_label = None # The "Question 3/10 Score: 20" line
        self.feedback_label = None # The "Correct" and "Wrong" message

        self.difficulty = "Easy" # The chosen level and it will overwrite when the used picks one
        self.score = 0 # The runnin g total
        self.question_number = 0 # How many questions have been asked already
        self.attempt = 1 # It checks if its the first or second attempt
        self.correct_answer = 0 # This shows the correct answer if user input is wrong 
        self.locked = False  # Set to True while the feedback appear so additional presses to enter are disregarded

    # Replace the current screen. One Tk root, one swapped frame
    def _new_frame(self): # It is an internal helper because of the leading underscore 
        if self.frame is not None:
            self.frame.destroy()
        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True, fill="both")
        return self.frame

    # Requires Function
    # This show difficulty buttons (Easy / Moderate / Advanced)
    def displayMenu(self):
        frame = self._new_frame()
        tk.Label(frame, text="DIFFICULTY LEVEL", font=("Times New Roman", 18, "bold")).pack(pady=20)
        for number, name in enumerate(Difficulties, start=1):
            tk.Button(frame, text=f"{number}. {name}", width=20, font=("Times New Roman", 12), command=lambda level=name: self._start_game(level),).pack(pady=6)
            
    # Returns a single random integer whose digit count fits to the difficulty
    @staticmethod # Marks a method that doesn't use. It needs only the output
    def randomInt(difficulty):
        low, high = Difficulties[difficulty]
        return random.randint(low, high)
        
    # Randomly returns either a Additon or Subtracion 
    @staticmethod
    def decideOperation():
        return random.choice(["+", "-"])

    # This shows and generates a question so that it is clear and focus to the entry
    def displayProblem(self):
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

        self.entry = tk.Entry(frame, font=("Arial", 16), width=10, justify="center")
        self.entry.pack()
        self.entry.focus_set()
        self.entry.bind("<Return>", self.handle_submit)

        self.feedback_label = tk.Label(frame, text="", font=("Times New Roman", 12), wraplength=380)
        self.feedback_label.pack(pady=12)

        tk.Button(frame, text="Submit", width=12, font=("Times New Roman", 12), command=self.handle_submit).pack()

    # This check and verifies the input of the user wether it is right or wrong
    def isCorrect(self, user_answer, correct_answer):
        if user_answer == correct_answer:
            self._set_feedback("Correct! :>", "green")
            return True
        if self.attempt == 1:
            self._set_feedback("Wrong. You have one more try. :|", "red")
        else:
            self._set_feedback(f"Wrong. The answer was {correct_answer}. :<", "red")
        return False

    # This display the result of user and asks if user wants to play again
    def displayResults(self):
        frame = self._new_frame()
        tk.Label(frame, text="Quiz Complete! <3", font=("Times New Roman", 20, "bold")).pack(pady=20)
        tk.Label(frame, text=f"Score: {self.score} / {Max_Score}", font=("Times New Roman", 16)).pack()
        tk.Label(frame, text=f"Rank: {self.grade_for(self.score)}", font=("Times New Roman", 16)).pack(pady=8)

        self.root.update_idletasks()  # Before the dialog box opens it write down the results
        if messagebox.askyesno("Play again?", "Would you like to play again?"):
            self.displayMenu()
        else:
            self.root.destroy()

    # Helpers

    # This start the game 
    def _start_game(self, difficulty):
        self.difficulty = difficulty
        self.score = 0
        self.question_number = 0
        self.displayProblem()

    # It validate input then check it folllow it by awarding points and advance
    def handle_submit(self, event=None):
        if self.locked:
            return

        # A bad input never costs an attempt 
        text = self.entry.get().strip()
        if not Integer_Pattern.fullmatch(text):
            self._set_feedback("Please enter a whole number like: 42 or -54.", "orange")
            return
        
        # This part runs the result of the user and it will determine the score of each question and advances the next part 
        if self.isCorrect(int(text), self.correct_answer):
            self.score += Points_First_Try if self.attempt == 1 else Points_Second_Try
            self._finish_question()
        elif self.attempt == 1:
            self.attempt = 2
            self.entry.delete(0, tk.END)
        else:
            self._finish_question()  # second miss: 0 points and answer will be shown
            
    # It locks the input of user and after a short pause it moves on to the next step
    def _finish_question(self):
        self.locked = True
        self._update_status()
        self.root.after(Feedback_Delay_Ms, self._next_step)

    # It shows the next question or result once all questions are done
    def _next_step(self):
        if self.question_number < Questions_Per_Game:
            self.displayProblem()
        else:
            self.displayResults()
            
    # This refreshes the "Question: x/10 Score: Y" at the top of the screen
    def _update_status(self):
        self.status_label.config(
            text=f"Question {self.question_number}/{Questions_Per_Game} Score: {self.score}")
        
    # This is the color part of the messages display under the answer box
    def _set_feedback(self, message, colour):
        self.feedback_label.config(text=message, fg=colour)

    # This returns the grade of the user 
    @staticmethod
    def grade_for(score):
        return next(grade for cutoff, grade in Grade_Boundaries if score >= cutoff)

# It creates the window and shows the difficulty menu which eventually starts the event loop
def main():
    root = tk.Tk()
    root.title("Maths Quiz")
    root.geometry("420x340")
    root.resizable(False, False)
    MathsQuiz(root).displayMenu()
    root.mainloop()

# This runs only when this file is executed directly not when imported
if __name__ == "__main__":
    main()

