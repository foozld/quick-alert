import random
from datetime import datetime, timedelta
import json

class SampleDataProvider:
    def __init__(self):
        self.sample_events = [
            {
                "source": "weather",
                "text": "Severe thunderstorm warning for Los Angeles County. Potential for heavy rain, hail, and wind gusts up to 60 mph.",
                "severity": "Severe",
                "location": "Los Angeles County, CA",
                "coordinates": {"lat": 34.0522, "lon": -118.2437},
                "details": {
                    "wind_speed": "45-60 mph",
                    "precipitation": "2-3 inches expected",
                    "duration": "Next 3 hours"
                }
            },
            {
                "source": "twitter",
                "text": "Multiple reports of flooding in downtown Miami. Ocean Drive and Collins Ave underwater. Vehicles stranded. Avoid area!",
                "severity": "Extreme",
                "location": "Miami Beach, FL",
                "coordinates": {"lat": 25.7617, "lon": -80.1918},
                "details": {
                    "affected_areas": ["Ocean Drive", "Collins Avenue", "5th Street"],
                    "reported_by": "Miami PD",
                    "evacuation_status": "Voluntary"
                }
            },
            {
                "source": "reddit",
                "text": "4.2 magnitude earthquake near San Francisco. Felt across Bay Area. BART temporarily suspended.",
                "severity": "Medium",
                "location": "San Francisco Bay Area, CA",
                "coordinates": {"lat": 37.7749, "lon": -122.4194},
                "details": {
                    "magnitude": 4.2,
                    "depth": "8.2 km",
                    "aftershocks": "3 recorded"
                }
            },
            {
                "source": "weather",
                "text": "Winter storm warning: Denver metro area expecting 8-12 inches of snow. Strong winds creating blizzard conditions.",
                "severity": "Severe",
                "location": "Denver Metropolitan Area, CO",
                "coordinates": {"lat": 39.7392, "lon": -104.9903},
                "details": {
                    "snowfall": "8-12 inches",
                    "wind_chill": "-15°F",
                    "visibility": "< 1/4 mile"
                }
            },
            {
                "source": "twitter",
                "text": "Fast-moving wildfire near Phoenix suburbs. Evacuation orders for Cave Creek area. Multiple structures threatened.",
                "severity": "Extreme",
                "location": "Cave Creek, Phoenix, AZ",
                "coordinates": {"lat": 33.4484, "lon": -112.0740},
                "details": {
                    "size": "approximately 500 acres",
                    "containment": "5%",
                    "evacuation_zones": ["Zone A", "Zone B"]
                }
            },
            {
                "source": "weather",
                "text": "Flash flood warning issued for Houston metro area. Street flooding reported in multiple locations.",
                "severity": "Severe",
                "location": "Houston, TX",
                "coordinates": {"lat": 29.7604, "lon": -95.3698},
                "details": {
                    "rainfall_rate": "2 inches per hour",
                    "duration": "Until 9:00 PM CDT",
                    "affected_areas": ["Downtown", "Midtown", "Medical Center"]
                }
            }
        ]

    def get_random_alerts(self, count=3):
        """Get a random selection of alerts with updated timestamps."""
        alerts = random.sample(self.sample_events, min(count, len(self.sample_events)))
        current_time = datetime.now()
        
        for alert in alerts:
            # Add a random timestamp within the last 6 hours for more realism
            random_minutes = random.randint(0, 360)
            alert_time = current_time - timedelta(minutes=random_minutes)
            alert["created_at"] = alert_time.isoformat()
            
            # Add random engagement metrics
            alert["engagement"] = {
                "shares": random.randint(10, 1000),
                "comments": random.randint(5, 500),
                "verified_reports": random.randint(1, 50)
            }
        
        return sorted(alerts, key=lambda x: x["created_at"], reverse=True)

    def get_all_alerts(self, source=None, severity=None, hours=24):
        """
        Get all sample alerts with filtering options.
        
        Args:
            source (str, optional): Filter by source (weather, twitter, reddit)
            severity (str, optional): Filter by severity (Extreme, Severe, Medium)
            hours (int, optional): Get alerts from the last N hours
        """
        current_time = datetime.now()
        alerts = []
        
        for event in self.sample_events:
            alert = event.copy()
            # More realistic time distribution
            random_minutes = random.randint(0, hours * 60)
            alert_time = current_time - timedelta(minutes=random_minutes)
            alert["created_at"] = alert_time.isoformat()
            
            # Add engagement metrics
            alert["engagement"] = {
                "shares": random.randint(10, 1000),
                "comments": random.randint(5, 500),
                "verified_reports": random.randint(1, 50)
            }
            
            # Apply filters
            if source and alert["source"] != source:
                continue
            if severity and alert["severity"] != severity:
                continue
                
            alerts.append(alert)
            
        return sorted(alerts, key=lambda x: x["created_at"], reverse=True) 