
"""
Twitter API Authentication Module
Handles secure authentication using Tweepy
"""

import tweepy
import logging
from config import Config

class TwitterAuth:
    """Handles Twitter API authentication"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        Config.validate_credentials()
        
        # Set up OAuth 1.0a authentication
        self.auth = tweepy.OAuthHandler(Config.API_KEY, Config.API_SECRET)
        self.auth.set_access_token(Config.ACCESS_TOKEN, Config.ACCESS_TOKEN_SECRET)
        
        # Initialize API clients
        self.api = tweepy.API(
            self.auth,
            wait_on_rate_limit=True,
            retry_count=3,
            retry_delay=5
        )
        
        # Initialize v2 client if bearer token is available
        self.client = None
        if Config.BEARER_TOKEN:
            self.client = tweepy.Client(
                bearer_token=Config.BEARER_TOKEN,
                consumer_key=Config.API_KEY,
                consumer_secret=Config.API_SECRET,
                access_token=Config.ACCESS_TOKEN,
                access_token_secret=Config.ACCESS_TOKEN_SECRET,
                wait_on_rate_limit=True
            )
    
    def get_api(self):
        """Get the Tweepy API v1.1 instance"""
        return self.api
    
    def get_client(self):
        """Get the Tweepy API v2 client instance"""
        return self.client
    
    def test_authentication(self):
        """Test API authentication and return user info"""
        try:
            user = self.api.verify_credentials()
            self.logger.info(f"Authentication successful for @{user.screen_name}")
            return user
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            raise
