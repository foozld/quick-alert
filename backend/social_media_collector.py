import tweepy
import facebook
import instaloader
from typing import Dict, List
from datetime import datetime, timedelta

class SocialMediaCollector:
    def __init__(self, api_keys: Dict[str, str]):
        self.twitter_api = self._setup_twitter(api_keys.get('twitter'))
        self.facebook_api = self._setup_facebook(api_keys.get('facebook'))
        self.instagram_api = self._setup_instagram()
        
    def _setup_twitter(self, api_keys: Dict[str, str]) -> tweepy.API:
        if not api_keys:
            return None
        auth = tweepy.OAuthHandler(api_keys['consumer_key'], api_keys['consumer_secret'])
        auth.set_access_token(api_keys['access_token'], api_keys['access_token_secret'])
        return tweepy.API(auth)
    
    def _setup_facebook(self, access_token: str) -> facebook.GraphAPI:
        if not access_token:
            return None
        return facebook.GraphAPI(access_token=access_token)
    
    def _setup_instagram(self) -> instaloader.Instaloader:
        return instaloader.Instaloader()
    
    def collect_disaster_data(self, keywords: List[str], time_period: int = 24) -> Dict:
        """
        Collect disaster-related data from social media platforms
        
        Args:
            keywords: List of keywords to search for
            time_period: Time period in hours to look back
            
        Returns:
            Dictionary containing collected data from each platform
        """
        since_time = datetime.now() - timedelta(hours=time_period)
        
        data = {
            'twitter': self._collect_from_twitter(keywords, since_time) if self.twitter_api else [],
            'facebook': self._collect_from_facebook(keywords, since_time) if self.facebook_api else [],
            'instagram': self._collect_from_instagram(keywords, since_time)
        }
        
        return data
    
    def _collect_from_twitter(self, keywords: List[str], since_time: datetime) -> List[Dict]:
        query = ' OR '.join(keywords)
        tweets = []
        
        try:
            for tweet in tweepy.Cursor(self.twitter_api.search_tweets, q=query).items(100):
                if tweet.created_at >= since_time:
                    tweets.append({
                        'source': 'twitter',
                        'text': tweet.text,
                        'created_at': tweet.created_at,
                        'location': tweet.user.location if tweet.user else None,
                        'coordinates': tweet.coordinates
                    })
        except Exception as e:
            print(f"Error collecting Twitter data: {str(e)}")
            
        return tweets
    
    def _collect_from_facebook(self, keywords: List[str], since_time: datetime) -> List[Dict]:
        posts = []
        
        try:
            for keyword in keywords:
                search_results = self.facebook_api.request(
                    f'/search?q={keyword}&type=post&limit=100'
                )
                
                for post in search_results.get('data', []):
                    if datetime.strptime(post.get('created_time'), '%Y-%m-%dT%H:%M:%S+0000') >= since_time:
                        posts.append({
                            'source': 'facebook',
                            'text': post.get('message', ''),
                            'created_at': post.get('created_time'),
                            'location': post.get('place', {}).get('name'),
                            'coordinates': None
                        })
        except Exception as e:
            print(f"Error collecting Facebook data: {str(e)}")
            
        return posts
    
    def _collect_from_instagram(self, keywords: List[str], since_time: datetime) -> List[Dict]:
        posts = []
        
        try:
            for keyword in keywords:
                for post in self.instagram_api.get_hashtag_posts(keyword):
                    if post.date >= since_time:
                        posts.append({
                            'source': 'instagram',
                            'text': post.caption if post.caption else '',
                            'created_at': post.date,
                            'location': post.location if post.location else None,
                            'coordinates': None
                        })
                    if len(posts) >= 100:
                        break
        except Exception as e:
            print(f"Error collecting Instagram data: {str(e)}")
            
        return posts 