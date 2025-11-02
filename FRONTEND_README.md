# Frontend Usage

## Starting the Application

### 1. Start the Backend Server
```bash
python3 server.py
```
The API will run on `http://localhost:8000`

### 2. Start the Frontend (in a new terminal)
```bash
streamlit run frontend.py
```
The Streamlit app will open automatically in your browser at `http://localhost:8501`

## Requirements

Make sure you have installed all dependencies:
```bash
pip install -r requirements.txt
```

Key frontend dependencies:
- `streamlit==1.39.0` - Web framework
- `requests==2.31.0` - HTTP client for API calls
