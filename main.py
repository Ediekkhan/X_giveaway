
"""
Twitter Giveaway Participation Bot
Main entry point for the bot that coordinates all components
"""

import logging
import time
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from auth import TwitterAuth
from tweet_monitor import TweetMonitor
from giveaway_filter import GiveawayFilter
from bot_actions import BotActions
from config import Config

def setup_logging():
    """Configure logging with timestamps and file output"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def main():
    """Main bot loop"""
    # Load environment variables from .env file
    load_dotenv()
    
    logger = setup_logging()
    logger.info("Starting Twitter Giveaway Bot")
    
    try:
        # Initialize components
        auth = TwitterAuth()
        api = auth.get_api()
        client = auth.get_client()
        
        monitor = TweetMonitor(api, client)
        giveaway_filter = GiveawayFilter()
        bot_actions = BotActions(api, client)
        
        # Verify authentication
        user = api.verify_credentials()
        logger.info(f"Authenticated as: @{user.screen_name}")
        
        # Track daily actions
        daily_actions = 0
        last_reset = datetime.now().date()
        
        logger.info("Bot started - monitoring for giveaways...")
        
        while True:
            try:
                # Reset daily counter at midnight
                if datetime.now().date() > last_reset:
                    daily_actions = 0
                    last_reset = datetime.now().date()
                    logger.info("Daily action counter reset")
                
                # Check if we've reached daily limit
                if daily_actions >= Config.MAX_DAILY_ENTRIES:
                    sleep_until_midnight = (datetime.now().replace(hour=23, minute=59, second=59) - datetime.now()).total_seconds() + 60
                    logger.info(f"Daily limit reached ({daily_actions}). Sleeping until midnight...")
                    time.sleep(sleep_until_midnight)
                    continue
                
                # Fetch new tweets
                tweets = monitor.get_new_tweets()
                logger.info(f"Fetched {len(tweets)} new tweets")
                
                for tweet in tweets:
                    try:
                        # Filter for giveaways
                        if not giveaway_filter.is_giveaway(tweet):
                            continue
                        
                        # Check engagement threshold
                        if not giveaway_filter.check_engagement_threshold(tweet):
                            logger.info(f"Skipped tweet {tweet.id}: Too much engagement")
                            continue
                        
                        # Perform actions
                        if bot_actions.participate_in_giveaway(tweet):
                            daily_actions += 1
                            logger.info(f"Participated in giveaway {tweet.id}. Daily count: {daily_actions}")
                            
                            # Add delay between actions
                            time.sleep(Config.ACTION_DELAY)
                            
                            if daily_actions >= Config.MAX_DAILY_ENTRIES:
                                break
                    
                    except Exception as e:
                        logger.error(f"Error processing tweet {tweet.id}: {str(e)}")
                        continue
                
                # Wait before next tweet fetch
                logger.info(f"Sleeping for {Config.FETCH_INTERVAL} seconds...")
                time.sleep(Config.FETCH_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                time.sleep(60)  # Wait before retrying
                
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        logger.info("Bot shutting down due to fatal error")

if __name__ == "__main__":
    main()
