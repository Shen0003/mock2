import sqlite3
import hashlib

class DatabaseManager:
    def __init__(self, db_name='udemy_clone.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'student', 'instructor'))
        )''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            instructor_id INTEGER,
            price REAL NOT NULL,
            FOREIGN KEY(instructor_id) REFERENCES users(id)
        )''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            course_id INTEGER,
            enrolled_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(student_id) REFERENCES users(id),
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )''')

        self.conn.commit()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password, email, role):
        hashed_password = self.hash_password(password)
        try:
            self.cursor.execute('''
            INSERT INTO users (username, password, email, role) 
            VALUES (?, ?, ?, ?)
            ''', (username, hashed_password, email, role))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def authenticate_user(self, username, password):
        hashed_password = self.hash_password(password)
        self.cursor.execute('''
        SELECT * FROM users 
        WHERE username = ? AND password = ?
        ''', (username, hashed_password))
        return self.cursor.fetchone()

    def get_user_role(self, username):
        self.cursor.execute('SELECT role FROM users WHERE username = ?', (username,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_user_email(self, username):
        self.cursor.execute('SELECT email FROM users WHERE username = ?', (username,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def create_course(self, title, description, instructor_id, price):
        try:
            self.cursor.execute('''
            INSERT INTO courses (title, description, instructor_id, price) 
            VALUES (?, ?, ?, ?)
            ''', (title, description, instructor_id, price))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_all_courses(self):
        self.cursor.execute('SELECT * FROM courses')
        return self.cursor.fetchall()

    def get_instructor_name(self, instructor_id):
        self.cursor.execute('SELECT username FROM users WHERE id = ?', (instructor_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 'Unknown'

    def enroll_course(self, student_id, course_id):
        self.cursor.execute('''
        SELECT * FROM enrollments WHERE student_id = ? AND course_id = ?
        ''', (student_id, course_id))
        if self.cursor.fetchone():
            return False

        try:
            self.cursor.execute('''
            INSERT INTO enrollments (student_id, course_id) 
            VALUES (?, ?)
            ''', (student_id, course_id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_enrolled_courses(self, student_id):
        self.cursor.execute('''
        SELECT courses.id, courses.title, courses.description, courses.price
        FROM courses
        INNER JOIN enrollments ON courses.id = enrollments.course_id
        WHERE enrollments.student_id = ?
        ''', (student_id,))
        return self.cursor.fetchall()

    def get_courses_by_instructor_id(self, instructor_id):
        self.cursor.execute('''
        SELECT * FROM courses WHERE instructor_id = ?
        ''', (instructor_id,))
        return self.cursor.fetchall()

    def get_enrolled_students_count(self, course_id):
        self.cursor.execute('''
        SELECT COUNT(*) FROM enrollments WHERE course_id = ?
        ''', (course_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def get_all_users(self):
        self.cursor.execute('SELECT * FROM users')
        return self.cursor.fetchall()

    def update_user_role(self, user_id, new_role):
        self.cursor.execute('''
        UPDATE users SET role = ? WHERE id = ?
        ''', (new_role, user_id))
        self.conn.commit()

    def get_total_users(self):
        self.cursor.execute('SELECT COUNT(*) FROM users')
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def get_total_courses(self):
        self.cursor.execute('SELECT COUNT(*) FROM courses')
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def get_total_enrollments(self):
        self.cursor.execute('SELECT COUNT(*) FROM enrollments')
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def close_connection(self):
        self.conn.close()