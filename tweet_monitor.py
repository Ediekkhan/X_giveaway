"""
Tweet Monitoring Module
Fetches tweets using Twitter API v2 search and tracks processed tweets.
"""

import tweepy
import logging
import os
from config import Config

class TweetMonitor:
    """Monitors tweets using search queries and tracks processed tweets."""
    
    def __init__(self, api, client): # client is now mandatory
        self.api = api # Keep for potential v1.1 actions if needed elsewhere
        self.client = client # This is the v2 client, crucial for search
        self.logger = logging.getLogger(__name__)
        self.since_id_file = Config.SINCE_ID_FILE
        # Ensure a search query is defined in Config
        if not hasattr(Config, 'SEARCH_QUERY'):
            self.logger.error("Config.SEARCH_QUERY is not defined. Please add a search query to config.py (e.g., 'giveaway OR #contest').")
            raise AttributeError("Config.SEARCH_QUERY is not defined.")

    def get_since_id(self):
        """Read the last processed tweet ID from file"""
        try:
            if os.path.exists(self.since_id_file):
                with open(self.since_id_file, 'r') as f:
                    since_id = f.read().strip()
                    return int(since_id) if since_id else None
        except Exception as e:
            self.logger.error(f"Error reading since_id from {self.since_id_file}: {str(e)}")
        return None

    def save_since_id(self, tweet_id):
        """Save the highest processed tweet ID to file"""
        try:
            with open(self.since_id_file, 'w') as f:
                f.write(str(tweet_id))
        except Exception as e:
            self.logger.error(f"Error saving since_id to {self.since_id_file}: {str(e)}")

    def get_new_tweets(self):
        """
        Fetch new tweets using the Twitter API v2 search endpoint.
        It searches for tweets matching Config.SEARCH_QUERY that are newer than the last processed ID.
        """
        self.logger.debug(f"Attempting to fetch new tweets with query: '{Config.SEARCH_QUERY}'")
        try:
            since_id = self.get_since_id()
            params = {
                "query": Config.SEARCH_QUERY,
                "tweet_fields": ["created_at", "author_id", "public_metrics", "conversation_id"],
                "expansions": ["author_id"], # To get user details in the response
                "max_results": Config.TWEETS_PER_FETCH,
            }

            if since_id:
                params["since_id"] = since_id
                self.logger.debug(f"Fetching tweets since ID: {since_id}")
            else:
                self.logger.debug("No previous since_id found, fetching recent tweets.")

            # Use the v2 client for searching
            response = self.client.search_recent_tweets(**params)
            
            tweet_list = []
            if response.data:
                # tweepy.Client.search_recent_tweets returns a Response object
                # response.data contains the list of Tweet objects
                # response.includes contains expanded objects (like users from author_id)
                tweet_list = response.data
                self.logger.debug(f"Successfully fetched {len(tweet_list)} tweets from search.")

                # If there are included users, you can process them here if needed
                # users_data = {user["id"]: user for user in response.includes.get("users", [])}
                # For example, to attach user data to tweets:
                # for tweet in tweet_list:
                #     tweet.user = users_data.get(tweet.author_id)

                # Update since_id with the highest tweet ID found
                highest_id = max(tweet.id for tweet in tweet_list)
                self.save_since_id(highest_id)
                self.logger.info(f"Updated since_id to {highest_id}")
            else:
                self.logger.info("No new tweets found matching the search query.")
            
            return tweet_list
            
        except tweepy.TweepyException as e:
            # Catch specific Tweepy exceptions for better error handling
            self.logger.error(f"Tweepy error fetching tweets: {e.response.status_code} - {e.response.text}")
            if e.response and e.response.status_code == 403:
                self.logger.error("403 Forbidden: Your API access level might not support this search endpoint or parameters. Please check your X Developer Portal product access.")
            elif e.response and e.response.status_code == 429:
                self.logger.warning("Rate limit hit while fetching tweets. Waiting for next interval.")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error fetching tweets: {str(e)}")
            return []

    def get_tweet_url(self, tweet):
        """Generate tweet URL for logging.
           Assumes tweet object has 'author_id' and 'id' from v2 API.
           Requires fetching username from author_id, or storing it.
           For simplicity, we'll use a placeholder or assume 'user' object is attached.
        """
        # This part might need adjustment if tweet.user is not directly available
        # from the search_recent_tweets response without further processing.
        # If 'expansions': ['author_id'] is used, you can find user info in response.includes['users']
        # For a quick fix, let's assume if it doesn't have user.screen_name, we use a generic placeholder
        if hasattr(tweet, 'user') and hasattr(tweet.user, 'screen_name'):
            return f"https://x.com/{tweet.user.screen_name}/status/{tweet.id}"
        elif hasattr(tweet, 'author_id'):
            # This is less ideal, as it doesn't show the username directly
            # You'd need to map author_id to username using response.includes['users'] in get_new_tweets
            return f"https://x.com/user_id_{tweet.author_id}/status/{tweet.id}"
        else:
            return f"https://x.com/unknown_user/status/{tweet.id}"

