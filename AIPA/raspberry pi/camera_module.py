import io
import time
import threading
import picamera
import config

class CameraModule:
    def __init__(self, network_client):
        self.network_client = network_client
        self.camera = None
        self.running = False
        
    def start_streaming(self):
        self.running = True
        self.camera = picamera.PiCamera()
        self.camera.resolution = config.CAMERA_RESOLUTION
        self.camera.framerate = config.CAMERA_FRAMERATE
        
        # Let camera warm up
        time.sleep(2)
        
        print("Camera module started")
        
        try:
            while self.running:
                # Capture frame
                stream = io.BytesIO()
                self.camera.capture(stream, format='jpeg', use_video_port=True)
                frame = stream.getvalue()
                
                # Send frame to server
                self.network_client.send_frame(frame)
                
                # Small delay to control frame rate
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Camera error: {str(e)}")
        finally:
            if self.camera:
                self.camera.close()
    
    def stop(self):
        self.running = False