import face_recognition
import cv2
import numpy as np
import pickle
import os
from io import BytesIO
from PIL import Image
import sys
sys.path.append('..')
import config

class FaceRecognizer:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.model_loaded = False
    
    def load_model(self):
        # Load pre-trained face encodings if available
        encodings_file = os.path.join(config.EMBEDDINGS_PATH, "encodings.pkl")
        
        if os.path.exists(encodings_file):
            with open(encodings_file, "rb") as f:
                data = pickle.load(f)
                self.known_face_encodings = data["encodings"]
                self.known_face_names = data["names"]
                self.model_loaded = True
                print(f"Loaded {len(self.known_face_names)} face profiles")
        else:
            print("No pre-trained encodings found. Need to train the model.")
            self._train_model()
    
    def _train_model(self):
        print("Training face recognition model...")
        
        # Process student images
        self._train_from_directory(config.STUDENT_IMAGES_PATH, "S_")
        
        # Process teacher images
        self._train_from_directory(config.TEACHER_IMAGES_PATH, "T_")
        
        # Save the encodings
        if self.known_face_encodings:
            encodings_file = os.path.join(config.EMBEDDINGS_PATH, "encodings.pkl")
            data = {"encodings": self.known_face_encodings, "names": self.known_face_names}
            
            os.makedirs(config.EMBEDDINGS_PATH, exist_ok=True)
            
            with open(encodings_file, "wb") as f:
                pickle.dump(data, f)
            
            self.model_loaded = True
            print(f"Model trained with {len(self.known_face_names)} face profiles")
        else:
            print("No faces found for training")
    
    def _train_from_directory(self, directory, prefix):
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
            return
        
        # Get all subdirectories (one per person)
        for person_dir in os.listdir(directory):
            person_path = os.path.join(directory, person_dir)
            
            if not os.path.isdir(person_path):
                continue
            
            # Person ID is the directory name
            person_id = prefix + person_dir
            
            # Process each image for the person
            for image_file in os.listdir(person_path):
                if not image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    continue
                
                image_path = os.path.join(person_path, image_file)
                
                # Load and encode the face
                image = face_recognition.load_image_file(image_path)
                face_encodings = face_recognition.face_encodings(image)
                
                if face_encodings:
                    # Use the first face found in the image
                    self.known_face_encodings.append(face_encodings[0])
                    self.known_face_names.append(person_id)
    
    def recognize_faces(self, frame_data):
        if not self.model_loaded:
            print("Face recognition model not loaded")
            return []
        
        # Convert frame data to image
        image = Image.open(BytesIO(frame_data))
        image_np = np.array(image)
        
        # Convert RGB to BGR (for OpenCV)
        rgb_image = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        
        # Find all faces in the current frame
        face_locations = face_recognition.face_locations(rgb_image)
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        
        recognized_names = []
        
        for face_encoding in face_encodings:
            # Compare with known faces
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"
            
            # Use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                    if name not in recognized_names:
                        recognized_names.append(name)
        
        return recognized_names
    
    def add_person(self, person_id, image_data, is_teacher=False):
        """Add a new person to the recognition database"""
        try:
            # Determine the appropriate directory
            if is_teacher:
                prefix = "T_"
                base_dir = config.TEACHER_IMAGES_PATH
            else:
                prefix = "S_"
                base_dir = config.STUDENT_IMAGES_PATH
            
            # Ensure the person directory exists
            person_dir = os.path.join(base_dir, person_id)
            os.makedirs(person_dir, exist_ok=True)
            
            # Save the image
            image_path = os.path.join(person_dir, f"{person_id}_{len(os.listdir(person_dir))}.jpg")
            
            # Convert bytes to image and save
            image = Image.open(BytesIO(image_data))
            image.save(image_path)
            
            # Update the face encoding database
            image_np = np.array(image)
            face_encodings = face_recognition.face_encodings(image_np)
            
            if face_encodings:
                self.known_face_encodings.append(face_encodings[0])
                self.known_face_names.append(prefix + person_id)
                
                # Save the updated encodings
                encodings_file = os.path.join(config.EMBEDDINGS_PATH, "encodings.pkl")
                data = {"encodings": self.known_face_encodings, "names": self.known_face_names}
                
                with open(encodings_file, "wb") as f:
                    pickle.dump(data, f)
                
                return True
            else:
                print(f"No face found in the provided image for {person_id}")
                return False
                
        except Exception as e:
            print(f"Error adding person: {str(e)}")
            return False
