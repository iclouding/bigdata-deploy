# -*- coding: utf-8 -*-
import requests

import hashlib

#sample
PublicKey  = 'ucloudsomeone@example.com1296235120854146120'
PrivateKey = '46f09bb9fab4f12dfc160dae12273d5332b5debe'

sample_data={
    "Action"     :  "CreateUHostInstance",
    "Region"     :  "cn-bj2",
    "Zone"       :  "cn-bj2-04",
    "ImageId"    :  "f43736e1-65a5-4bea-ad2e-8a46e18883c2",
    "CPU"        :  2,
    "Memory"     :  2048,
    "DiskSpace"  :  10,
    "LoginMode"  :  "Password",
    "Password"   :  "VUNsb3VkLmNu",
    "Name"       :  "Host01",
    "ChargeType" :  "Month",
    "Quantity"   :  1,
    "PublicKey"  :  "ucloudsomeone@example.com1296235120854146120"
}

#4f9ef5df2abab2c6fccd1e9515cb7e2df8c6bb65

def _verfy_ac(private_key, params):
    items = params.items()
    # 请求参数串
    items.sort()
    # 将参数串排序

    params_data = ""
    for key, value in items:
        params_data = params_data + str(key) + str(value)
    params_data = params_data + private_key

    sign = hashlib.sha1()
    sign.update(params_data)
    signature = sign.hexdigest()

    return signature
    # 生成的Signature值

def main():
    sign=_verfy_ac(private_key=PrivateKey,params=sample_data)
    print sign

if __name__=="__main__":
    main()

