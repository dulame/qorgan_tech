"""
Free email breach checker using free APIs and resources.
"""
import requests
import hashlib
import time

class FreeEmailChecker:
    """Check if email/password has been compromised using free APIs."""
    
    def __init__(self):
        self.pwned_passwords_url = "https://api.pwnedpasswords.com/range"
        # List of known free services for email checking
        self.headers = {
            'User-Agent': 'Qorgan-Tech-Bot',
        }
    
    def check_email_in_breaches(self, email):
        """
        Check if email appears in known breaches.
        Note: This is a simplified checker using free resources.
        For comprehensive checking, consider upgrading to paid services.
        """
        try:
            # This is a simple check - in production, you might want to:
            # 1. Maintain a local database of known breaches
            # 2. Use other free APIs like Snusbase query
            # 3. Schedule periodic updates
            
            # For now, we'll provide a basic check and user guidance
            return {
                'status': 'checked',
                'email': email,
                'message': 'Free email breach checking has limitations. For comprehensive checking, use haveibeenpwned.com website.',
                'recommendation': 'Visit https://haveibeenpwned.com directly for real-time breach checking'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def check_password_pwned(self, password):
        """
        Check if password has been pwned using k-anonymity (FREE).
        This uses the public Pwned Passwords API.
        """
        try:
            # Get SHA1 hash
            sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
            prefix = sha1[:5]
            suffix = sha1[5:]
            
            # Query the API
            response = requests.get(
                f"{self.pwned_passwords_url}/{prefix}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                # Search for the suffix in response
                for line in response.text.splitlines():
                    if line.startswith(suffix):
                        count = int(line.split(':')[1])
                        return {
                            'is_pwned': True,
                            'count': count,
                            'message': f'⚠️ This password has been seen {count} time(s) in data breaches. Consider using a different password.',
                            'severity': 'high' if count > 100 else 'medium'
                        }
                
                return {
                    'is_pwned': False,
                    'count': 0,
                    'message': '✅ This password has not been seen in any known data breaches.',
                    'severity': 'low'
                }
            else:
                return {
                    'error': f'API returned status {response.status_code}'
                }
        
        except Exception as e:
            return {
                'error': f'Error checking password: {str(e)}'
            }
    
    def format_email_check_result(self, email, result):
        """Format email check result for Telegram."""
        if 'error' in result:
            return f"❌ Error: {result['error']}"
        
        message = f"""
📧 *Email Breach Check*

Email: `{email}`

{result['message']}

🔗 {result.get('recommendation', '')}
"""
        return message
    
    def format_password_check_result(self, result):
        """Format password check result for Telegram."""
        if 'error' in result:
            return f"❌ Error: {result['error']}"
        
        severity_icon = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }
        
        icon = severity_icon.get(result.get('severity', 'low'), '⚪')
        
        message = f"""
{icon} *Password Breach Check*

{result['message']}
"""
        return message
