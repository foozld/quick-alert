from disaster_detector import DisasterDetector
from alert_generator import AlertGenerator, AlertLevel

def test_alert_system():
    """Test the complete alert system with sample data"""
    
    # Initialize components
    detector = DisasterDetector()
    alert_gen = AlertGenerator(confidence_threshold=0.6)
    
    # Sample disaster-related texts
    test_texts = [
        "Major earthquake of magnitude 7.2 hits Los Angeles, causing widespread damage",
        "Severe flooding reported in Miami Beach area, residents evacuating",
        "Category 5 hurricane approaching Florida coast, expected landfall in 12 hours",
        "This is a normal news article about local politics",  # Non-disaster text
        "Wildfire spreading rapidly near San Diego, multiple neighborhoods evacuated"
    ]
    
    # Process texts through detector
    print("Processing texts through disaster detector...")
    detection_results = detector.predict(test_texts)
    
    # Generate alerts
    print("\nGenerating alerts...")
    alerts = alert_gen.generate_alerts(detection_results)
    
    # Print results
    print(f"\nGenerated {len(alerts)} alerts:")
    for alert in alerts:
        print("\n-------------------")
        print(f"Alert Level: {alert['alert_level']}")
        print(f"Disaster Type: {alert['disaster_type']}")
        print(f"Confidence Score: {alert['confidence_score']:.2f}")
        print(f"Locations: {', '.join(loc['name'] for loc in alert['locations'])}")
        print("\nRecommendations:")
        for rec in alert['recommendations']:
            print(f"- {rec}")
    
    # Test location-based filtering
    print("\n\nTesting location-based alerts...")
    la_alerts = alert_gen.get_alerts_by_location(34.0522, -118.2437, radius_km=100)  # Los Angeles
    print(f"Found {len(la_alerts)} alerts near Los Angeles")
    
    # Test alert level filtering
    critical_alerts = alert_gen.get_alerts_by_level(AlertLevel.CRITICAL)
    print(f"Found {len(critical_alerts)} critical alerts")

if __name__ == "__main__":
    test_alert_system() 