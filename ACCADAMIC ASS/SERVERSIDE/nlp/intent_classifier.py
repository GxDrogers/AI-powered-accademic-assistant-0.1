import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download NLTK resources if not already downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class IntentClassifier:
    def __init__(self):
        self.attendance_keywords = [
            'attendance', 'present', 'absent', 'who is here', 'who\'s here', 
            'who came', 'mark attendance', 'take attendance', 'record attendance',
            'class attendance', 'students present'
        ]
        
        self.academic_keywords = [
            'what is', 'define', 'explain', 'how to', 'when was', 'who is',
            'where is', 'why does', 'calculate', 'solve', 'formula', 'concept',
            'subject', 'topic', 'chapter', 'homework', 'assignment', 'question',
            'problem', 'solution', 'answer', 'help me', 'can you help'
        ]
        
        self.reminder_keywords = [
            'remind', 'reminder', 'remember', 'note', 'don\'t forget', 
            'schedule', 'set reminder', 'set a reminder', 'create reminder',
            'remind me', 'remind us', 'remind the class'
        ]
        
        self.stopwords = set(stopwords.words('english'))
    
    def classify(self, text):
        # Convert to lowercase
        text = text.lower()
        
        # Tokenize
        words = word_tokenize(text)
        
        # Remove stopwords
        filtered_words = [w for w in words if w not in self.stopwords]
        
        # Check for keywords
        for keyword in self.attendance_keywords:
            if keyword in text:
                return "attendance_query"
        
        for keyword in self.reminder_keywords:
            if keyword in text:
                return "reminder"
        
        # Academic query is more generic, so check it last
        for keyword in self.academic_keywords:
            if keyword in text:
                return "academic_query"
        
        # If no specific intent is found, treat as a general query
        return "general_query"
