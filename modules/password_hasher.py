import hashlib
import secrets


class PasswordHasher:
    """Utility class for hashing passwords securely"""

    @staticmethod
    def hash_password(password, salt=None):
        """
        Hash a password using SHA-256 with salt.
        
        Args:
            password (str): The password to hash
            salt (str): Optional salt. If not provided, a random one is generated
            
        Returns:
            dict: Contains 'hash', 'salt', and 'salted_hash' (for display)
        """
        if salt is None:
            # Generate a random salt (16 bytes = 128 bits)
            salt = secrets.token_hex(16)
        
        # Hash the password with salt
        salted_password = f"{salt}{password}"
        hashed = hashlib.sha256(salted_password.encode()).hexdigest()
        
        return {
            'hash': hashed,
            'salt': salt,
            'salted_hash': f"{salt}${hashed}"
        }

    @staticmethod
    def verify_password(password, salted_hash):
        """
        Verify a password against a salted hash.
        
        Args:
            password (str): The password to verify
            salted_hash (str): The salted hash in format 'salt$hash'
            
        Returns:
            bool: True if password matches, False otherwise
        """
        try:
            salt, stored_hash = salted_hash.split('$')
            result = PasswordHasher.hash_password(password, salt)
            return result['hash'] == stored_hash
        except:
            return False

    @staticmethod
    def get_truncated_hash(password):
        """
        Get a truncated version of the hash for display purposes.
        While still maintaining security through truncation and formatting.
        
        Args:
            password (str): The password to hash
            
        Returns:
            str: Truncated hash suitable for display
        """
        result = PasswordHasher.hash_password(password)
        full_hash = result['salted_hash']
        # Display first 8 chars of salt and first 16 chars of hash
        salt, hash_part = full_hash.split('$')
        return f"{salt[:8]}...${hash_part[:16]}..."
