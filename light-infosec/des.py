"""
This module provides functions to perform DES encryption
and decryption on files.

Code source: https://github.com/SuQinghang/CoursesCode/blob/b4b1c78b8436ffd796a3dfa5a54b9bbfa327fd65/Cryptology_Exp/code/DES/DES_encrypt.py
"""


import des_utils as du
import bin_io as bi


def generateKset(key_path):
    key = bi.get_key_from_file(key_path)
    C,D = du.Key_Transposition(key)
    K = []
    for i in du.LeftRotate:
        C = du.Key_LeftRotate(C,i)
        C = du.Key_LeftRotate(D,i)
        K.append(du.Key_Compress(C,D))
    return K


def des_encrypt(source_file_path, target_file_path, keyfile_path):
    plaintext = bi.get_binary_from_file(source_file_path)
    L,R = du.IP_Transposition(plaintext)
    K = generateKset(keyfile_path)
    for i in range(0,15):
        oldR = R
        p_result = du.F(R,K[i])
        R = du.xor(L,p_result)
        L = oldR
    p_result = du.F(R,K[15])
    L = du.xor(L,p_result)
    reversedP = du.IP_reverseTransp(L+R)
    Cipher = du.generateHex(reversedP)
    bi.write_binary_to_file(target_file_path,Cipher)
    return Cipher


def des_decrypt(source_file_path, target_file_path, keyfile_path):
    Ciphertext = bi.get_binary_from_file(source_file_path)
    L,R = du.IP_Transposition(Ciphertext)
    K = generateKset(keyfile_path)
    for i in range(15,0,-1):
        oldR = R
        p_result = du.F(R,K[i])
        R = du.xor(L,p_result)
        L = oldR
    p_result = du.F(R,K[0])
    L = du.xor(L,p_result)
    reversedP = du.IP_reverseTransp(L+R)
    plaintext = du.generateHex(reversedP)
    bi.write_binary_to_file(target_file_path,plaintext)
    return plaintext
