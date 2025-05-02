import tkinter as tk
from tkinter import messagebox
import mysql.connector
import random

class FlashcardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cert Study Game")
        self.root.geometry("600x400")
        
        # Connect to database
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Fluffy14",
            database="cert_study"
        )
        self.cursor = self.db.cursor()
        self.questions = self.get_questions()
        random.shuffle(self.questions)
        self.current_question = 0
        
        # GUI elements
        self.question_label = tk.Label(root, text="", wraplength=500, font=("Arial", 14))
        self.question_label.pack(pady=20)
        
        self.option_buttons = []
        for i in range(4):
            btn = tk.Button(root, text="", font=("Arial", 12), command=lambda x=i: self.check_answer(x))
            btn.pack(pady=5)
            self.option_buttons.append(btn)
        
        self.next_button = tk.Button(root, text="Next Question", command=self.load_question)
        self.next_button.pack(pady=20)
        
        self.load_question()
    
    def get_questions(self):
        self.cursor.execute("SELECT question_text, answer, option_a, option_b, option_c, option_d FROM questions")
        return self.cursor.fetchall()
    
    def load_question(self):
        if self.current_question < len(self.questions):
            q = self.questions[self.current_question]
            self.question_label.config(text=q[0])
            options = [q[2], q[3], q[4], q[5]]
            random.shuffle(options)
            for i, btn in enumerate(self.option_buttons):
                btn.config(text=options[i])
            self.current_question += 1
        else:
            messagebox.showinfo("Quiz Complete", "No more questions!")
    
    def check_answer(self, selected):
        q = self.questions[self.current_question - 1]
        if self.option_buttons[selected]["text"] == q[1]:
            messagebox.showinfo("Result", "Correct!")
        else:
            messagebox.showinfo("Result", f"Wrong! Correct answer: {q[1]}")
    
    def __del__(self):
        self.db.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = FlashcardApp(root)
    root.mainloop()