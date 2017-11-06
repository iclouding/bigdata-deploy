# -*- coding: utf-8 -*-
import requests

import hashlib

#sample
public_key = 'ucloudma.kai@moretv.com.cn1355800414123959271'
private_key = 'cd295132434ad835baa118f4da33e44bb7a419ac'

url='http://api.ucloud.cn/'

sample_data={
    "Action"     :  "DescribeBandwidthUsage",
    "Region"     :  "cn-bj2",
    "EIPIds.n"       :  "eip-vwulua",
    #"PublicKey"  :  public_key
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
    sign=_verfy_ac(private_key=private_key,params=sample_data)
    print sign

    r=requests.get(url,)

if __name__=="__main__":
    main()

