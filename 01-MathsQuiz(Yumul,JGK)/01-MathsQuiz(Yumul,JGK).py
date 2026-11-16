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