#!/usr/bin/env python3

import logging
import config
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError

from modules.database import Database
from modules.password_checker import PasswordChecker
from modules.recommendations import RecommendationsGenerator
from modules.news_fetcher import NewsFetcher

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

db = Database()
password_checker = PasswordChecker()  # ⭐ Initialize for logging
scheduler = BackgroundScheduler()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    db.add_user(user_id, user.username, user.first_name, user.last_name)
    
    keyboard = [
        [KeyboardButton("🔐 Check Password")],
        [KeyboardButton("📰 Security Vulnerabilities")],
        [KeyboardButton("ℹ️ About Us")],
        [KeyboardButton("❓ Help")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_message = """🛡️ *Welcome to Qorgan Tech Security Bot* 🛡️

Developed by: Qorgan Tech SLC Team
For: NUFYP SLC Challenge 6

This bot is designed to help you understand cybersecurity risks and vulnerabilities. We provide real-time security vulnerability information and password strength analysis to help protect your digital assets.

*Features:*
• Real-time CVE (Common Vulnerabilities & Exposures) data
• Password strength analysis
• Security awareness education
• Risk assessment information

Use the buttons below to get started and protect yourself!"""
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown', reply_markup=reply_markup)
    logger.info(f"New user started: {user_id}")


async def help_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """*🛡️ Qorgan Tech Bot - Security Assistant*

*Available Features:*

🔐 **Check Password** - Analyze password strength and vulnerability to brute-force attacks

📰 **Security Vulnerabilities** - View latest CVE (Common Vulnerabilities & Exposures) from official sources

ℹ️ **About Us** - Learn about Qorgan Tech and our mission

All your data is processed locally and never stored. Your privacy is protected."""
    
    keyboard = [
        [KeyboardButton("🔐 Check Password")],
        [KeyboardButton("📰 Security Vulnerabilities")],
        [KeyboardButton("ℹ️ About Us")],
        [KeyboardButton("❓ Help")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)


async def about_us_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = """🛡️ About Qorgan Tech Security Initiative

PROJECT DETAILS
Qorgan Tech Security Awareness Bot

CHALLENGE: NUFYP SLC Challenge 6
DEVELOPED BY: Qorgan Tech SLC Team
PURPOSE: Cybersecurity Education & Risk Awareness

OUR MISSION
We are committed to raising awareness about cybersecurity risks and vulnerabilities. This bot demonstrates the importance of security in the digital world and helps users understand potential threats.

WHY THIS PROJECT
• Educate users about real security vulnerabilities
• Promote password security best practices
• Stay updated on CVEs and emerging threats
• Encourage proactive security measures

CONNECT WITH US
Instagram: https://www.instagram.com/qorgan_tech.slc/

Stay secure, stay informed. 🛡️"""
    
    keyboard = [
        [KeyboardButton("🔐 Check Password")],
        [KeyboardButton("📰 Security Vulnerabilities")],
        [KeyboardButton("ℹ️ About Us")],
        [KeyboardButton("❓ Help")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(about_text, reply_markup=reply_markup)


async def password_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Password check initiated by user {update.effective_user.id}")
    try:
        await update.message.reply_text("🔐 Send me a password to check (use a test password, never your real one):", reply_markup=ReplyKeyboardRemove())
        context.user_data['awaiting_password_check'] = True
        logger.info(f"Waiting for password from user {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Error in password_button: {e}")
        try:
            await update.message.reply_text("❌ An error occurred. Please try again.")
        except:
            pass


async def news_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("📡 Fetching latest security vulnerabilities...", reply_markup=ReplyKeyboardRemove())
        news = NewsFetcher.get_daily_news()
        news_message = NewsFetcher.format_news_message(news)
        
        keyboard = [
            [KeyboardButton("🔐 Check Password")],
            [KeyboardButton("📰 Security Vulnerabilities")],
            [KeyboardButton("ℹ️ About Us")],
            [KeyboardButton("❓ Help")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(news_message, parse_mode='Markdown', reply_markup=reply_markup)
        logger.info(f"User {update.effective_user.id} viewed news")
    except Exception as e:
        logger.error(f"Error in news_button: {e}")
        keyboard = [
            [KeyboardButton("🔐 Check Password")],
            [KeyboardButton("📰 Security Vulnerabilities")],
            [KeyboardButton("ℹ️ About Us")],
            [KeyboardButton("❓ Help")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("❌ Error fetching vulnerabilities. Please try again.", reply_markup=reply_markup)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        text = update.message.text
        logger.info(f"Message from {user_id}: {text[:50]}...")
        
        if text == "🔐 Check Password":
            await password_button(update, context)
            return
        
        if text == "📰 Security Vulnerabilities":
            await news_button(update, context)
            return
        
        if text == "ℹ️ About Us":
            await about_us_button(update, context)
            return
        
        if text == "❓ Help":
            await help_button(update, context)
            return
        
        if context.user_data.get('awaiting_password_check'):
            logger.info(f"Processing password check for user {user_id}")
            context.user_data['awaiting_password_check'] = False
            
            try:
                checking_msg = await update.message.reply_text("🔐 Analyzing password strength...")
                
                # ⭐ Log the password check to database
                log_result = password_checker.log_password_check(user_id, text)
                logger.info(f"Password logged for user {user_id}: {log_result['strength_text']}")
                
                report = PasswordChecker.generate_password_report(text)
                
                keyboard = [
                    [KeyboardButton("🔐 Check Password")],
                    [KeyboardButton("📰 Security Vulnerabilities")],
                    [KeyboardButton("ℹ️ About Us")],
                    [KeyboardButton("❓ Help")]
                ]
                reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
                
                try:
                    await checking_msg.edit_text(report, parse_mode='Markdown')
                    await update.message.reply_text("✅ Result above. What would you like to do next?", reply_markup=reply_markup)
                except TelegramError:
                    await update.message.reply_text(report, parse_mode='Markdown', reply_markup=reply_markup)
            except Exception as e:
                logger.error(f"Error checking password: {e}")
                keyboard = [
                    [KeyboardButton("🔐 Check Password")],
                    [KeyboardButton("📰 Security Vulnerabilities")],
                    [KeyboardButton("ℹ️ About Us")],
                    [KeyboardButton("❓ Help")]
                ]
                reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
                await update.message.reply_text(f"❌ Error analyzing password: {str(e)}", reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in handle_message: {e}")


async def send_daily_recommendations(application: Application):
    try:
        active_users = db.get_all_active_users()
        logger.info(f"Sending daily update to {len(active_users)} users")
        
        news = NewsFetcher.get_daily_news(count=3)
        news_message = NewsFetcher.format_news_message(news)
        
        header = "🛡️ *Daily Security Update from Qorgan Tech*\n\n"
        
        full_message = f"{header}{news_message}"
        
        for user_id in active_users:
            try:
                await application.bot.send_message(
                    chat_id=user_id,
                    text=full_message,
                    parse_mode='Markdown'
                )
            except TelegramError as e:
                logger.warning(f"Failed to send message to {user_id}: {e}")
    
    except Exception as e:
        logger.error(f"Error in send_daily_recommendations: {e}")


def schedule_daily_job(application: Application):
    try:
        tz = pytz.timezone(config.TIMEZONE)
        
        scheduler.add_job(
            send_daily_recommendations,
            'cron',
            hour=config.SCHEDULE_HOUR,
            minute=config.SCHEDULE_MINUTE,
            timezone=tz,
            args=[application],
            id='daily_recommendations',
            replace_existing=True
        )
        
        if not scheduler.running:
            scheduler.start()
            logger.info(f"Scheduler started - daily job at {config.SCHEDULE_HOUR}:{config.SCHEDULE_MINUTE:02d} {config.TIMEZONE}")
    except Exception as e:
        logger.error(f"Error scheduling daily job: {e}")


def main():
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    
    async def error_handler(update, context):
        logger.error(f"Exception while handling an update: {context.error}")
    
    application.add_error_handler(error_handler)
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    async def post_init_scheduler(app):
        schedule_daily_job(app)
    
    application.post_init = post_init_scheduler
    
    logger.info("Starting Qorgan Tech Bot...")
    application.run_polling()


if __name__ == '__main__':
    main()
