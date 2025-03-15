import os
from dotenv import load_dotenv
from social_media_collector import SocialMediaCollector
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_social_media_collection():
    """Test the social media collection system"""
    
    # Get API keys from environment variables
    api_keys = {
        'twitter': {
            'consumer_key': os.getenv('TWITTER_API_KEY'),
            'consumer_secret': os.getenv('TWITTER_API_SECRET'),
            'access_token': os.getenv('TWITTER_ACCESS_TOKEN'),
            'access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        },
        'reddit': {
            'client_id': os.getenv('REDDIT_CLIENT_ID'),
            'client_secret': os.getenv('REDDIT_CLIENT_SECRET'),
            'user_agent': 'QuickAlert/1.0'
        }
    }
    
    # Initialize collector
    collector = SocialMediaCollector(api_keys)
    
    # Test keywords for disasters
    disaster_keywords = [
        'earthquake',
        'flood warning',
        'hurricane alert',
        'wildfire',
        'tornado warning'
    ]
    
    # Collect data from the last 24 hours
    logger.info("Starting data collection...")
    data = collector.collect_disaster_data(
        keywords=disaster_keywords,
        time_period=24
    )
    
    # Print results for each platform
    for platform, posts in data.items():
        logger.info(f"\n{platform.upper()} Results:")
        logger.info(f"Collected {len(posts)} posts/alerts")
        
        if posts:
            # Show sample post
            sample = posts[0]
            logger.info("\nSample Post/Alert:")
            logger.info(f"Text: {sample['text'][:200]}...")
            logger.info(f"Created at: {sample['created_at']}")
            logger.info(f"URL: {sample['url']}")
            
            if sample['location']:
                logger.info(f"Location: {sample['location']}")
            if sample.get('coordinates'):
                logger.info(f"Coordinates: {sample['coordinates']}")
                
            # Platform-specific details
            if platform == 'reddit':
                logger.info(f"Subreddit: {sample['subreddit']}")
                logger.info(f"Score: {sample['score']}")
            elif platform == 'weather':
                logger.info(f"Event: {sample['event']}")
                logger.info(f"Severity: {sample['severity']}")
                logger.info(f"Certainty: {sample['certainty']}")
                if sample.get('ends_at'):
                    logger.info(f"Ends at: {sample['ends_at']}")

def main():
    try:
        test_social_media_collection()
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 