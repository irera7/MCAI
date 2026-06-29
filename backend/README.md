# AI Model Builder - Backend

Python FastAPI backend for the AI Model Builder application.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt

# Optional: Install additional packages for ONNX inference, TFLite export, etc.
pip install -r requirements-optional.txt
```

**Note:** If you encounter errors with `onnxruntime`, you can skip it. ONNX export will still work, but ONNX inference will require manual installation of onnxruntime later.

4. Create `.env` file (copy from `.env.example`):
```bash
copy .env.example .env
```

5. Run the server:
```bash
python main.py
```

The API will be available at `http://127.0.0.1:8181`

## API Documentation

Once the server is running, access the interactive API documentation at:
- Swagger UI: `http://127.0.0.1:8181/docs`
- ReDoc: `http://127.0.0.1:8181/redoc`

## Project Structure

```
backend/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── api/
│   └── routes/            # API endpoints
│       ├── project.py     # Project management
│       ├── data.py        # Data handling
│       ├── training.py    # Training endpoints
│       ├── inference.py   # Inference endpoints
│       ├── export_routes.py # Model export
│       └── system.py      # System info
├── models/                # Model architectures (to be implemented)
├── data/                  # Data processing utilities (to be implemented)
├── training/              # Training logic (to be implemented)
├── inference/             # Inference logic (to be implemented)
├── exporters/             # Model exporters (to be implemented)
├── cloud/                 # Cloud training integration (to be implemented)
└── utils/
    ├── config.py          # Configuration management
    └── logger.py          # Logging utilities
```

## Development

The backend is designed to be modular and extensible. Each data modality (image, text, audio, etc.) will have its own module with specific implementations.

