'''
academic-assistant/
├── raspberry_pi/
│   ├── main.py               # Main script for Raspberry Pi
│   ├── camera_module.py      # Camera handling and streaming
│   ├── audio_module.py       # Microphone input and speaker output
│   ├── network_client.py     # Communication with laptop server
│   └── config.py             # Configuration settings
│
├── laptop/
│   ├── server.py             # Main server application
│   ├── face_recognition/     # Face recognition module
│   │   ├── __init__.py
│   │   ├── trainer.py        # Train face recognition models
│   │   └── recognizer.py     # Recognize faces
│   ├── nlp/                  # Natural Language Processing
│   │   ├── __init__.py
│   │   ├── intent_classifier.py  # Classify user intents
│   │   └── query_processor.py    # Process academic queries
│   ├── database/             # Database operations
│   │   ├── __init__.py
│   │   ├── models.py         # Database models
│   │   └── operations.py     # CRUD operations
│   ├── web_interface/        # Web interface
│   │   ├── static/           # CSS, JS files
│   │   ├── templates/        # HTML templates
│   │   └── app.py            # Web application
│   └── config.py             # Configuration settings
'''