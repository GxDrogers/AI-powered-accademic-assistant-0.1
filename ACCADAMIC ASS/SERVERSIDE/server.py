import socket
import threading
import struct
import time
import queue
import os
import json
from face_recognition.recognizer import FaceRecognizer
from nlp.intent_classifier import IntentClassifier
from nlp.query_processor import QueryProcessor
from database.operations import DatabaseOperations
from web_interface.app import start_web_server
import config

class Server:
    def __init__(self):
        self.server_socket = None
        self.clients = []
        self.running = False
        self.face_recognizer = FaceRecognizer()
        self.intent_classifier = IntentClassifier()
        self.query_processor = QueryProcessor()
        self.db = DatabaseOperations()
        
        # Ensure directories exist
        os.makedirs(config.FACE_RECOGNITION_MODEL_PATH, exist_ok=True)
        os.makedirs(config.EMBEDDINGS_PATH, exist_ok=True)
        os.makedirs(config.STUDENT_IMAGES_PATH, exist_ok=True)
        os.makedirs(config.TEACHER_IMAGES_PATH, exist_ok=True)
    
    def start(self):
        # Initialize database
        self.db.initialize_database()
        
        # Start the server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', config.SERVER_PORT))
        self.server_socket.listen(5)
        
        self.running = True
        print(f"Server started on port {config.SERVER_PORT}")
        
        # Start web interface in a separate thread
        web_thread = threading.Thread(target=start_web_server, args=(config.WEB_PORT,))
        web_thread.daemon = True
        web_thread.start()
        print(f"Web interface started on port {config.WEB_PORT}")
        
        # Load face recognition model
        self.face_recognizer.load_model()
        
        # Accept client connections
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"New connection from {address}")
                
                # Start client handling thread
                client_thread = threading.Thread(target=self._handle_client, args=(client_socket, address))
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                print(f"Error accepting connection: {str(e)}")
    
    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        
        for client in self.clients:
            client[0].close()
        
        print("Server stopped")
    
    def _handle_client(self, client_socket, address):
        # Add client to list
        client_info = (client_socket, address)
        self.clients.append(client_info)
        
        try:
            while self.running:
                # Read header (5 bytes: 1 byte message type + 4 bytes length)
                header = self._recv_all(client_socket, 5)
                if not header:
                    break
                
                msg_type, data_len = struct.unpack("!BI", header)
                
                # Read data
                data = self._recv_all(client_socket, data_len)
                if not data:
                    break
                
                # Process based on message type
                if msg_type == 1:  # Frame data
                    self._process_frame(client_socket, data)
                elif msg_type == 2:  # Audio data
                    self._process_audio(client_socket, data)
        
        except Exception as e:
            print(f"Error handling client {address}: {str(e)}")
        finally:
            client_socket.close()
            if client_info in self.clients:
                self.clients.remove(client_info)
            print(f"Connection from {address} closed")
    
    def _recv_all(self, sock, n):
        data = b''
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data
    
    def _process_frame(self, client_socket, frame_data):
        # Process the frame for face recognition
        names = self.face_recognizer.recognize_faces(frame_data)
        
        if names:
            # Record attendance for recognized faces
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            for name in names:
                # Check if student or teacher
                if name.startswith("S_"):  # Student
                    student_id = name[2:]
                    self.db.record_attendance(student_id, current_time)
                    print(f"Recorded attendance for student {student_id}")
                elif name.startswith("T_"):  # Teacher
                    teacher_id = name[2:]
                    self.db.record_teacher_presence(teacher_id, current_time)
                    print(f"Recorded presence for teacher {teacher_id}")
            
            # Send text response
            response = f"Recognized: {', '.join(names)}"
            self._send_text_response(client_socket, response)
    
    def _process_audio(self, client_socket, audio_data):
        # Convert audio to text using speech recognition
        import speech_recognition as sr
        from io import BytesIO
        import wave
        
        recognizer = sr.Recognizer()
        
        # Create a WAV file in memory
        wav_file = BytesIO()
        with wave.open(wav_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 2 bytes per sample (16-bit)
            wf.setframerate(16000)
            wf.writeframes(audio_data)
        
        wav_file.seek(0)
        
        try:
            with sr.AudioFile(wav_file) as source:
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio)
                print(f"Recognized speech: {text}")
                
                # Process the intent
                intent = self.intent_classifier.classify(text)
                
                if intent == "attendance_query":
                    # Query attendance information
                    response = self.db.get_attendance_summary()
                    self._send_text_response(client_socket, response)
                
                elif intent == "academic_query":
                    # Process academic question
                    answer = self.query_processor.process_query(text)
                    self._send_text_response(client_socket, answer)
                    
                    # Send audio response
                    self._generate_and_send_audio(client_socket, answer)
                
                elif intent == "reminder":
                    # Set a reminder
                    parts = text.lower().split("remind")
                    if len(parts) > 1:
                        reminder_text = parts[1].strip()
                        self.db.add_reminder(reminder_text)
                        response = f"Reminder set: {reminder_text}"
                        self._send_text_response(client_socket, response)
                
                else:
                    # General conversation
                    response = "I'm your academic assistant. How can I help you with your classes today?"
                    self._send_text_response(client_socket, response)
        
        except sr.UnknownValueError:
            self._send_text_response(client_socket, "Sorry, I didn't understand that.")
        except sr.RequestError:
            self._send_text_response(client_socket, "Sorry, I'm having trouble processing your request.")
        except Exception as e:
            print(f"Error processing audio: {str(e)}")
            self._send_text_response(client_socket, "Sorry, an error occurred.")
    
    def _send_text_response(self, client_socket, text):
        try:
            # Encode text to bytes
            text_bytes = text.encode('utf-8')
            
            # Prepare header (message type + data length)
            header = struct.pack("!BI", 4, len(text_bytes))  # 4 = text response
            
            # Send header followed by data
            client_socket.sendall(header + text_bytes)
        except Exception as e:
            print(f"Error sending text response: {str(e)}")
    
    def _generate_and_send_audio(self, client_socket, text):
        try:
            import pyttsx3
            
            # Initialize the TTS engine
            engine = pyttsx3.init()
            
            # Set properties
            engine.setProperty('rate', 150)  # Speed of speech
            engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
            
            # Save speech to a BytesIO object
            import io
            output = io.BytesIO()
            
            def save_to_buffer(audio):
                output.write(audio)
            
            engine.connect('write', save_to_buffer)
            engine.say(text)
            engine.runAndWait()
            
            # Get the audio data
            audio_data = output.getvalue()
            
            # Prepare header (message type + data length)
            header = struct.pack("!BI", 3, len(audio_data))  # 3 = audio response
            
            # Send header followed by data
            client_socket.sendall(header + audio_data)
        except Exception as e:
            print(f"Error generating/sending audio: {str(e)}")

if __name__ == "__main__":
    server = Server()
    try:
        server.start()
    except KeyboardInterrupt:
        print("Shutting down server...")
        server.stop()