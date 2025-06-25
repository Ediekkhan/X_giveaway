
"""
Giveaway Filter Module
Identifies eligible giveaway tweets using regex patterns
"""

import re
import logging

class GiveawayFilter:
    """Filters tweets to identify eligible giveaways"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Inclusion patterns (case-insensitive)
        self.inclusion_patterns = [
            # Follow-related phrases
            r'follow\s+all\s+these\s+accounts',
            r'follow\s+the\s+accounts',
            r'follow\s+all\s+accounts\s+mentioned',
            r'follow\s+our\s+partners',
            r'follow\s+all\s+accounts\s+below',
            r'follow',
            
            # Tagging phrases
            r'tag\s+\d+\s+(?:people|friends|users|accounts)',
            r'tag\s+(?:three|four|five|\d+)\s+(?:people|friends|users|accounts)',
            r'mention\s+\d+\s+(?:people|friends|users|accounts)',
            
            # Timeframe phrases
            r'winners?\s+(?:be\s+)?selected\s+in\s+\d+(?:-\d+)?\s+days?',
            r'winners?\s+selected\s+in\s+\d+\s+days?',
            r'draw\s+in\s+\d+\s+days?',
            r'ends?\s+in\s+\d+\s+days?',
            r'closes?\s+in\s+\d+\s+days?',
            
            # Giveaway keywords
            r'giveaway',
            r'funded',
            r'account',
            r'contest',
            r'prize',
            r'win\s+(?:money|cash|crypto|nft)',
            r'airdrop',
            r'free\s+(?:money|cash|crypto|nft)',
            r'enter\s+to\s+win',
        ]
        
        # Exclusion patterns (case-insensitive)
        self.exclusion_patterns = [
            r'screenshot\s+proof',
            r'add\s+screenshot',
            r'upload\s+screenshot',
            r'screenshot\s+in\s+comments',
            r'dm\s+screenshot',
            r'send\s+screenshot',
            r'post\s+screenshot',
            r'share\s+screenshot',
            r'proof\s+of\s+follow',
            r'screenshot\s+required',
        ]
        
        # Compile patterns for efficiency
        self.inclusion_regex = re.compile(
            '|'.join(self.inclusion_patterns),
            re.IGNORECASE
        )
        
        self.exclusion_regex = re.compile(
            '|'.join(self.exclusion_patterns),
            re.IGNORECASE
        )
    
    def is_giveaway(self, tweet):
        """Check if tweet is an eligible giveaway"""
        try:
            # Get tweet text (handling both API v1.1 and v2)
            text = getattr(tweet, 'full_text', getattr(tweet, 'text', ''))
            
            # Log tweet for debugging
            self.logger.debug(f"Checking tweet {tweet.id}: {text[:100]}...")
            
            # Check inclusion patterns
            if not self.inclusion_regex.search(text):
                self.logger.debug(f"Tweet {tweet.id}: No giveaway keywords found")
                return False
            
            # Check exclusion patterns
            if self.exclusion_regex.search(text):
                self.logger.info(f"Excluded tweet {tweet.id}: Screenshot required")
                return False
            
            self.logger.info(f"Found eligible giveaway: {tweet.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error filtering tweet {tweet.id}: {str(e)}")
            return False
    
    def check_engagement_threshold(self, tweet):
        """Check if tweet engagement is below threshold"""
        try:
            likes = getattr(tweet, 'favorite_count', 0)
            retweets = getattr(tweet, 'retweet_count', 0)
            total_engagement = likes + retweets
            
            if total_engagement > 3000:
                self.logger.info(
                    f"Tweet {tweet.id} exceeds engagement threshold: "
                    f"{likes} likes + {retweets} retweets = {total_engagement}"
                )
                return False
            
            self.logger.debug(
                f"Tweet {tweet.id} engagement OK: "
                f"{likes} likes + {retweets} retweets = {total_engagement}"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking engagement for tweet {tweet.id}: {str(e)}")
            return False
