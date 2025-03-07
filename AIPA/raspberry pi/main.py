import time
import threading
from camera_module import CameraModule
from audio_module import AudioModule
from network_client import NetworkClient
import config

def main():
    print("Starting AI Academic Assistant on Raspberry Pi...")
    
    # Initialize modules
    network_client = NetworkClient(config.SERVER_IP, config.SERVER_PORT)
    camera_module = CameraModule(network_client)
    audio_module = AudioModule(network_client)
    
    # Start connection to server
    if not network_client.connect():
        print("Failed to connect to server. Exiting.")
        return
    
    print("Connected to server. Starting modules...")
    
    # Start modules in separate threads
    camera_thread = threading.Thread(target=camera_module.start_streaming)
    audio_thread = threading.Thread(target=audio_module.start_listening)
    speaker_thread = threading.Thread(target=audio_module.start_speaker)
    
    camera_thread.daemon = True
    audio_thread.daemon = True
    speaker_thread.daemon = True
    
    camera_thread.start()
    audio_thread.start()
    speaker_thread.start()
    
    print("AI Academic Assistant is running. Press Ctrl+C to stop.")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        network_client.disconnect()
        camera_module.stop()
        audio_module.stop()

if __name__ == "__main__":
    main()