import socket
import json
import struct
import threading
import time

class NetworkClient:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = None
        self.connected = False
        self.response_handler_thread = None
    
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_ip, self.server_port))
            self.connected = True
            
            # Start response handler thread
            self.response_handler_thread = threading.Thread(target=self._handle_responses)
            self.response_handler_thread.daemon = True
            self.response_handler_thread.start()
            
            print(f"Connected to server at {self.server_ip}:{self.server_port}")
            return True
        except Exception as e:
            print(f"Connection error: {str(e)}")
            return False
    
    def disconnect(self):
        if self.connected:
            self.connected = False
            if self.socket:
                self.socket.close()
            print("Disconnected from server")
    
    def send_frame(self, frame_data):
        if not self.connected:
            return False
        
        try:
            # Prepare header (message type + data length)
            header = struct.pack("!BI", 1, len(frame_data))  # 1 = frame data
            
            # Send header followed by data
            self.socket.sendall(header + frame_data)
            return True
        except Exception as e:
            print(f"Error sending frame: {str(e)}")
            self.connected = False
            return False
    
    def send_audio(self, audio_data):
        if not self.connected:
            return False
        
        try:
            # Prepare header (message type + data length)
            header = struct.pack("!BI", 2, len(audio_data))  # 2 = audio data
            
            # Send header followed by data
            self.socket.sendall(header + audio_data)
            return True
        except Exception as e:
            print(f"Error sending audio: {str(e)}")
            self.connected = False
            return False
    
    def _handle_responses(self):
        from audio_module import AudioModule
        
        while self.connected:
            try:
                # Read header (5 bytes: 1 byte message type + 4 bytes length)
                header = self._recv_all(5)
                if not header:
                    break
                
                msg_type, data_len = struct.unpack("!BI", header)
                
                # Read data
                data = self._recv_all(data_len)
                if not data:
                    break
                
                # Process based on message type
                if msg_type == 3:  # Audio response
                    # Get the AudioModule instance from main
                    import sys, inspect
                    for frame_info in inspect.stack():
                        frame = frame_info[0]
                        if 'self' in frame.f_locals and isinstance(frame.f_locals['self'], AudioModule):
                            audio_module = frame.f_locals['self']
                            audio_module.play_audio(data)
                            break
                
                elif msg_type == 4:  # Text response
                    text = data.decode('utf-8')
                    print(f"Server: {text}")
                
            except Exception as e:
                print(f"Error handling server response: {str(e)}")
                self.connected = False
                break
    
    def _recv_all(self, n):
        data = b''
        while len(data) < n:
            packet = self.socket.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data