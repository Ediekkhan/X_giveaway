
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
        """Like a tweet"""
        try:
            self.api.create_favorite(tweet.id)
            self.logger.info(f"Liked tweet {tweet.id}")
            return True
        except tweepy.Forbidden:
            self.logger.warning(f"Already liked tweet {tweet.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error liking tweet {tweet.id}: {str(e)}")
            return False
    
    def retweet_tweet(self, tweet):
        """Retweet a tweet"""
        try:
            self.api.retweet(tweet.id)
            self.logger.info(f"Retweeted tweet {tweet.id}")
            return True
        except tweepy.Forbidden:
            self.logger.warning(f"Already retweeted tweet {tweet.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error retweeting tweet {tweet.id}: {str(e)}")
            return False
    
    def reply_to_tweet(self, tweet):
        """Reply to a tweet with tagged users"""
        try:
            # Get random reply template
            template = random.choice(Config.REPLY_TEMPLATES)
            
            # Format the reply
            tags = ' '.join(Config.TAGGED_USERS)
            author = f"@{tweet.user.screen_name}"
            
            reply_text = template.format(tags=tags, author=author)
            
            # Ensure reply doesn't exceed Twitter's character limit
            if len(reply_text) > 280:
                # Use shorter template if needed
                reply_text = f"Participating! {tags} {author}"
            
            # Post reply
            self.api.update_status(
                status=reply_text,
                in_reply_to_status_id=tweet.id,
                auto_populate_reply_metadata=True
            )
            
            self.logger.info(f"Replied to tweet {tweet.id}: {reply_text}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error replying to tweet {tweet.id}: {str(e)}")
            return False
    
    def participate_in_giveaway(self, tweet):
        """Perform all actions to participate in a giveaway"""
        try:
            self.logger.info(f"Participating in giveaway: {tweet.id}")
            
            success_count = 0
            
            # Like the tweet
            if self.like_tweet(tweet):
                success_count += 1
                time.sleep(5)  # Small delay between actions
            
            # Retweet the tweet
            if self.retweet_tweet(tweet):
                success_count += 1
                time.sleep(5)
            
            # Reply to the tweet
            if self.reply_to_tweet(tweet):
                success_count += 1
            
            # Consider participation successful if at least 2/3 actions succeeded
            if success_count >= 2:
                self.logger.info(f"Successfully participated in giveaway {tweet.id}")
                return True
            else:
                self.logger.warning(f"Partial participation in giveaway {tweet.id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error participating in giveaway {tweet.id}: {str(e)}")
            return False
