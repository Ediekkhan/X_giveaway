"""
Tweet Monitoring Module
Fetches tweets using Twitter API v2 search and tracks processed tweets.
"""

import tweepy
import logging
import os
import datetime # Import datetime module
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
        It searches for tweets matching Config.SEARCH_QUERY within the last 3 days
        and that are newer than the last processed ID.
        """
        self.logger.debug(f"Attempting to fetch new tweets with query: '{Config.SEARCH_QUERY}'")
        try:
            since_id = self.get_since_id()
            
            # Calculate start_time for the last 3 days
            # end_time can be current UTC time, start_time is 3 days before that
            now_utc = datetime.datetime.now(datetime.timezone.utc)
            # three_days_ago = now_utc - datetime.timedelta(days=3)

            # --- FIX STARTS HERE ---
            # Subtract a buffer (e.g., 15 seconds) from the current time for end_time
            # This ensures it's always in the past relative to the API request.
            buffered_now_utc = now_utc - datetime.timedelta(seconds=15)
            # --- FIX ENDS HERE ---

            three_days_ago = buffered_now_utc - datetime.timedelta(days=3) # Base start_time on buffered_now_utc



            # Format to ISO 8601 string (YYYY-MM-DDTHH:mm:ssZ)
            start_time_iso = three_days_ago.isoformat(timespec='seconds').replace('+00:00', 'Z')
            end_time_iso = now_utc.isoformat(timespec='seconds').replace('+00:00', 'Z')

            self.logger.debug(f"Searching tweets from {start_time_iso} to {end_time_iso}")

            params = {
                "query": Config.SEARCH_QUERY,
                "tweet_fields": ["created_at", "author_id", "public_metrics", "conversation_id"],
                "expansions": ["author_id"], # To get user details in the response
                "max_results": Config.TWEETS_PER_FETCH,
                "start_time": start_time_iso, # Set the start time
                "end_time": end_time_iso      # Set the end time
            }

            if since_id:
                # If since_id is present, it takes precedence over start_time for filtering
                # to ensure only truly *new* tweets are fetched.
                # The API will return tweets newer than since_id, but still within start_time/end_time.
                params["since_id"] = since_id
                self.logger.debug(f"Fetching tweets since ID: {since_id} (within 3-day window)")
            else:
                self.logger.debug("No previous since_id found, fetching recent tweets (last 3 days).")

            # Use the v2 client for searching
            response = self.client.search_recent_tweets(**params)
            
            tweet_list = []
            if response.data:
                tweet_list = response.data
                self.logger.debug(f"Successfully fetched {len(tweet_list)} tweets from search.")

                # It's good practice to ensure tweet objects have the user property for later use
                # You can attach the user data from expansions if needed
                if response.includes and 'users' in response.includes:
                    users_data = {user["id"]: user for user in response.includes["users"]}
                    for tweet in tweet_list:
                        # Attach the user object to the tweet for easy access
                        tweet.user = users_data.get(tweet.author_id)


                # Update since_id with the highest tweet ID found
                highest_id = max(tweet.id for tweet in tweet_list)
                self.save_since_id(highest_id)
                self.logger.info(f"Updated since_id to {highest_id}")
            else:
                self.logger.info("No new tweets found matching the search query within the last 3 days.")
            
            return tweet_list
            
        except tweepy.TweepyException as e:
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
        """
        Generate tweet URL for logging.
        Attempts to use screen_name from tweet.user if available (due to 'expansions').
        """
        if hasattr(tweet, 'user') and hasattr(tweet.user, 'username'): # v2 tweet objects have .username
            return f"https://x.com/{tweet.user.username}/status/{tweet.id}"
        elif hasattr(tweet, 'author_id'):
            # Fallback if user object isn't directly available (less common with expansions)
            return f"https://x.com/user_id_{tweet.author_id}/status/{tweet.id}"
        else:
            return f"https://x.com/unknown_user/status/{tweet.id}"

