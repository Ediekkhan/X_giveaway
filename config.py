
"""
Configuration settings for the Twitter Giveaway Bot
"""

import os

class Config:
    """Configuration class containing all bot settings"""
    
    # API Credentials (loaded from environment variables)
    API_KEY = os.getenv('API_KEY')
    API_SECRET = os.getenv('API_SECRET')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
    BEARER_TOKEN = os.getenv('BEARER_TOKEN')
    
    # Bot behavior settings
    MAX_DAILY_ENTRIES = 250  # Maximum giveaway entries per day
    MAX_ENGAGEMENT_THRESHOLD = 2000  # Max combined likes + retweets
    ACTION_DELAY = 10  # Seconds between actions (like, retweet, reply)
    FETCH_INTERVAL = 3600  # Seconds between tweet fetches
    # FETCH_INTERVAL = 14400  # Seconds between tweet fetches
    
    SEARCH_QUERY = "giveaway OR trading OR props OR instant funded account" 

    # Tweet fetching settings
    TWEETS_PER_FETCH = 10  # Number of tweets to fetch per API call
    SINCE_ID_FILE = 'since_id.txt'  # File to store last processed tweet ID
    
    # Tagged users for replies (customize these)
    TAGGED_USERS = ["@50_pips_trader", "@s_ha_kur_", "@kelvinious15048", "@g_uncho"]
    
    # Reply variations for natural responses
    REPLY_TEMPLATES = [
        "Participating! Good luck everyone {tags} {author}",
        "Count me in! {tags} {author}",
        "Excited to join this giveaway! {tags} {author}",
        "Thanks for the opportunity! {tags} {author}",
        "Hope I win! Good luck to all {tags} {author}"
    ]
    
    @classmethod
    def validate_credentials(cls):
        """Validate that all required credentials are present"""
        required = [cls.API_KEY, cls.API_SECRET, cls.ACCESS_TOKEN, cls.ACCESS_TOKEN_SECRET]
        missing = [name for name, value in zip(
            ['API_KEY', 'API_SECRET', 'ACCESS_TOKEN', 'ACCESS_TOKEN_SECRET'],
            required
        ) if not value]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
