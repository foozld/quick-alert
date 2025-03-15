from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Set
import asyncio
import json
from datetime import datetime, timedelta

from social_media_collector import SocialMediaCollector
from disaster_detector import DisasterDetector
from alert_generator import AlertGenerator

app = FastAPI(
    title="Quick Alert API",
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

# Initialize components
collector = SocialMediaCollector({})  # Add API keys in production
detector = DisasterDetector()
alert_generator = AlertGenerator()

# Store active WebSocket connections
active_connections: Set[WebSocket] = set()

# Store recent alerts
recent_alerts: List[Dict] = []
MAX_STORED_ALERTS = 100

async def background_alert_check():
    """Background task to check for new alerts"""
    while True:
        try:
            # Collect social media data
            disaster_keywords = [
                'earthquake', 'flood', 'hurricane', 'tornado',
                'wildfire', 'tsunami', 'emergency', 'evacuation'
            ]
            social_data = collector.collect_disaster_data(disaster_keywords)
            
            # Flatten the data
            posts = []
            for platform_data in social_data.values():
                posts.extend(platform_data)
            
            if posts:
                # Get predictions
                predictions = detector.predict([post['text'] for post in posts])
                
                # Generate alerts
                new_alerts = alert_generator.generate_alerts(predictions, posts)
                
                if new_alerts:
                    # Update recent alerts
                    recent_alerts.extend(new_alerts)
                    if len(recent_alerts) > MAX_STORED_ALERTS:
                        recent_alerts[:] = recent_alerts[-MAX_STORED_ALERTS:]
                    
                    # Broadcast to all connected clients
                    for alert in new_alerts:
                        await broadcast_alert(alert)
        
        except Exception as e:
            print(f"Error in background task: {str(e)}")
        
        # Wait before next check
        await asyncio.sleep(60)  # Check every minute

@app.on_event("startup")
async def startup_event():
    """Start background tasks on application startup"""
    background_tasks = BackgroundTasks()
    background_tasks.add_task(background_alert_check)

@app.get("/")
async def read_root():
    """Root endpoint"""
    return {
        "message": "Welcome to Quick Alert API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/alerts")
async def get_alerts(
    limit: int = 10,
    severity: str = None,
    source: str = None
):
    """Get recent alerts with optional filtering"""
    filtered_alerts = recent_alerts
    
    if severity:
        filtered_alerts = [
            alert for alert in filtered_alerts
            if alert['severity'] == severity.upper()
        ]
    
    if source:
        filtered_alerts = [
            alert for alert in filtered_alerts
            if alert['source'] == source.lower()
        ]
    
    return filtered_alerts[-limit:]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time alerts"""
    await websocket.accept()
    active_connections.add(websocket)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def broadcast_alert(alert: Dict):
    """Broadcast alert to all connected clients"""
    dead_connections = set()
    
    for connection in active_connections:
        try:
            await connection.send_json(alert)
        except:
            dead_connections.add(connection)
    
    # Clean up dead connections
    active_connections.difference_update(dead_connections)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 