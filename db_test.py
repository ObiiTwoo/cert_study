import mysql.connector

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Fluffy14",
        database="cert_study"
    )
    print("Connected to MySQL!")
    cursor = db.cursor()

    # Test scenarios table
    cursor.execute("SELECT * FROM scenarios")
    print("\nScenarios:")
    for row in cursor.fetchall():
        print(row)

    # Test users table
    cursor.execute("SELECT * FROM users")
    print("\nUsers:")
    for row in cursor.fetchall():
        print(row)

    # Test questions table
    cursor.execute("SELECT * FROM questions")
    print("\nQuestions:")
    for row in cursor.fetchall():
        print(row)

    # Test firewall_rules table
    cursor.execute("SELECT * FROM firewall_rules")
    print("\nFirewall Rules:")
    for row in cursor.fetchall():
        print(row)

    # Test user_progress table
    cursor.execute("SELECT * FROM user_progress")
    print("\nUser Progress:")
    for row in cursor.fetchall():
        print(row)

    db.close()
except mysql.connector.Error as err:
    print(f"Error: {err}")