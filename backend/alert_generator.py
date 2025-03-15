from datetime import datetime
from typing import Dict, List, Optional
import uuid
import json
from enum import Enum

class AlertLevel(str, Enum):
    CRITICAL = "critical"    # Immediate action required
    HIGH = "high"           # Urgent attention needed
    MEDIUM = "medium"       # Monitor closely
    LOW = "low"            # General awareness

class AlertGenerator:
    def __init__(self):
        pass
    
    def generate_alerts(self, predictions, posts):
        """Dummy alert generation method for sample implementation"""
        return []
    
    def _create_alert(self, detection_result: Dict) -> Optional[Dict]:
        """
        Create a structured alert from a detection result
        
        Args:
            detection_result: Single result from disaster detector
            
        Returns:
            Structured alert dictionary or None if alert should not be generated
        """
        # Extract base information
        disaster_prob = detection_result['probabilities']['disaster']
        confidence = detection_result['confidence_score']
        
        # Determine alert level
        base_level = self.severity_levels.get(
            detection_result['severity'],
            AlertLevel.LOW
        )
        
        # Adjust level based on confidence
        alert_level = self._determine_alert_level(
            base_level,
            confidence,
            disaster_prob
        )
        
        # Create alert structure
        alert = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat(),
            'alert_level': alert_level,
            'disaster_type': detection_result['disaster_type'],
            'confidence_score': confidence,
            'probability': disaster_prob,
            'locations': detection_result['locations'],
            'keywords': detection_result['keywords'],
            'entities': detection_result['entities'],
            'recommendations': self._generate_recommendations(
                detection_result['disaster_type'],
                alert_level
            ),
            'status': 'active'
        }
        
        return alert
    
    def _determine_alert_level(self,
                             base_level: AlertLevel,
                             confidence: float,
                             probability: float) -> AlertLevel:
        """
        Determine final alert level based on multiple factors
        
        Args:
            base_level: Initial alert level from severity
            confidence: Overall confidence score
            probability: Raw disaster probability
            
        Returns:
            Final alert level
        """
        if confidence >= self.critical_threshold and probability >= 0.9:
            return AlertLevel.CRITICAL
        elif confidence >= 0.8 and probability >= 0.8:
            return AlertLevel.HIGH
        elif confidence >= 0.7:
            return AlertLevel.MEDIUM
            
        return base_level
    
    def _generate_recommendations(self,
                                disaster_type: str,
                                alert_level: AlertLevel) -> List[str]:
        """
        Generate specific recommendations based on disaster type and alert level
        
        Args:
            disaster_type: Type of disaster detected
            alert_level: Determined alert level
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Basic recommendations by disaster type
        disaster_recommendations = {
            'earthquake': [
                "Drop, Cover, and Hold On",
                "Stay away from windows and exterior walls",
                "If inside, stay inside; if outside, move to open area"
            ],
            'flood': [
                "Move to higher ground immediately",
                "Avoid walking or driving through flood waters",
                "Follow evacuation orders from local authorities"
            ],
            'hurricane': [
                "Board up windows and secure loose outdoor items",
                "Prepare emergency supplies and evacuation plan",
                "Follow local authority evacuation orders"
            ],
            'tornado': [
                "Seek shelter in basement or interior room",
                "Stay away from windows and exterior walls",
                "Keep monitoring local weather updates"
            ],
            'wildfire': [
                "Follow evacuation orders immediately",
                "Prepare emergency supplies",
                "Close all windows and doors"
            ],
            'tsunami': [
                "Move to higher ground immediately",
                "Follow evacuation routes",
                "Stay away from coastal areas"
            ]
        }
        
        # Get basic recommendations for disaster type
        if disaster_type in disaster_recommendations:
            recommendations.extend(disaster_recommendations[disaster_type])
        
        # Add general recommendations based on alert level
        if alert_level == AlertLevel.CRITICAL:
            recommendations.extend([
                "Take immediate action",
                "Follow all emergency instructions",
                "Contact emergency services if in immediate danger"
            ])
        elif alert_level == AlertLevel.HIGH:
            recommendations.extend([
                "Prepare for immediate action",
                "Monitor official communications",
                "Review evacuation plans"
            ])
        
        return recommendations
    
    def get_active_alerts(self) -> List[Dict]:
        """Get all active alerts"""
        return [alert for alert in self.alerts if alert['status'] == 'active']
    
    def get_alert_by_id(self, alert_id: str) -> Optional[Dict]:
        """Get specific alert by ID"""
        for alert in self.alerts:
            if alert['id'] == alert_id:
                return alert
        return None
    
    def update_alert_status(self, alert_id: str, status: str) -> bool:
        """Update the status of an alert"""
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['status'] = status
                return True
        return False
    
    def get_alerts_by_level(self, level: AlertLevel) -> List[Dict]:
        """Get all alerts of a specific level"""
        return [
            alert for alert in self.alerts 
            if alert['alert_level'] == level and alert['status'] == 'active'
        ]
    
    def get_alerts_by_location(self, lat: float, lon: float, radius_km: float = 50) -> List[Dict]:
        """Get alerts within a radius of a location"""
        from geopy.distance import geodesic
        
        nearby_alerts = []
        for alert in self.get_active_alerts():
            for location in alert['locations']:
                distance = geodesic(
                    (lat, lon),
                    (location['lat'], location['lon'])
                ).km
                if distance <= radius_km:
                    nearby_alerts.append(alert)
                    break
        
        return nearby_alerts 