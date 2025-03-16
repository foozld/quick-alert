# QuickAlert Project

A real-time disaster alert system that aggregates and displays emergency information from multiple sources including Twitter, Reddit, and sample data.

## Project Structure

```
quickalertproject/
├── backend/
│   ├── main.py           # FastAPI backend server
│   ├── sample_data.py    # Sample alert data provider
│   ├── requirements.txt  # Python dependencies
│   └── .env             # Environment variables
└── frontend/
    ├── index.html       # Main HTML file
    ├── css/
    │   └── styles.css   # CSS styles
    └── js/
        └── app.js       # Frontend JavaScript
```

## Setup Instructions

1. **Install Python Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**
   - Copy the `.env.example` file to `.env` (if not already done)
   - Update the following variables in `.env`:
     ```
     # Twitter API Credentials (if using Twitter integration)
     TWITTER_API_KEY=your_api_key
     TWITTER_API_SECRET=your_api_secret
     TWITTER_ACCESS_TOKEN=your_access_token
     TWITTER_ACCESS_TOKEN_SECRET=your_token_secret
     TWITTER_BEARER_TOKEN=your_bearer_token

     # Reddit API Credentials (if using Reddit integration)
     REDDIT_CLIENT_ID=your_client_id
     REDDIT_CLIENT_SECRET=your_client_secret
     REDDIT_USER_AGENT=your_user_agent
     ```

## Running the Application

1. **Start the Backend Server**
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```
   The backend will run on http://127.0.0.1:8000

2. **Start the Frontend Server**
   In a new terminal:
   ```bash
   cd frontend
   python -m http.server 8080
   ```
   Access the frontend at http://localhost:8080

## Features

- Real-time disaster alerts from multiple sources
- Interactive map display of alert locations
- Filtering by source and severity
- WebSocket connection for live updates
- Scrollable alerts panel with detailed information

## API Endpoints

- `GET /api/alerts` - Get all alerts with optional filters
  - Query parameters:
    - `source`: Filter by source (twitter, reddit)
    - `severity`: Filter by severity (High, Medium, Low)
    - `hours`: Get alerts from the last N hours (1-72)

- `GET /api/sources` - Get available alert sources
- `GET /api/severities` - Get available severity levels
- `WebSocket /ws` - Real-time alert updates

## Troubleshooting

If you encounter the "ModuleNotFoundError: No module named 'fastapi'" error:
```bash
cd backend
python -m pip install --no-cache-dir fastapi uvicorn
```

## Maintenance

- Keep dependencies updated using `pip install -r requirements.txt`
- Monitor the `alerts.log` file for any errors
- Check API rate limits for Twitter and Reddit integrations
- Update disaster keywords in `.env` as needed

## Security Notes

- Never commit the `.env` file with real API credentials
- Keep API keys and tokens secure
- Use appropriate rate limiting for production deployments 