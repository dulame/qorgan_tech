import random

SUSPICIOUS_EMAILS = [
    'noreply@phishing-site.com',
    'support@fake-bank.com',
    'verify-account@amazon-verify.com',
    'admin@suspicious-domain.net',
]

SUSPICIOUS_COMPANIES = [
    {
        'name': 'Fake Bank Corp',
        'domains': ['fakebank.com', 'fakebank.net', 'fake-bank.io'],
        'reason': 'Impersonating legitimate banking institutions'
    },
    {
        'name': 'Phishing Services LLC',
        'domains': ['phishing-attempts.com', 'spear-phish.net'],
        'reason': 'Known phishing service provider'
    },
]

NEWS_TOPICS = [
    'Password best practices',
    'Two-factor authentication benefits',
    'How to recognize phishing attempts',
    'Data breach awareness',
    'Email security tips',
    'Password manager recommendations',
    'Social engineering prevention',
    'Malware protection essentials',
]


class RecommendationsGenerator:
    @staticmethod
    def get_daily_recommendations():
        return {
            'suspicious_emails': SUSPICIOUS_EMAILS,
            'suspicious_companies': SUSPICIOUS_COMPANIES,
            'security_tips': RecommendationsGenerator.get_security_tip(),
        }

    @staticmethod
    def get_security_tip():
        tips = [
            "🛡️ Enable two-factor authentication on all important accounts",
            "🔐 Use unique passwords for each service and store them in a password manager",
            "⚠️ Be cautious of emails requesting personal information or urgent action",
            "🔄 Update your software and operating system regularly",
            "📧 Never share your password or recovery codes via email or chat",
            "🔍 Check the sender's email address carefully - it might look similar to legitimate ones",
            "🚫 Avoid public WiFi for sensitive transactions",
            "📱 Use recovery phone numbers and backup email addresses",
        ]
        return random.choice(tips)

    @staticmethod
    def format_recommendations_message(recommendations):
        message = "📋 *Today's Security Recommendations*\n\n"
        
        message += "⚠️ *Avoid These Emails:*\n"
        for email in recommendations['suspicious_emails'][:5]:
            message += f"• {email}\n"
        
        message += "\n🚫 *Suspicious Companies:*\n"
        for company in recommendations['suspicious_companies']:
            domains = ', '.join(company['domains'])
            message += f"• {company['name']}\n  Domains: {domains}\n  Reason: {company['reason']}\n"
        
        message += f"\n💡 *Security Tip:*\n{recommendations['security_tips']}"
        
        return message

    @staticmethod
    def add_custom_recommendation(user_data, rec_type, value):
        if rec_type == 'email':
            if value not in user_data.get('custom_emails', []):
                user_data.setdefault('custom_emails', []).append(value)
        elif rec_type == 'company':
            if value not in user_data.get('custom_companies', []):
                user_data.setdefault('custom_companies', []).append(value)
        return user_data
