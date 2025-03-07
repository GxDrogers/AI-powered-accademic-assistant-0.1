import sqlite3
import os
import sys
sys.path.append('..')
import config

def create_tables(conn):
    """Create the database tables if they don't exist"""
    cursor = conn.cursor()
    
    # Students table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        class_id TEXT,
        email TEXT,
        registration_date TEXT
    )
    ''')
    
    # Teachers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teachers (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        subject TEXT,
        email TEXT
    )
    ''')
    
    # Attendance table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        status TEXT DEFAULT 'present',
        FOREIGN KEY (student_id) REFERENCES students (id)
    )
    ''')
    
    # Teacher presence table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teacher_presence (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (teacher_id) REFERENCES teachers (id)
    )
    ''')
    
    # Reminders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        completed INTEGER DEFAULT 0
    )
    ''')
    
    # Academic queries log
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS query_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT NOT NULL,
        response TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    ''')
    
    # Performance metrics table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS performance_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        subject TEXT NOT NULL,
        metric_type TEXT NOT NULL,
        value REAL NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students (id)
    )
    ''')
    
    # Commit the changes
    conn.commit()