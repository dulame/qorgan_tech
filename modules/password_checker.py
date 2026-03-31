from zxcvbn import zxcvbn
from modules.password_hasher import PasswordHasher
from modules.database import Database


class PasswordChecker:
    def __init__(self):
        self.db = Database()
    
    @staticmethod
    def check_password_strength(password):
        result = zxcvbn(password)
        
        return {
            'score': result['score'],
            'feedback': result['feedback'],
            'crack_times_seconds': result['crack_times_seconds'],
            'crack_times_display': result['crack_times_display'],
            'sequence': result['sequence'],
            'calc_time': result['calc_time']
        }

    @staticmethod
    def get_strength_text(score):
        strengths = {
            0: '🔴 Very Weak',
            1: '🟠 Weak',
            2: '🟡 Fair',
            3: '🟢 Good',
            4: '🟢 Very Strong'
        }
        return strengths.get(score, 'Unknown')

    @staticmethod
    def format_time_to_crack(seconds):
        if seconds < 1:
            return "less than 1 second"
        elif seconds < 60:
            return f"{int(seconds)} seconds"
        elif seconds < 3600:
            return f"{int(seconds / 60)} minutes"
        elif seconds < 86400:
            return f"{int(seconds / 3600)} hours"
        elif seconds < 2592000:
            return f"{int(seconds / 86400)} days"
        elif seconds < 31536000:
            return f"{int(seconds / 2592000)} months"
        else:
            return f"{int(seconds / 31536000)} years"

    def log_password_check(self, user_id, password):
        """
        Log a password check with hashed password to database.
        
        Args:
            user_id (int): The user ID
            password (str): The password to hash and log
            
        Returns:
            dict: Information about the logged check
        """
        result = self.check_password_strength(password)
        score = result['score']
        strength_text = self.get_strength_text(score).replace('🔴 ', '').replace('🟠 ', '').replace('🟡 ', '').replace('🟢 ', '')
        
        crack_times_seconds = result.get('crack_times_seconds', {})
        offline_seconds = crack_times_seconds.get('offline_fast_hashing_1e10_per_second', 0)
        # Convert Decimal to float if necessary
        offline_seconds = float(offline_seconds) if offline_seconds else 0
        
        crack_times_display = result.get('crack_times_display', {})
        offline_time = crack_times_display.get('offline_fast_hashing_1e10_per_second') or \
                      crack_times_display.get('offlineFastHashing1e10PerSecond') or \
                      'Unknown'
        
        # Hash the password
        hashed = PasswordHasher.hash_password(password)
        
        # Log to database
        self.db.log_password_check(
            user_id=user_id,
            hashed_password=hashed['salted_hash'],
            strength_score=score,
            strength_text=strength_text,
            crack_time_offline=offline_time,
            crack_time_seconds=offline_seconds
        )
        
        return {
            'user_id': user_id,
            'hashed': hashed['salted_hash'],
            'strength_score': score,
            'strength_text': strength_text,
            'crack_time_offline': offline_time
        }

    @staticmethod
    def generate_password_report(password):
        result = PasswordChecker.check_password_strength(password)
        score = result['score']
        
        crack_times = result.get('crack_times_display', {})
        
        online_time = crack_times.get('online_throttled_100_per_hour') or \
                     crack_times.get('onlineThrottled100PerHour') or \
                     'Unknown'
        offline_time = crack_times.get('offline_fast_hashing_1e10_per_second') or \
                      crack_times.get('offlineFastHashing1e10PerSecond') or \
                      'Unknown'
        
        report = f"""
{PasswordChecker.get_strength_text(score)}

⏱️ Time to crack (online guessing): {online_time}
⏱️ Time to crack (offline fast hashing): {offline_time}

📊 Score: {score}/4
"""
        
        if result['feedback']:
            report += "\n💡 Feedback:\n"
            if result['feedback'].get('warning'):
                report += f"- ⚠️ {result['feedback']['warning']}\n"
            if result['feedback'].get('suggestions'):
                for suggestion in result['feedback']['suggestions']:
                    report += f"- {suggestion}\n"
        
        return report
