import os
import sys
sys.path.append('..')
from recognizer import FaceRecognizer
import config

def train_model():
    """Utility function to (re)train the face recognition model"""
    recognizer = FaceRecognizer()
    # Force training
    recognizer._train_model()
    print("Training complete")

if __name__ == "__main__":
    train_model()