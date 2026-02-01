from cryptography.fernet import Fernet
import base64
import hashlib

class EncryptionService:
    """Service for encrypting and decrypting sensitive data like API keys"""
    
    def __init__(self, encryption_key: str):
        """
        Initialize the encryption service
        
        Args:
            encryption_key: A string key that will be hashed to create Fernet key
        """
        # Hash the encryption key to ensure it's the right length (32 bytes)
        key_bytes = hashlib.sha256(encryption_key.encode()).digest()
        self.fernet_key = base64.urlsafe_b64encode(key_bytes)
        self.cipher = Fernet(self.fernet_key)
    
    def encrypt_api_key(self, api_key: str) -> str:
        """
        Encrypt an API key
        
        Args:
            api_key: Plain text API key to encrypt
            
        Returns:
            Encrypted API key as base64 string
        """
        encrypted = self.cipher.encrypt(api_key.encode())
        return encrypted.decode()
    
    def decrypt_api_key(self, encrypted_api_key: str) -> str:
        """
        Decrypt an encrypted API key
        
        Args:
            encrypted_api_key: Encrypted API key (base64 string)
            
        Returns:
            Decrypted plain text API key
            
        Raises:
            Exception: If decryption fails (invalid token or key)
        """
        decrypted = self.cipher.decrypt(encrypted_api_key.encode())
        return decrypted.decode()
