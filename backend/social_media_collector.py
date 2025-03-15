import tweepy
import praw
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SocialMediaCollector:
    def __init__(self, api_keys: Dict[str, str]):
        """Initialize API clients"""
        self.twitter_api = self._setup_twitter(api_keys.get('twitter'))
        self.reddit_api = self._setup_reddit(api_keys.get('reddit'))
        self.nws_headers = {
            'User-Agent': '(QuickAlert, contact@quickalert.com)',
            'Accept': 'application/geo+json'
        }
        self.api_keys = api_keys
        
    def _setup_twitter(self, api_keys: Dict[str, str]) -> Optional[tweepy.API]:
        """Set up Twitter API client"""
        if not api_keys:
            logger.warning("No Twitter API keys provided")
            return None
            
        try:
            auth = tweepy.OAuthHandler(
                api_keys['consumer_key'],
                api_keys['consumer_secret']
            )
            auth.set_access_token(
                api_keys['access_token'],
                api_keys['access_token_secret']
            )
            return tweepy.API(auth, wait_on_rate_limit=True)
        except Exception as e:
            logger.error(f"Twitter API setup failed: {str(e)}")
            return None

    def _setup_reddit(self, api_keys: Dict[str, str]) -> Optional[praw.Reddit]:
        """Set up Reddit API client"""
        if not api_keys:
            logger.warning("No Reddit API keys provided")
            return None
            
        try:
            return praw.Reddit(
                client_id=api_keys['client_id'],
                client_secret=api_keys['client_secret'],
                user_agent='QuickAlert/1.0'
            )
        except Exception as e:
            logger.error(f"Reddit API setup failed: {str(e)}")
            return None
    
    def _get_weather_alerts(self) -> List[Dict]:
        """Get active weather alerts from National Weather Service"""
        try:
            response = requests.get(
                'https://api.weather.gov/alerts/active',
                headers=self.nws_headers
            )
            response.raise_for_status()
            
            alerts = []
            data = response.json()
            
            for feature in data.get('features', []):
                props = feature.get('properties', {})
                if props.get('status') == 'Actual' and props.get('severity') in ['Extreme', 'Severe']:
                    alert = {
                        'text': props.get('headline', ''),
                        'description': props.get('description', ''),
                        'created_at': datetime.fromisoformat(props.get('sent', '').replace('Z', '+00:00')),
                        'location': props.get('areaDesc'),
                        'event': props.get('event'),
                        'severity': props.get('severity'),
                        'source': 'weather'
                    }
                    
                    # Extract coordinates if available
                    if feature.get('geometry') and feature['geometry'].get('coordinates'):
                        coords = feature['geometry']['coordinates'][0][0] if isinstance(feature['geometry']['coordinates'][0][0], list) else feature['geometry']['coordinates']
                        alert['coordinates'] = {
                            'lon': coords[0],
                            'lat': coords[1]
                        }
                    
                    alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error collecting weather alerts: {str(e)}")
            return []
    
    def collect_disaster_data(self, keywords: List[str], time_period: int = 24) -> Dict[str, List[Dict]]:
        """
        Collect disaster-related data from Twitter, Reddit, and NWS
        
        Args:
            keywords: List of keywords to search for
            time_period: Time period in hours to look back
            
        Returns:
            Dictionary containing collected data from each source
        """
        since_time = datetime.now() - timedelta(hours=time_period)
        
        # Collect from all sources
        twitter_data = self._collect_from_twitter(keywords, since_time)
        reddit_data = self._collect_from_reddit(keywords, since_time)
        weather_data = self._get_weather_alerts()
        
        return {
            'twitter': twitter_data,
            'reddit': reddit_data,
            'weather': weather_data
        }
    
    def _collect_from_twitter(self, keywords: List[str], since_time: datetime) -> List[Dict]:
        """Collect data from Twitter"""
        if not self.twitter_api:
            return []
            
        tweets = []
        query = ' OR '.join(f'"{keyword}"' for keyword in keywords)
        
        try:
            for tweet in tweepy.Cursor(
                self.twitter_api.search_tweets,
                q=query,
                tweet_mode='extended',
                lang='en'
            ).items(50):  # Limit to 50 most recent tweets
                if tweet.created_at >= since_time:
                    tweet_data = {
                        'text': tweet.full_text,
                        'created_at': tweet.created_at,
                        'location': tweet.user.location if tweet.user.location else None,
                        'source': 'twitter'
                    }
                    
                    if tweet.coordinates:
                        tweet_data['coordinates'] = {
                            'lat': tweet.coordinates['coordinates'][1],
                            'lon': tweet.coordinates['coordinates'][0]
                        }
                    
                    tweets.append(tweet_data)
        except Exception as e:
            logger.error(f"Error collecting Twitter data: {str(e)}")
            
        return tweets

    def _collect_from_reddit(self, keywords: List[str], since_time: datetime) -> List[Dict]:
        """Collect data from Reddit"""
        if not self.reddit_api:
            return []
            
        posts = []
        # Focus on disaster-related subreddits
        subreddits = ['weather', 'naturaldisasters', 'worldnews']
        
        try:
            for subreddit in subreddits:
                sub = self.reddit_api.subreddit(subreddit)
                for keyword in keywords:
                    search_results = sub.search(
                        keyword,
                        time_filter='day',
                        limit=10  # Limit to 10 posts per keyword per subreddit
                    )
                    
                    for post in search_results:
                        created_time = datetime.fromtimestamp(post.created_utc)
                        if created_time >= since_time:
                            posts.append({
                                'text': f"{post.title}\n{post.selftext if hasattr(post, 'selftext') else ''}",
                                'created_at': created_time,
                                'location': None,  # Reddit posts rarely have reliable location info
                                'source': 'reddit',
                                'subreddit': subreddit,
                                'score': post.score
                            })
        except Exception as e:
            logger.error(f"Error collecting Reddit data: {str(e)}")
            
        return posts

    def collect_disaster_data(self, keywords):
        """Dummy collection method for sample implementation"""
        return {
            "twitter": [],
            "reddit": [],
            "weather": []
        } 