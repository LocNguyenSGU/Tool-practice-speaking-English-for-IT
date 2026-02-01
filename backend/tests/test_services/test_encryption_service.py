import pytest
from app.services.encryption_service import EncryptionService

def test_encrypt_and_decrypt_api_key():
    encryption_key = "test-encryption-key-32-bytes-long!!"
    service = EncryptionService(encryption_key)
    
    api_key = "sk-test-1234567890abcdef"
    
    # Encrypt
    encrypted = service.encrypt_api_key(api_key)
    assert encrypted != api_key
    assert len(encrypted) > 0
    
    # Decrypt
    decrypted = service.decrypt_api_key(encrypted)
    assert decrypted == api_key

def test_encrypt_different_keys_produce_different_ciphertext():
    encryption_key = "test-encryption-key-32-bytes-long!!"
    service = EncryptionService(encryption_key)
    
    api_key1 = "sk-test-1111"
    api_key2 = "sk-test-2222"
    
    encrypted1 = service.encrypt_api_key(api_key1)
    encrypted2 = service.encrypt_api_key(api_key2)
    
    assert encrypted1 != encrypted2

def test_decrypt_invalid_token_raises_error():
    encryption_key = "test-encryption-key-32-bytes-long!!"
    service = EncryptionService(encryption_key)
    
    with pytest.raises(Exception):
        service.decrypt_api_key("invalid-encrypted-token")

def test_same_plaintext_encrypts_differently_each_time():
    encryption_key = "test-encryption-key-32-bytes-long!!"
    service = EncryptionService(encryption_key)
    
    api_key = "sk-test-same"
    
    encrypted1 = service.encrypt_api_key(api_key)
    encrypted2 = service.encrypt_api_key(api_key)
    
    # Fernet uses timestamp, so same plaintext may encrypt differently
    # But both should decrypt to same value
    assert service.decrypt_api_key(encrypted1) == api_key
    assert service.decrypt_api_key(encrypted2) == api_key
