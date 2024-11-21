from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import os
import rsa

from pchat.core.commons import public_key, private_key


# Función para generar una clave AES
def generate_aes_key():
    return os.urandom(32)

# Cifrar mensaje usando AES
def encrypt_aes(message, aes_key):
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(aes_key[:16]))
    encryptor = cipher.encryptor()

    # Relleno del mensaje
    padder = padding.PKCS7(128).padder()
    padded_message = padder.update(message.encode()) + padder.finalize()

    return encryptor.update(padded_message) + encryptor.finalize()

# Descifrar mensaje usando AES
def decrypt_aes(encrypted_message, aes_key):
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(aes_key[:16]))
    decryptor = cipher.decryptor()

    # Desencriptar y eliminar relleno
    unpadder = padding.PKCS7(128).unpadder()
    padded_message = decryptor.update(encrypted_message) + decryptor.finalize()
    return unpadder.update(padded_message) + unpadder.finalize()

# Uso de RSA para cifrar y descifrar la clave AES
aes_key = generate_aes_key()
encrypted_aes_key = rsa.encrypt(aes_key, public_key)  # Cifrar clave AES con clave pública
decrypted_aes_key = rsa.decrypt(encrypted_aes_key, private_key)  # Descifrar clave AES con clave privada
