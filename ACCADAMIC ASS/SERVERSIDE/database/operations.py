import sqlite3
import os
import time
import sys
sys.path.append('..')
import config

class DatabaseOperations:
    def __init__(self):
        self.db_path = config.DATABASE_PATH
        self.conn = None
    
    def _get_connection(self):
        """Get a database connection, creating the database if it doesn't exist"""
        if self.conn is None:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return self.conn
    
    def initialize_database(self):
        """Initialize the database with required tables"""
        conn = self._get_connection()
        from database.models import create_tables
        create_tables(conn)
        
        # Add some sample data if the database is empty
        self._add_sample_data()
    
    def _add_sample_data(self):
        """Add sample data if tables are empty"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if students table is empty
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        
        if student_count == 0:
            # Add sample students
            sample_students = [
                ("S001", "John Smith", "Class-A", "john.smith@example.com", time.strftime("%Y-%m-%d")),
                ("S002", "Emily Johnson", "Class-A", "emily.j@example.com", time.strftime("%Y-%m-%d")),
                ("S003", "Michael Brown", "Class-B", "michael.b@example.com", time.strftime("%Y-%m-%d")),
                ("S004", "Sarah Lee", "Class-B", "sarah.lee@example.com", time.strftime("%Y-%m-%d"))
            ]
            
            cursor.executemany("INSERT INTO students VALUES (?, ?, ?, ?, ?)", sample_students)
        
        # Check if teachers table is empty
        cursor.execute("SELECT COUNT(*) FROM teachers")
        teacher_count = cursor.fetchone()[0]
        
        if teacher_count == 0:
            # Add sample teachers
            sample_teachers = [
                ("T001", "Dr. Robert Wilson", "Mathematics", "r.wilson@example.com"),
                ("T002", "Prof. Jennifer Adams", "Physics", "j.adams@example.com"),
                ("T003", "Ms. David Clark", "English", "d.clark@example.com")
            ]
            
            cursor.executemany("INSERT INTO teachers VALUES (?, ?, ?, ?)", sample_teachers)
        
        conn.commit()
    
    def record_attendance(self, student_id, timestamp=None):
        """Record student attendance"""
        if timestamp is None:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if the student exists
        cursor.execute("SELECT id FROM students WHERE id = ?", (student_id,))
        result = cursor.fetchone()
        
        if result:
            # Check if attendance already recorded for today
            today = timestamp.split()[0]
            cursor.execute(
                "SELECT id FROM attendance WHERE student_id = ? AND date(timestamp) = date(?)",
                (student_id, timestamp)
            )
            
            if not cursor.fetchone():
                # Record new attendance
                cursor.execute(
                    "INSERT INTO attendance (student_id, timestamp) VALUES (?, ?)",
                    (student_id, timestamp)
                )
                conn.commit()
                return True
            return False  # Already recorded
        else:
            return False  # Student not found
    
    def record_teacher_presence(self, teacher_id, timestamp=None):
        """Record teacher presence"""
        if timestamp is None:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if the teacher exists
        cursor.execute("SELECT id FROM teachers WHERE id = ?", (teacher_id,))
        result = cursor.fetchone()
        
        if result:
            # Check if presence already recorded for today
            today = timestamp.split()[0]
            cursor.execute(
                "SELECT id FROM teacher_presence WHERE teacher_id = ? AND date(timestamp) = date(?)",
                (teacher_id, timestamp)
            )
            
            if not cursor.fetchone():
                # Record new presence
                cursor.execute(
                    "INSERT INTO teacher_presence (teacher_id, timestamp) VALUES (?, ?)",
                    (teacher_id, timestamp)
                )
                conn.commit()
                return True
            return False  # Already recorded
        else:
            return False  # Teacher not found
    
    def add_reminder(self, text, timestamp=None):
        """Add a new reminder"""
        if timestamp is None:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO reminders (text, timestamp) VALUES (?, ?)",
            (text, timestamp)
        )
        conn.commit()
        return cursor.lastrowid
    
    def log_query(self, query, response, timestamp=None):
        """Log an academic query and its response"""
        if timestamp is None:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO query_log (query, response, timestamp) VALUES (?, ?, ?)",
            (query, response, timestamp)
        )
        conn.commit()
    
    def add_performance_metric(self, student_id, subject, metric_type, value, timestamp=None):
        """Add a student performance metric"""
        if timestamp is None:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO performance_metrics (student_id, subject, metric_type, value, timestamp) VALUES (?, ?, ?, ?, ?)",
            (student_id, subject, metric_type, value, timestamp)
        )
        conn.commit()
    
    def get_attendance_summary(self, date=None):
        """Get attendance summary for a specific date or today"""
        if date is None:
            date = time.strftime("%Y-%m-%d")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT s.name, s.class_id, a.timestamp
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE date(a.timestamp) = date(?)
            ORDER BY s.class_id, s.name
        """, (date,))
        
        results = cursor.fetchall()
        
        if results:
            summary = f"Attendance for {date}:\n"
            current_class = None
            
            for row in results:
                if row['class_id'] != current_class:
                    current_class = row['class_id']
                    summary += f"\n{current_class}:\n"
                
                summary += f"- {row['name']} (arrived at {row['timestamp'].split()[1]})\n"
            
            return summary
        else:
            return f"No attendance records for {date}"
    
    def get_active_reminders(self):
        """Get all active (incomplete) reminders"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, text, timestamp
            FROM reminders
            WHERE completed = 0
            ORDER BY timestamp
        """)
        
        results = cursor.fetchall()
        
        if results:
            reminders = []
            for row in results:
                reminders.append({
                    'id': row['id'],
                    'text': row['text'],
                    'timestamp': row['timestamp']
                })
            return reminders
        else:
            return []
    
    def mark_reminder_completed(self, reminder_id):
        """Mark a reminder as completed"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE reminders SET completed = 1 WHERE id = ?",
            (reminder_id,)
        )
        conn.commit()
        
        return cursor.rowcount > 0
    
    def get_student_performance(self, student_id, subject=None):
        """Get performance metrics for a student"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if subject:
            cursor.execute("""
                SELECT metric_type, value, timestamp
                FROM performance_metrics
                WHERE student_id = ? AND subject = ?
                ORDER BY timestamp DESC
            """, (student_id, subject))
        else:
            cursor.execute("""
                SELECT subject, metric_type, value, timestamp
                FROM performance_metrics
                WHERE student_id = ?
                ORDER BY subject, timestamp DESC
            """, (student_id,))
        
        results = cursor.fetchall()
        
        if results:
            metrics = []
            for row in results:
                metric = {
                    'metric_type': row['metric_type'],
                    'value': row['value'],
                    'timestamp': row['timestamp']
                }
                
                if not subject:
                    metric['subject'] = row['subject']
                
                metrics.append(metric)
            return metrics
        else:
            return []
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None