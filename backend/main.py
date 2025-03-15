from fastapi import FastAPI, WebSocket, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict
import asyncio
from datetime import datetime, timedelta
import logging
import os
import tweepy
from dotenv import load_dotenv
from sample_data import SampleDataProvider

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.getenv('LOG_FILE', 'alerts.log')
)
logger = logging.getLogger(__name__)

# Twitter API Configuration
twitter_client = tweepy.Client(
    bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
    consumer_key=os.getenv('TWITTER_API_KEY'),
    consumer_secret=os.getenv('TWITTER_API_SECRET'),
    access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
    access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
)

app = FastAPI(
    title="QuickAlert API",
    description="Real-time disaster alert system API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize sample data provider
sample_data = SampleDataProvider()

# Store active WebSocket connections
active_connections: List[WebSocket] = []

# Get disaster keywords from environment
DISASTER_KEYWORDS = os.getenv('DISASTER_KEYWORDS', '').split(',')

async def fetch_twitter_alerts() -> List[Dict]:
    """Fetch recent disaster-related tweets."""
    try:
        query = ' OR '.join(DISASTER_KEYWORDS)
        tweets = twitter_client.search_recent_tweets(
            query=query,
            max_results=10,
            tweet_fields=['created_at', 'geo', 'public_metrics']
        )
        
        alerts = []
        if tweets.data:
            for tweet in tweets.data:
                alert = {
                    "source": "twitter",
                    "text": tweet.text,
                    "severity": "Medium",  # Default severity, could be enhanced with NLP
                    "created_at": tweet.created_at.isoformat(),
                    "coordinates": tweet.geo.coordinates if tweet.geo else None,
                    "engagement": {
                        "retweets": tweet.public_metrics['retweet_count'],
                        "likes": tweet.public_metrics['like_count'],
                        "replies": tweet.public_metrics['reply_count']
                    }
                }
                alerts.append(alert)
        return alerts
    except Exception as e:
        logger.error(f"Error fetching Twitter alerts: {str(e)}")
        return []

async def fetch_all_alerts() -> List[Dict]:
    """Fetch alerts from all sources."""
    twitter_alerts = await fetch_twitter_alerts()
    sample_alerts = sample_data.get_all_alerts()  # Get some sample data if APIs fail
    return twitter_alerts + sample_alerts

@app.get("/")
async def root():
    """Root endpoint returning API status."""
    return {
        "message": "QuickAlert API is running",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/alerts")
async def get_alerts(
    source: Optional[str] = Query(None, description="Filter by source (twitter)"),
    severity: Optional[str] = Query(None, description="Filter by severity (High, Medium, Low)"),
    hours: Optional[int] = Query(24, description="Get alerts from the last N hours", ge=1, le=72)
):
    """Get filtered alerts."""
    try:
        alerts = await fetch_all_alerts()
        
        # Apply filters
        if source:
            alerts = [a for a in alerts if a["source"] == source]
        if severity:
            alerts = [a for a in alerts if a["severity"] == severity]
            
        # Filter by time
        cutoff_time = datetime.now() - timedelta(hours=hours)
        alerts = [
            a for a in alerts 
            if datetime.fromisoformat(a["created_at"]) > cutoff_time
        ]
            
        return {
            "alerts": alerts,
            "timestamp": datetime.now().isoformat(),
            "count": len(alerts),
            "filters": {
                "source": source,
                "severity": severity,
                "hours": hours
            }
        }
    except Exception as e:
        logger.error(f"Error fetching alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sources")
async def get_sources():
    """Get available alert sources."""
    return {
        "sources": ["twitter"],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/severities")
async def get_severities():
    """Get available severity levels."""
    return {
        "severities": ["High", "Medium", "Low"],
        "timestamp": datetime.now().isoformat()
    }

async def broadcast_alerts():
    """Broadcast alerts to all connected clients."""
    while True:
        if active_connections:
            try:
                alerts = await fetch_all_alerts()
                for connection in active_connections:
                    try:
                        await connection.send_json({
                            "type": "alerts",
                            "data": alerts,
                            "timestamp": datetime.now().isoformat()
                        })
                    except Exception as e:
                        logger.error(f"Error sending to client: {str(e)}")
                        active_connections.remove(connection)
            except Exception as e:
                logger.error(f"Error in broadcast: {str(e)}")
        await asyncio.sleep(int(os.getenv('ALERT_REFRESH_INTERVAL', 300)))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time alerts."""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send initial data
        initial_alerts = await fetch_all_alerts()
        await websocket.send_json({
            "type": "initial",
            "data": initial_alerts,
            "timestamp": datetime.now().isoformat()
        })
        
        while True:
            try:
                data = await websocket.receive_text()
                await websocket.send_json({
                    "type": "acknowledgment",
                    "message": "received",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"WebSocket error: {str(e)}")
                break
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)

@app.on_event("startup")
async def startup_event():
    """Start background tasks on application startup."""
    asyncio.create_task(broadcast_alerts())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv('API_HOST', '127.0.0.1'), port=int(os.getenv('API_PORT', 8000))) 