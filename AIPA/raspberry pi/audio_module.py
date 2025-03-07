import pyaudio
import wave
import numpy as np
import threading
import queue
import time
import config

class AudioModule:
    def __init__(self, network_client):
        self.network_client = network_client
        self.audio = pyaudio.PyAudio()
        self.listening = False
        self.speaking = False
        self.audio_queue = queue.Queue()
        
    def start_listening(self):
        self.listening = True
        
        # Set up microphone stream
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=config.AUDIO_RATE,
            input=True,
            frames_per_buffer=config.AUDIO_CHUNK
        )
        
        print("Audio listening started")
        
        # Variables for voice activity detection
        silence_threshold = 500
        silence_counter = 0
        speech_detected = False
        audio_buffer = []
        
        try:
            while self.listening:
                data = stream.read(config.AUDIO_CHUNK)
                audio_array = np.frombuffer(data, dtype=np.int16)
                volume = np.abs(audio_array).mean()
                
                # Voice activity detection
                if volume > silence_threshold:
                    silence_counter = 0
                    speech_detected = True
                    audio_buffer.append(data)
                elif speech_detected:
                    silence_counter += 1
                    audio_buffer.append(data)
                    
                    # End of speech detected
                    if silence_counter > 10:  # About 0.6 seconds of silence
                        if len(audio_buffer) > 5:  # Minimum length check
                            audio_data = b''.join(audio_buffer)
                            self.network_client.send_audio(audio_data)
                        
                        # Reset for next utterance
                        speech_detected = False
                        audio_buffer = []
                
        except Exception as e:
            print(f"Audio input error: {str(e)}")
        finally:
            stream.stop_stream()
            stream.close()
    
    def start_speaker(self):
        self.speaking = True
        
        # Set up speaker stream
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=config.AUDIO_RATE,
            output=True
        )
        
        print("Audio output started")
        
        try:
            while self.speaking:
                try:
                    audio_data = self.audio_queue.get(timeout=0.5)
                    stream.write(audio_data)
                    self.audio_queue.task_done()
                except queue.Empty:
                    continue
        except Exception as e:
            print(f"Audio output error: {str(e)}")
        finally:
            stream.stop_stream()
            stream.close()
    
    def play_audio(self, audio_data):
        self.audio_queue.put(audio_data)
    
    def stop(self):
        self.listening = False
        self.speaking = False
        self.audio.terminate()