# -*- coding: utf-8 -*-

import hashlib
import time
from xml.dom.minidom import parse

import aliyun
import 代理api


def saveip():
    return 代理api.getip()


global ip
ip = saveip()


def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()


def truncate(q):
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]


def xmlGetAndUpdate(name):
    global ip
    domTree = parse(name)
    # 文档根元素
    rootNode = domTree.documentElement
    print(rootNode.nodeName)
    aaa = 0
    bbb = True
    # 所有list
    lists = rootNode.getElementsByTagName("Body")[0].getElementsByTagName("listElem")
    print("****所有信息****")
    for list in lists:
        if list.hasAttribute("id"):

            # if int(list.getAttribute("id"))<8934:
            #     continue
            # translation 元素
            translation = list.getElementsByTagName("translation")[0]
            original = list.getElementsByTagName("original")[0]
            if not translation.childNodes:
                print("id:", list.getAttribute("id"))
                continue
            if translation.childNodes[0].data != original.childNodes[0].data:
                continue

            print("id:", list.getAttribute("id"))
            print(translation.nodeName, ":", translation.childNodes[0].data)
            if translation.childNodes[0].data == "\FFFF\\":
                continue
            if translation.childNodes[0].data == "－－\F801\\\\FFFF\\":
                continue

            chuli1 = str(translation.childNodes[0].data)
            chuli = ""
            tran = ""
            for i in chuli1:
                if i == "\\":
                    if chuli != "":
                        # time.sleep(0.04)
                        # tran = tran + connect(chuli, random.randint(0, 9))
                        # tran = tran + connect(chuli, aaa%10)
                        # tran = tran + connect1(chuli)
                        args = {
                            'format_type': 'text',
                            'source_language': 'ja',
                            'target_language': 'zh',
                            'source_text': chuli,
                            'scene': 'general'
                        }
                        if chuli == '！':
                            tran = tran + "!"
                        else:
                            tran = tran + aliyun.Sample.main(args)
                    tran = tran + i
                    if bbb:
                        bbb = False
                    else:
                        bbb = True
                    continue
                if bbb:
                    chuli = chuli + i
                else:
                    chuli = ""
                    tran = tran + i
            print(tran)
            print("等待0.2s")
            time.sleep(0.2)
            translation.childNodes[0].data = tran
            if aaa > 10:
                with open(name, 'w', encoding='UTF-8') as f:
                    # 缩进 - 换行 - 编码
                    domTree.writexml(f, encoding='UTF-8')
                    f.close()
                aaa = 0
            else:
                aaa = aaa + 1

    with open(name, 'w', encoding='UTF-8') as f:
        # 缩进 - 换行 - 编码
        domTree.writexml(f, encoding='UTF-8')
        f.close()


def xmlGetAndUpdate2(name):
    global ip
    domTree = parse(name)
    # 文档根元素
    rootNode = domTree.documentElement
    print(rootNode.nodeName)
    aaa = 0
    bbb = True
    # 所有list
    lists = rootNode.getElementsByTagName("body")[0].getElementsByTagName("id")
    print("****所有信息****")
    for list in lists:

        # if int(list.getAttribute("id"))<8934:
        #     continue
        # translation 元素
        translation = list.getElementsByTagName("translate")[0]
        original = list.getElementsByTagName("origin")[0].childNodes[0].data
        if translation.childNodes[0].data != original:
            continue
        if translation.childNodes[0].data == "ＮＯＮＥ":
            continue

        chuli1 = str(translation.childNodes[0].data)
        tran = ""

        args = {
                        'format_type': 'text',
                        'source_language': 'ja',
                        'target_language': 'zh',
                        'source_text': chuli1,
                        'scene': 'general'
        }
        tran=aliyun.Sample.main(args)
        print(tran)
        print("等待0.1s")
        time.sleep(0.1)
        translation.childNodes[0].data = tran
        if aaa > 10:
            with open(name, 'w', encoding='UTF-8') as f:
                # 缩进 - 换行 - 编码
                domTree.writexml(f, encoding='UTF-8')
                f.close()
            aaa = 0
        else:
            aaa = aaa + 1

    with open(name, 'w', encoding='UTF-8') as f:
        # 缩进 - 换行 - 编码
        domTree.writexml(f, encoding='UTF-8')
        f.close()


# if __name__ == '__main__':
#     # xmlGetAndUpdate("HPI/DICTIONARYREPORT/DICREPORTITEMMSG.xml")
#     # print("OK")
#     with open("xml.txt", "r", encoding='UTF-8') as f:
#         for line in f.readlines():
#             line = line.strip('\n')  # 去掉列表中每一个元素的换行符
#             xmlGetAndUpdate(line)
#             print("完成", line)
#     print("全部翻译完成\n哈哈哈哈哈哈哈")
if __name__ == '__main__':
    with open("tblxml.txt", "r", encoding='GBK') as f:
        for line in f.readlines():
            line = line.strip('\n')  # 去掉列表中每一个元素的换行符
            xmlGetAndUpdate2(line)
            print("完成", line)
    print("全部翻译完成\n哈哈哈哈哈哈哈")
