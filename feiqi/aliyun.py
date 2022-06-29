# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import sys

from typing import List

from alibabacloud_alimt20181012.client import Client as alimt20181012Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alimt20181012 import models as alimt_20181012_models


class Sample:
    def __init__(self):
        pass

    @staticmethod
    def create_client(
            access_key_id: str,
            access_key_secret: str,
    ) -> alimt20181012Client:
        """
        使用AK&SK初始化账号Client
        @param access_key_id:
        @param access_key_secret:
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(
            # 您的AccessKey ID,
            access_key_id="",
            # 您的AccessKey Secret,
            access_key_secret=""
        )
        # 访问的域名
        config.endpoint = f'mt.cn-hangzhou.aliyuncs.com'
        return alimt20181012Client(config)

    @staticmethod
    def main(lll):
        client = Sample.create_client('accessKeyId', 'accessKeySecret')
        # translate_general_request = alimt_20181012_models.TranslateGeneralRequest()
        translate_general_request = alimt_20181012_models.TranslateGeneralRequest(
            format_type=lll.get("format_type"),
            source_language=lll.get('source_language'),
            target_language=lll.get('target_language'),
            source_text=lll.get('source_text'),
            scene=lll.get('scene')
        )
        # 复制代码运行请自行打印 API 的返回值

        a = client.translate_general(translate_general_request)
        # print(a.body.data.translated)
        return a.body.data.translated

    @staticmethod
    async def main_async(
            args: List[str],
    ) -> None:
        client = Sample.create_client('accessKeyId', 'accessKeySecret')
        translate_general_request = alimt_20181012_models.TranslateGeneralRequest()

        # 复制代码运行请自行打印 API 的返回值
        await client.translate_general_async(translate_general_request)


if __name__ == '__main__':
    args = {
        'format_type': 'text',
        'source_language': 'ja',
        'target_language': 'zh',
        'source_text': 'ブロート',
        'scene': 'general'
    }
    Sample.main(args)


def yuyu():
    return None