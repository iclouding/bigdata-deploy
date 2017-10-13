#!/usr/bin/python
# -*- coding: utf-8 -*-

#pip install pycrypto
from Crypto.Cipher import AES

from binascii import b2a_hex, a2b_hex
import sys

class MyCrypto():
    def __init__(self, key):
        self.key_len = len(key)
        if not self.key_len == 16 and not self.key_len == 24 and not self.key_len == 32:
            raise Exception("length of key is wrong")
        self.key = key
        self.mode = AES.MODE_CBC    #这种模式更加安全

    def encrypt(self, text):
        '''
            被加密的明文长度必须是key长度的整数倍,如果不够,则用\0进行填充
            转成16进制字符串,是因为避免不可见的ascii在显示的时候捣乱
        '''
        cryptor = AES.new(self.key, self.mode, self.key)
        count = len(text)
        add = self.key_len - (count % self.key_len)
        text = text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(text)
        return b2a_hex(self.ciphertext)


    def decrypt(self, text):
        '''
            解密后需注意,加密时有可能填充\0,因此要去掉右侧的\0
        '''
        cryptor = AES.new(self.key, self.mode, self.key)
        plain_text = cryptor.decrypt(a2b_hex(text))
        return plain_text.rstrip('\0')


if __name__ == '__main__':
    key = 'djfhj878DFHGFDJ3'
    mc = MyCrypto(key)
    if len(sys.argv) != 3:
        raise "Muse choose encrypt or decrypt  and values "
    method=sys.argv[1]
    values=sys.argv[2]
    if  method not in ('encrypt','decrypt'):
        raise "Must choose encrypt or decrypt "
    elif method=="encrypt":
        print  mc.encrypt(values)
    elif method=='decrypt':
        print mc.decrypt(values)
    else:
        print "Must choose encrypt or decrypt "
    #
    # e = mc.encrypt("张东升")
    # d = mc.decrypt(e)
    # print e,d