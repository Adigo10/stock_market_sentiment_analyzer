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

## Features

- **Clean, Minimal UI**: Purple gradient design with centered layout
- **Company Selection**: Dropdown menu populated from the `/companies` endpoint
- **Analyze Button**: Click "🚀 Analyze" to fetch and analyze company news
- **Top 5 Articles Display**: Shows the top 5 ranked articles with:
  - Headline (numbered)
  - Summary/Description
  - Simple, readable format
- **Full Data View**: Expandable section to see complete JSON response
- **Flexible Output**: Automatically adapts to different data structures (list, dict, or custom formats)

## UI Design

- **Wide Layout**: Full-width display for better readability
- **No Sidebar**: Clean, distraction-free interface
- **Gradient Buttons**: Purple to pink gradient with hover effects
- **Responsive**: Works on different screen sizes

## Requirements

Make sure you have installed all dependencies:
```bash
pip install -r requirements.txt
```

Key frontend dependencies:
- `streamlit==1.39.0` - Web framework
- `requests==2.31.0` - HTTP client for API calls
