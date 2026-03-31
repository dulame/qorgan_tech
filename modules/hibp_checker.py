import requests
import hashlib
import time
import config

class HIBPChecker:
    def __init__(self):
        self.api_url = config.HIBP_API_URL
        self.headers = {
            'User-Agent': 'Qorgan-Tech-Bot',
        }
        if config.HIBP_API_KEY:
            self.headers['hibp-api-key'] = config.HIBP_API_KEY

    def check_email_pwned(self, email):
        """
        Check if an email has been pwned using HIBP API.
        Returns a dictionary with breach information.
        """
        try:
            time.sleep(config.HIBP_RATE_LIMIT_DELAY)
            
            url = f"{self.api_url}/breachedaccount"
            params = {
                'account': email,
                'truncateResponse': False
            }
            
            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                breaches = response.json()
                return {
                    'is_pwned': True,
                    'breach_count': len(breaches),
                    'breaches': breaches
                }
            elif response.status_code == 404:
                return {
                    'is_pwned': False,
                    'breach_count': 0,
                    'breaches': []
                }
            elif response.status_code == 429:
                return {
                    'error': 'Rate limited by HIBP API',
                    'is_pwned': None
                }
            else:
                return {
                    'error': f'API returned status code {response.status_code}',
                    'is_pwned': None
                }
        except Exception as e:
            return {
                'error': f'Error checking email: {str(e)}',
                'is_pwned': None
            }

    def format_breach_info(self, email, check_result):
        """Format breach information for display."""
        if 'error' in check_result:
            return f"❌ Error: {check_result['error']}"
        
        if not check_result['is_pwned']:
            return f"✅ Good news! Email '{email}' has not been found in any known breaches."
        
        report = f"⚠️ Email '{email}' was found in {check_result['breach_count']} breach(es):\n\n"
        
        for breach in check_result['breaches']:
            report += f"📌 {breach['Name']}\n"
            report += f"   Date: {breach.get('BreachDate', 'N/A')}\n"
            report += f"   Data: {', '.join(breach.get('DataClasses', []))}\n\n"
        
        return report

    def get_password_hash_prefix(self, password):
        """Get the first 5 characters of SHA1 hash for k-anonymity check."""
        sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
        return sha1[:5]

    def check_password_pwned(self, password):
        """
        Check if a password has been pwned using k-anonymity.
        Returns count of how many times it was found in breaches.
        """
        try:
            prefix = self.get_password_hash_prefix(password)
            url = f"https://api.pwnedpasswords.com/range/{prefix}"
            
            response = requests.get(url, headers={'User-Agent': 'Qorgan-Tech-Bot'})
            
            if response.status_code == 200:
                full_hash = hashlib.sha1(password.encode()).hexdigest().upper()
                suffix = full_hash[5:]
                
                for line in response.text.splitlines():
                    if line.startswith(suffix):
                        count = int(line.split(':')[1])
                        return {
                            'is_pwned': True,
                            'count': count,
                            'message': f'This password has been seen {count} time(s) in data breaches.'
                        }
                
                return {
                    'is_pwned': False,
                    'count': 0,
                    'message': 'This password has not been seen in any known data breaches.'
                }
            else:
                return {
                    'error': f'API returned status code {response.status_code}'
                }
        except Exception as e:
            return {
                'error': f'Error checking password: {str(e)}'
            }
