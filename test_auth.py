
"""
Test script to verify Twitter API authentication
Run this before starting the main bot to ensure everything is set up correctly
"""

import os
from dotenv import load_dotenv
from auth import TwitterAuth
import logging

def test_authentication():
    """Test Twitter API authentication"""
    # Load environment variables
    load_dotenv()
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Test authentication
        auth = TwitterAuth()
        user = auth.test_authentication()
        
        print(f"✅ Authentication successful!")
        print(f"   Username: @{user.screen_name}")
        print(f"   Display Name: {user.name}")
        print(f"   Followers: {user.followers_count}")
        print(f"   Following: {user.friends_count}")
        
        # Test API calls
        api = auth.get_api()
        
        # Test home timeline access
        tweets = list(api.home_timeline(count=5))
        print(f"✅ Home timeline access successful! Found {len(tweets)} recent tweets")
        
        print("\n🎉 All tests passed! Your bot is ready to run.")
        print("📝 Run 'python main.py' to start the bot")
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication failed: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your .env file has all required credentials")
        print("2. Verify credentials are correct on developer.twitter.com")
        print("3. Ensure your app has 'Read + Write' permissions")
        return False

if __name__ == "__main__":
    test_authentication()
