import json
import time
import random
import requests

import 代理api


def deepl_translator(sentence):
    sentence = '"' + sentence + '"'
    u_sentence = sentence.encode("unicode_escape").decode()
    data = '{"jsonrpc":"2.0","method": "LMT_handle_jobs","params":{"jobs":[{"kind":"default","raw_en_sentence":' + sentence + ',"raw_en_context_before":[],"raw_en_context_after":[],"preferred_num_beams":4,"quality":"fast"}],"lang":{"user_preferred_langs":["EN","ZH","JA"],"source_lang_user_selected":"auto","target_lang":"ZH"},"priority":-1,"commonJobParams":{},"timestamp":' + str(
        int(time.time() * 10000)) + '},"id":' + str(
        random.randint(1, 100000000)) + '}'
    r = requests.post('https://www2.deepl.com/jsonrpc',
                      headers={'content-type': 'application/json'},
                      data=data.encode()
                     )

    # r = requests.post('https://www2.deepl.com/jsonrpc',
    #                   headers={'content-type': 'application/json'},
    #                   data=data.encode())
    # print(r.json())
    if 'error' in r.json():
        a = 'error'
        return a
    else:
        a = r.json()['result']['translations'][0]['beams']
        return a

# one=deepl_translator('李さんは中国人です')
# print(one)
# print(one[0]['postprocessed_sentence'])
