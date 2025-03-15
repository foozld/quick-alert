from datetime import datetime
from typing import List, Dict, Tuple, Optional
import json
import uuid

class AlertGenerator:
    def __init__(self, threshold: float = 0.75):
        """
        Initialize the alert generator
        
        Args:
            threshold: Probability threshold for generating alerts (0.0 to 1.0)
        """
        self.threshold = threshold
        
    def generate_alerts(
        self,
        predictions: List[Tuple[float, float]],
        social_media_data: List[Dict]
    ) -> List[Dict]:
        """
        Generate alerts based on disaster predictions
        
        Args:
            predictions: List of (non_disaster_prob, disaster_prob) tuples
            social_media_data: List of social media posts with metadata
            
        Returns:
            List of generated alerts
        """
        alerts = []
        
        for i, (_, disaster_prob) in enumerate(predictions):
            if disaster_prob > self.threshold:
                post = social_media_data[i]
                alert = {
                    'id': str(uuid.uuid4()),
                    'probability': float(disaster_prob),
                    'severity': self._calculate_severity(disaster_prob),
                    'source': post['source'],
                    'content': post['text'],
                    'location': self._extract_location(post),
                    'coordinates': post.get('coordinates'),
                    'timestamp': datetime.now().isoformat(),
                    'keywords': self._extract_keywords(post['text'])
                }
                alerts.append(alert)
                
        return alerts
    
    def _calculate_severity(self, probability: float) -> str:
        """Calculate alert severity based on probability"""
        if probability > 0.9:
            return 'CRITICAL'
        elif probability > 0.8:
            return 'HIGH'
        elif probability > 0.7:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _extract_location(self, post: Dict) -> Optional[str]:
        """Extract location information from the post"""
        # First try to get coordinates-based location
        if post.get('coordinates'):
            return f"Lat: {post['coordinates']['lat']}, Long: {post['coordinates']['long']}"
        
        # Fall back to text-based location
        return post.get('location')
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from the alert text"""
        disaster_keywords = {
            'earthquake', 'flood', 'hurricane', 'tornado', 'wildfire',
            'tsunami', 'landslide', 'avalanche', 'volcanic', 'storm',
            'emergency', 'evacuation', 'disaster', 'catastrophe', 'crisis'
        }
        
        words = set(text.lower().split())
        return list(words.intersection(disaster_keywords))
    
    def serialize_alert(self, alert: Dict) -> str:
        """Serialize alert to JSON string"""
        return json.dumps(alert)
    
    def deserialize_alert(self, alert_json: str) -> Dict:
        """Deserialize alert from JSON string"""
        return json.loads(alert_json) 