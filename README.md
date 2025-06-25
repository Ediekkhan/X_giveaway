
# Twitter Giveaway Participation Bot

An automated Python bot that monitors your Twitter timeline for "profit-based" giveaways and participates by liking, retweeting, and replying with tagged users.

## Features

- **Smart Giveaway Detection**: Uses regex patterns to identify eligible giveaway tweets
- **Engagement Filtering**: Only participates in giveaways with ≤10 combined likes/retweets
- **Rate Limiting**: Respects Twitter API limits with 500 entries/day maximum
- **Natural Replies**: Varies reply messages to avoid spam detection
- **Comprehensive Logging**: Tracks all activities with timestamps
- **Error Handling**: Robust error handling and recovery

## Setup Instructions

### 1. Twitter Developer Account

1. Go to [https://developer.twitter.com](https://developer.twitter.com)
2. Apply for a developer account
3. Create a new project and app
4. Enable "Read + Write" permissions
5. Generate API keys and tokens

### 2. Environment Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Fill in your Twitter API credentials in `.env`:
   ```
   API_KEY=your_actual_api_key
   API_SECRET=your_actual_api_secret
   ACCESS_TOKEN=your_actual_access_token
   ACCESS_TOKEN_SECRET=your_actual_access_token_secret
   BEARER_TOKEN=your_actual_bearer_token
   ```

### 3. Configuration

Edit `config.py` to customize:
- `TAGGED_USERS`: Users to tag in replies
- `REPLY_TEMPLATES`: Vary reply messages
- `MAX_DAILY_ENTRIES`: Daily participation limit
- `MAX_ENGAGEMENT_THRESHOLD`: Engagement filter

### 4. Running the Bot

```bash
python main.py
```

The bot will:
- Monitor your home timeline every 2 minutes
- Identify giveaway tweets using regex patterns
- Participate by liking, retweeting, and replying
- Log all activities to `bot.log`

## Giveaway Detection Criteria

### Included Tweets (must contain at least one):
- Follow phrases: "follow all these accounts", "follow our partners"
- Tagging phrases: "tag 3 people", "mention 5 friends"
- Time phrases: "winners selected in 5 days", "draw in 3 days"
- Keywords: "giveaway", "contest", "prize", "win money", "crypto", "airdrop"

### Excluded Tweets:
- Screenshot requirements: "screenshot proof", "dm screenshot"
- High engagement: >10 combined likes + retweets

## Rate Limiting

- Maximum 500 giveaway entries per day (1,500 total actions)
- 60-second delays between actions
- 2-minute intervals between timeline checks
- Automatic rate limit handling

## File Structure

```
├── main.py              # Main bot entry point
├── auth.py              # Twitter API authentication
├── tweet_monitor.py     # Tweet fetching and monitoring
├── giveaway_filter.py   # Giveaway detection logic
├── bot_actions.py       # Like, retweet, reply actions
├── config.py            # Configuration settings
├── .env                 # API credentials (create from .env.example)
├── .env.example         # Environment template
├── requirements.txt     # Python dependencies
├── since_id.txt         # Last processed tweet ID (auto-generated)
└── bot.log             # Activity logs (auto-generated)
```

## Logging

All activities are logged to `bot.log` and console:
- Tweet processing and filtering
- Successful and failed actions
- API errors and rate limits
- Daily statistics

## Compliance & Ethics

This bot is designed to:
- Respect Twitter's automation rules
- Use natural, varied replies
- Maintain reasonable rate limits
- Be transparent about automation

**Recommendation**: Add a note to your Twitter bio like "I use a bot for giveaways" for transparency.

## Troubleshooting

### Authentication Errors
- Verify API credentials in `.env`
- Ensure "Read + Write" permissions
- Check if tokens are still valid

### No Giveaways Found
- Check if you follow accounts that post giveaways
- Review regex patterns in `giveaway_filter.py`
- Enable debug logging for pattern matching

### Rate Limiting
- The bot handles rate limits automatically
- Check logs for rate limit messages
- Reduce `MAX_DAILY_ENTRIES` if needed

## Customization

### Adding New Detection Patterns
Edit `giveaway_filter.py`:
```python
self.inclusion_patterns.append(r'your_new_pattern')
```

### Changing Reply Templates
Edit `config.py`:
```python
REPLY_TEMPLATES = [
    "Your custom reply {tags} {author}",
    # Add more variations...
]
```

### Adjusting Tagged Users
Edit `config.py`:
```python
TAGGED_USERS = ['@newuser1', '@newuser2', '@newuser3', '@newuser4']
```

## Deployment on Replit

This bot is designed to run continuously on Replit:

1. Upload all files to your Repl
2. Set environment variables in Replit's Secrets tab
3. The bot will run automatically using the existing workflow

## Support

For issues or questions:
1. Check the logs in `bot.log`
2. Review the troubleshooting section
3. Verify your Twitter API setup
4. Test with debug logging enabled

## Disclaimer

Use this bot responsibly and in compliance with Twitter's Terms of Service. The bot is for educational purposes and legitimate giveaway participation only.
