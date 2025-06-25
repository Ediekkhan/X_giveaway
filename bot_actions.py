"""
Bot Actions Module
Handles liking, retweeting, and replying to giveaway tweets
"""

import tweepy
import logging
import random
import time
from config import Config

class BotActions:
    """Handles automated actions for giveaway participation"""
    
    def __init__(self, api, client=None):
        self.api = api
        self.client = client
        self.logger = logging.getLogger(__name__)
    
    def like_tweet(self, tweet):
        """
        Like a tweet.
        Returns:
            0: Liked successfully.
            1: Already liked.
            2: Error liking.
        """
        try:
            # Use tweepy.API for v1.1 favorite endpoint
            self.api.create_favorite(tweet.id)
            self.logger.info(f"Liked tweet {tweet.id}")
            return 0 # Success
        except tweepy.Forbidden:
            # This typically means the tweet has already been liked by the authenticated user.
            self.logger.warning(f"Already liked tweet {tweet.id}")
            return 1 # Already liked
        except tweepy.TweepyException as e:
            # Catch Tweepy-specific exceptions for better error handling
            self.logger.error(f"Tweepy error liking tweet {tweet.id}: {e.response.status_code} - {e.response.text}")
            return 2 # Other error
        except Exception as e:
            self.logger.error(f"Unexpected error liking tweet {tweet.id}: {str(e)}")
            return 2 # Other error
    
    def retweet_tweet(self, tweet):
        """
        Retweet a tweet.
        Returns:
            0: Retweeted successfully.
            1: Already retweeted.
            2: Error retweeting.
        """
        try:
            # Use tweepy.API for v1.1 retweet endpoint
            self.api.retweet(tweet.id)
            self.logger.info(f"Retweeted tweet {tweet.id}")
            return 0 # Success
        except tweepy.Forbidden:
            # This typically means the tweet has already been retweeted by the authenticated user.
            self.logger.warning(f"Already retweeted tweet {tweet.id}")
            return 1 # Already retweeted
        except tweepy.TweepyException as e:
            self.logger.error(f"Tweepy error retweeting tweet {tweet.id}: {e.response.status_code} - {e.response.text}")
            return 2 # Other error
        except Exception as e:
            self.logger.error(f"Unexpected error retweeting tweet {tweet.id}: {str(e)}")
            return 2 # Other error
    
    def reply_to_tweet(self, tweet):
        """
        Reply to a tweet with tagged users.
        Returns:
            0: Replied successfully.
            2: Error replying. (No "already replied" status as multiple replies are possible)
        """
        try:
            # Ensure REPLY_TEMPLATES and TAGGED_USERS are defined in Config
            if not hasattr(Config, 'REPLY_TEMPLATES') or not Config.REPLY_TEMPLATES:
                self.logger.error("Config.REPLY_TEMPLATES is not defined or empty. Cannot reply.")
                return 2

            if not hasattr(Config, 'TAGGED_USERS') or not Config.TAGGED_USERS:
                self.logger.warning("Config.TAGGED_USERS is not defined or empty. Reply might not tag anyone.")
                tags = ""
            else:
                tags = ' '.join(Config.TAGGED_USERS)

            # Get random reply template
            template = random.choice(Config.REPLY_TEMPLATES)
            
            # Use tweet.author.username for v1.1, or retrieve from expansions if using v2 tweet object
            # Assuming tweet.user.screen_name is available or populated from TweetMonitor
            author_screen_name = ""
            if hasattr(tweet, 'user') and hasattr(tweet.user, 'screen_name'):
                author_screen_name = tweet.user.screen_name
            elif hasattr(tweet, 'author_id') and self.client:
                # If tweet is a v2 object and only has author_id, try to fetch user info
                # This is an example, typically you'd expand users in TweetMonitor
                try:
                    user_response = self.client.get_user(id=tweet.author_id)
                    if user_response.data:
                        author_screen_name = user_response.data.username
                except tweepy.TweepyException as ue:
                    self.logger.warning(f"Could not get user details for {tweet.author_id} for reply: {ue}")
            
            author_tag = f"@{author_screen_name}" if author_screen_name else ""
            
            reply_text = template.format(tags=tags, author=author_tag)
            
            # Ensure reply doesn't exceed Twitter's character limit (280 for tweets/replies)
            if len(reply_text) > 280:
                self.logger.warning(f"Reply text too long ({len(reply_text)} chars), truncating.")
                # A simpler fallback for truncation, ensure it's still meaningful
                reply_text = f"Participating! {tags} {author_tag}"[:280] # Truncate to max chars
                if len(reply_text) == 280: # Ensure it doesn't end mid-word or tag
                    reply_text = reply_text.rsplit(' ', 1)[0] + '...' # Add ellipsis

            # Post reply using Tweepy's API (v1.1 endpoint for update_status)
            self.api.update_status(
                status=reply_text,
                in_reply_to_status_id=tweet.id,
                auto_populate_reply_metadata=True
            )
            
            self.logger.info(f"Replied to tweet {tweet.id}: '{reply_text}'")
            return 0 # Success
            
        except tweepy.TweepyException as e:
            self.logger.error(f"Tweepy error replying to tweet {tweet.id}: {e.response.status_code} - {e.response.text}")
            return 2 # Error
        except Exception as e:
            self.logger.error(f"Unexpected error replying to tweet {tweet.id}: {str(e)}")
            return 2 # Error
    
    def participate_in_giveaway(self, tweet):
        """
        Perform all actions to participate in a giveaway.
        If a tweet is already liked, it skips retweet and comment.
        Returns True if participation is considered complete (at least one action succeeded or already done),
        False otherwise.
        """
        self.logger.info(f"Attempting to participate in giveaway: {tweet.id}")
        
        # 1. Like the tweet
        like_status = self.like_tweet(tweet)
        if like_status == 1: # Already liked
            self.logger.info(f"Tweet {tweet.id} was already liked. Skipping retweet and reply.")
            return True # Consider participation complete for this run
        elif like_status == 2: # Error liking
            self.logger.warning(f"Failed to like tweet {tweet.id}. Attempting other actions.")
            # Do not return False immediately, try other actions
        
        # Small delay between actions
        time.sleep(Config.ACTION_DELAY)
        
        # 2. Retweet the tweet
        retweet_status = self.retweet_tweet(tweet)
        if retweet_status == 2: # Error retweeting
            self.logger.warning(f"Failed to retweet tweet {tweet.id}. Attempting reply.")
            # Do not return False immediately, try other actions
        
        # Small delay between actions
        time.sleep(Config.ACTION_DELAY)
        
        # 3. Reply to the tweet
        reply_status = self.reply_to_tweet(tweet)
        if reply_status == 2: # Error replying
            self.logger.warning(f"Failed to reply to tweet {tweet.id}.")

        # Determine overall success
        # Participation is considered successful if:
        # - It was already liked (like_status == 1)
        # - Liking succeeded (like_status == 0)
        # - Retweeting succeeded (retweet_status == 0)
        # - Replying succeeded (reply_status == 0)
        # Note: If it was already liked, we return True early, so this final check
        # only applies if we proceeded past the initial "already liked" check.
        
        if like_status == 0 or retweet_status == 0 or reply_status == 0:
            self.logger.info(f"Successfully performed actions for giveaway {tweet.id}.")
            return True
        else:
            self.logger.warning(f"No actions could be successfully performed for giveaway {tweet.id}.")
            return False