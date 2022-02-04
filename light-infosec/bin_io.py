"""
This module facilitates input/output for files
including storing the buffer data as binary strings
to process them.

Code source: https://github.com/SuQinghang/CoursesCode/blob/b4b1c78b8436ffd796a3dfa5a54b9bbfa327fd65/Cryptology_Exp/code/DES/DES_encrypt.py
"""


def get_binary_from_file(path):
    with open(path, 'r') as f:
        text = f.read()
    text = text.split('\n')
    text = [eval(x) for x in text]
    text = ['{:08b}'.format(x) for x in text]
    text = ''.join(text)
    return text


def write_binary_to_file(path, data):
    f = open(path,'w+')
    for i in range(len(data)-1):
        f.write(data[i]+'\n')
    f.write(data[-1])


def get_key_from_file(path):
    with open(path,'r')as f:
        key = f.read()
    key = key.split('\n')
    key = [eval(x) for x in key]
    key = ['{:08b}'.format(x) for x in key]
    key = "".join(key)
    return key
