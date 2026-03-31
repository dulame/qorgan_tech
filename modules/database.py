import sqlite3
from datetime import datetime
from pathlib import Path
import config

class Database:
    def __init__(self, db_path=config.DATABASE_PATH):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                daily_notifications BOOLEAN DEFAULT 1,
                timezone TEXT DEFAULT 'UTC'
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                recommendation_text TEXT NOT NULL,
                recommendation_type TEXT DEFAULT 'email',
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_recommendations (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                recommendation_date DATE DEFAULT CURRENT_DATE,
                emails TEXT,
                companies TEXT,
                news TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_checks (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                hashed_password TEXT NOT NULL,
                strength_score INTEGER,
                strength_text TEXT,
                crack_time_offline TEXT,
                crack_time_seconds REAL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        conn.commit()
        conn.close()

    def add_user(self, user_id, username=None, first_name=None, last_name=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name))
            conn.commit()
        except Exception as e:
            print(f"Error adding user: {e}")
        finally:
            conn.close()

    def get_user(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user

    def add_recommendation(self, user_id, recommendation_text, rec_type='email'):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO recommendations 
                (user_id, recommendation_text, recommendation_type)
                VALUES (?, ?, ?)
            ''', (user_id, recommendation_text, rec_type))
            conn.commit()
        except Exception as e:
            print(f"Error adding recommendation: {e}")
        finally:
            conn.close()

    def get_recommendations(self, user_id, limit=10):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM recommendations 
            WHERE user_id = ?
            ORDER BY added_at DESC
            LIMIT ?
        ''', (user_id, limit))
        recommendations = cursor.fetchall()
        conn.close()
        return recommendations

    def get_all_active_users(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id FROM users 
            WHERE daily_notifications = 1
        ''')
        users = cursor.fetchall()
        conn.close()
        return [u[0] for u in users]

    def log_daily_recommendations(self, user_id, emails, companies, news):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO daily_recommendations 
                (user_id, emails, companies, news)
                VALUES (?, ?, ?, ?)
            ''', (user_id, emails, companies, news))
            conn.commit()
        except Exception as e:
            print(f"Error logging daily recommendations: {e}")
        finally:
            conn.close()

    def log_password_check(self, user_id, hashed_password, strength_score, strength_text, crack_time_offline, crack_time_seconds):
        """Log a password check to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO password_checks 
                (user_id, hashed_password, strength_score, strength_text, crack_time_offline, crack_time_seconds)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, hashed_password, strength_score, strength_text, crack_time_offline, crack_time_seconds))
            conn.commit()
        except Exception as e:
            print(f"Error logging password check: {e}")
        finally:
            conn.close()

    def get_password_checks(self, user_id=None, limit=None):
        """Get all password checks, optionally filtered by user_id"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('''
                SELECT * FROM password_checks 
                WHERE user_id = ?
                ORDER BY checked_at DESC
            ''', (user_id,) if not limit else (user_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM password_checks
                ORDER BY checked_at DESC
            ''')
        
        if limit:
            checks = cursor.fetchmany(limit)
        else:
            checks = cursor.fetchall()
        
        conn.close()
        return checks

    def get_all_password_checks(self):
        """Get all password checks from database for export"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, checked_at, hashed_password, 
                   strength_score, strength_text, crack_time_offline, 
                   crack_time_seconds
            FROM password_checks
            ORDER BY checked_at DESC
        ''')
        checks = cursor.fetchall()
        conn.close()
        return checks
