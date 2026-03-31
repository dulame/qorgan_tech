# Qorgan Tech Bot 🛡️

A Telegram bot providing daily security recommendations, password strength checking, and email breach detection.

## Features

- 📋 **Daily Recommendations** - Get daily tips on avoiding phishing and suspicious companies
- 🔐 **Password Strength Checker** - Analyze password strength with estimated crack time
- 📧 **Email Breach Detection** - Check if your email has been compromised
- 📰 **Security News** - Daily security news and updates
- ⏰ **Scheduled Messages** - Automatic daily reminders with security recommendations

## Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (get from [@BotFather](https://t.me/botfather))
- Internet connection for API calls

## Installation

1. **Clone or download the project:**
```bash
cd /home/dulo/Documents/qorgan_tech_bot
```

2. **Create a virtual environment (recommended):**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create a .env file:**
```bash
cp .env.example .env
```

5. **Configure your .env file:**
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
DATABASE_PATH=./data/bot.db
TIMEZONE=UTC
```

## Usage

### Starting the Bot

```bash
python3 main.py
```

### Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Initialize the bot and enable daily recommendations |
| `/check_password` | Check password strength |
| `/check_email <email>` | Check if email is in any known breaches |
| `/recommendations` | View today's security recommendations |
| `/help` | Show available commands |

## How It Works

### Password Checker
Uses the `zxcvbn` library to estimate password strength and crack time. Shows:
- Strength score (0-4)
- Time to crack (various attack scenarios)
- Specific feedback for improvement

### Email Breach Detection
Uses free APIs to check if emails appear in known data breaches:
- No API key required
- Pwned Passwords API for password checks (free, k-anonymity model)
- Recommendations for comprehensive email checking

### Daily Recommendations
Scheduled job that sends:
- List of suspicious emails to avoid
- Known malicious companies and their domains
- Security tips and best practices
- Latest security news

## Project Structure

```
qorgan_tech_bot/
├── main.py                 # Main bot entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── .github/
│   └── copilot-instructions.md
├── modules/
│   ├── __init__.py
│   ├── database.py        # SQLite database management
│   ├── password_checker.py # Password strength analysis
│   ├── free_email_checker.py # Free email/password breach detection
│   ├── recommendations.py  # Security recommendations
│   └── news_fetcher.py    # Daily news
└── data/
    └── bot.db            # SQLite database (auto-created)
```

## Configuration

Edit `config.py` to customize:

- `SCHEDULE_HOUR` - Time for daily recommendations (0-23)
- `SCHEDULE_MINUTE` - Minute for daily recommendations (0-59)
- `TIMEZONE` - Timezone for scheduling
- `DATABASE_PATH` - Path to SQLite database

## Security Notes

- ⚠️ **Passwords** are never stored or logged
- 🔒 **Email checks** use anonymous API calls (k-anonymity)
- 🔐 **All data** is stored locally in SQLite
- 🛡️ Use environment variables for sensitive API keys

## Dependencies

- **python-telegram-bot** - Telegram Bot API
- **requests** - HTTP library for API calls
- **zxcvbn** - Password strength estimation
- **pytz** - Timezone handling
- **APScheduler** - Job scheduling
- **python-dotenv** - Environment variable management

## API Integration

### Free APIs Used
- **Pwned Passwords API** - Free, no key required
  - k-anonymity privacy model for password checks
  - Checks if passwords appear in known breaches

## Troubleshooting

### Bot not responding
- Check if bot token is correct in `.env`
- Verify internet connection
- Check `main.py` runs without errors

### Scheduling not working
- Verify timezone in `.env` is correct
- Check APScheduler library is installed
- Review logs for scheduler errors

### HIBP API errors
- This bot no longer uses the HIBP email API
- For comprehensive email breach checking, visit [haveibeenpwned.com](https://haveibeenpwned.com) directly

## Development

To extend the bot:

1. Add new modules in `modules/` directory
2. Import and use in `main.py`
3. Add new handlers with `application.add_handler()`
4. Update database schema in `modules/database.py` as needed

## License

This project is provided as-is for educational purposes.

## Support

For issues or questions, review the code comments and configuration options in `config.py`.
