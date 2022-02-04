"""
This module provides functions to perform DES encryption
and decryption on files.
"""


from Crypto.Cipher import DES
from des import DesKey

def encryptA(source_file_path, target_file_path, keyfile_path):
    pass


def decryptA(source_file_path, target_file_path, keyfile_path):
    pass


def encryptB(source_file_path, target_file_path, keyfile_path):
    with open(keyfile_path) as f:
        key = ''.join(f.readlines())
        key = str.encode(key, 'utf-8')
    key = DesKey(key)
    
    with open(source_file_path) as f:
        plaintext = ''.join(f.readlines())
        plaintext = str.encode(plaintext)
    cyphertext = key.encrypt(plaintext)

    with open(target_file_path, 'w') as f:
        f.write(str(cyphertext))


def decryptB(source_file_path, target_file_path, keyfile_path):
    """
    Source file should contain b'...'-like string (bytes)
    """
    with open(keyfile_path) as f:
        key = ''.join(f.readlines())
        key = str.encode(key, 'utf-8')
    key = DesKey(key)

    with open(source_file_path) as f:
        cyphertext = eval(f.readline())

    plaintext = key.decrypt(cyphertext)

    with open(target_file_path, 'w') as f:
        f.write(plaintext.decode('utf-8'))


def custom_encrypt(source_file_path, target_file_path, keyfile_path):
    pass


def custom_decrypt(source_file_path, target_file_path, keyfile_path):
    pass
