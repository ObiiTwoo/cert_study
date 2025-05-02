import mysql.connector
import random

def get_questions(category=None):
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Fluffy14", 
        database="cert_study"
    )
    cursor = db.cursor()
    query = "SELECT id, question_text, answer, option_a, option_b, option_c, option_d FROM questions"
    if category:
        query += " WHERE category = %s"
        cursor.execute(query, (category,))
    else:
        cursor.execute(query)
    questions = cursor.fetchall()
    db.close()
    return questions

def run_quiz(category=None, num_questions=3):
    questions = get_questions(category)
    if not questions:
        print("No questions found!")
        return
    random.shuffle(questions)
    score = 0
    for q in questions[:num_questions]:
        print(f"\nQuestion: {q[1]}")
        options = [q[3], q[4], q[5], q[6]]
        random.shuffle(options)
        for i, opt in enumerate(options, 1):
            print(f"{i}. {opt}")
        try:
            answer = int(input("Enter the number of your answer (1-4): "))
            if 1 <= answer <= 4:
                if options[answer - 1] == q[2]:
                    print("Correct!")
                    score += 1
                else:
                    print(f"Wrong! Correct answer: {q[2]}")
            else:
                print("Invalid input! Skipping question.")
        except ValueError:
            print("Please enter a number! Skipping question.")
    print(f"\nYour score: {score}/{num_questions}")

if __name__ == "__main__":
    print("Welcome to the Cert Study Quiz!")
    category = input("Enter category (Network+, Security+, or leave blank for all): ").strip()
    category = category if category in ["Network+", "Security+"] else None
    run_quiz(category)