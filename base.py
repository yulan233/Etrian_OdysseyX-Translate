import struct
import time
import xml.dom.minidom

from feiqi import aliyun

shift_jis = {"8140": ' '}
shift_jis_fan = {" ": "8140"}


def switchSome(x):
    if x.isupper():
        return ord(x) + 33311
    else:
        return ord(x) + 33312


# 初始化一个码表
def init_shift_jis():
    with open('./shift_jis-unicode-文字.txt', 'r', encoding='UTF-8') as lines:
        for line in lines.readlines():
            # print(line)
            line1 = line.split("　")
            shift_jis[line1[0]] = line1[2].strip()[0]
    with open('./shift_jis-unicode-符号.txt', 'r', encoding='UTF-8') as lines:
        for line in lines.readlines():
            # print(line)
            line1 = line.split("　")
            shift_jis_fan[line1[2].strip()[0]] = line1[0]


# 返回读取到的mbm文件的十六进制数据
def read_mbm(filepath):
    with open(filepath, 'rb') as file_byte:
        file_hex = file_byte.read().hex()
        res = [file_hex[i:i + 2] for i in range(0, len(file_hex), 2)]
    return res


# 生成mbm的xml文件，第一个是生成文件位置，第二个读取的十六进制数据
def write_mbm_to_xml(filepath, file_hex):
    doc = xml.dom.minidom.Document()
    # 创建一些标签
    tree_root = doc.createElement("mbm")
    head = doc.createElement("head")
    size = doc.createElement("size")
    number = doc.createElement("number")
    j = doc.createElement("j")
    body = doc.createElement("body")
    # 添加到根
    doc.appendChild(tree_root)
    tree_root.appendChild(head)
    tree_root.appendChild(size)
    tree_root.appendChild(number)
    tree_root.appendChild(j)
    tree_root.appendChild(body)
    # 添加数据到标签
    head.appendChild(doc.createTextNode(''.join(file_hex[0:12])))
    size.appendChild(doc.createTextNode(''.join(file_hex[12:16])))
    number.appendChild(doc.createTextNode(''.join(file_hex[16:20])))
    j.appendChild(doc.createTextNode(''.join(file_hex[20:32])))
    # 读取总共多少条数据
    number1 = file_hex[16:20]
    number1.reverse()
    number1 = ''.join(number1)
    number1 = int(number1, 16)
    # 读取那些是有文本的，有文本的添加到list中
    i = 0
    list = []
    while i <= number1:
        id = doc.createElement("id")
        text = ''.join(file_hex[32 + i * 16: 32 + (i + 1) * 16])
        if int(text, 16) == 0:
            id.setAttribute("id", str(i))
            body.appendChild(id)
            i += 1
            continue
        id.setAttribute("id", str(i))
        body.appendChild(id)
        list.append(id)
        i += 1
    # 写入文本到id标签的translate标签和origin标签，一个是用来存翻译后的一个用来原文
    j = 0
    for ii in list:
        tag = 0
        text1 = ""
        text = ""
        for iii in file_hex[32 + i * 16 + j:]:
            text += iii
            tag += 1
            j += 1
            if tag == 2:
                tag = 0
                if text.upper() == 'FFFF':
                    text1 += ('\\' + text + '\\')
                    break
                if shift_jis.get(text.upper()) is None:
                    text1 += ('\\' + text + '\\')
                    text = ''
                    continue
                text1 += shift_jis.get(text.upper())
                text = ''
        origin = doc.createElement("origin")
        origin.appendChild(doc.createTextNode(text1))
        translate = doc.createElement("translate")
        translate.appendChild(doc.createTextNode(text1))
        ii.appendChild(origin)
        ii.appendChild(translate)
    # 以utf-8编码打开并写入文件filepath中
    fp = open(filepath, 'w', encoding="UTF-8")
    doc.writexml(fp, indent='\t', addindent='\t', newl='\n', encoding="UTF-8")


# 从xml中生成mbm
def write_xml_to_mbm(filepath, out_filepath):
    with open(out_filepath, 'wb') as new_file:
        root = xml.dom.minidom.parse(filepath)
        root_node = root.documentElement
        head = root_node.getElementsByTagName('head')[0]
        head_text = '' + head.childNodes[0].data
        head_text = [head_text[i:i + 2] for i in range(0, len(head_text), 2)]
        # 写入头
        for i in head_text:
            s = struct.pack('B', int(i, 16))
            new_file.write(s)
        # 有多少条数据
        number = '' + root_node.getElementsByTagName('number')[0].childNodes[0].data
        number = [number[i:i + 2] for i in range(0, len(number), 2)]
        number.reverse()
        number = int(''.join(number), 16)

        # 新的大小
        new_size = len(head_text) + 20 + 16 * (number + 1)
        body = root_node.getElementsByTagName('body')[0].getElementsByTagName('id')
        # 计算文本大小加入new_size中
        for id in body:
            if not id.childNodes:
                continue
            translate = str(id.getElementsByTagName('translate')[0].childNodes[0].data)
            i = 0
            for text in translate:
                if text == '\\':
                    i -= 3
                    continue
                i += 2
            new_size += i
        # 写入总大小
        new_file.write(struct.pack('B', int(new_size % (16 * 16))))
        new_file.write(struct.pack('B', int(new_size / (16 * 16)) % (16 * 16)))
        new_file.write(struct.pack('B', int(new_size / (16 * 16 * 16 * 16)) % (16 * 16)))
        new_file.write(struct.pack('B', int(new_size / (16 * 16 * 16 * 16 * 16 * 16)) % (16 * 16)))
        # 写入数据数量和一个定量
        new_file.write(struct.pack('B', int(number % (16 * 16))))
        new_file.write(struct.pack('B', int(number / (16 * 16))))
        new_file.write(struct.pack('B', int(number / (16 * 16 * 16 * 16))))
        new_file.write(struct.pack('B', int(number / (16 * 16 * 16 * 16 * 16 * 16))))
        j_text = '' + root_node.getElementsByTagName('j')[0].childNodes[0].data
        j_text = [j_text[i:i + 2] for i in range(0, len(j_text), 2)]
        for i in j_text:
            s = struct.pack('B', int(i, 16))
            new_file.write(s)
        # 计算每条位置和大小写入前面
        new_size = len(head_text) + 20 + 16 * (number + 1)
        all0 = ['00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00']
        for id in body:
            if not id.childNodes:
                for some in all0:
                    s = struct.pack('B', int(some, 16))
                    new_file.write(s)
                continue
            translate = str(id.getElementsByTagName('translate')[0].childNodes[0].data)
            i = 0
            for text in translate:
                if text == '\\':
                    i -= 3
                    continue
                i += 2

            # 写入序号
            xu_hao = int(id.getAttribute("id"))
            new_file.write(struct.pack('B', int(xu_hao % (16 * 16))))
            new_file.write(struct.pack('B', int(xu_hao / (16 * 16)) % (16 * 16)))
            new_file.write(struct.pack('B', int(xu_hao / (16 * 16 * 16 * 16)) % (16 * 16)))
            new_file.write(struct.pack('B', int(xu_hao / (16 * 16 * 16 * 16 * 16 * 16)) % (16 * 16)))
            # 写入长度
            new_file.write(struct.pack('B', int(i % (16 * 16))))
            new_file.write(struct.pack('B', int(i / (16 * 16)) % (16 * 16)))
            new_file.write(struct.pack('B', int(i / (16 * 16 * 16 * 16)) % (16 * 16)))
            new_file.write(struct.pack('B', int(i / (16 * 16 * 16 * 16 * 16 * 16)) % (16 * 16)))
            # 写入起始位置
            new_file.write(struct.pack('B', int(new_size % (16 * 16))))
            new_file.write(struct.pack('B', int(new_size / (16 * 16)) % (16 * 16)))
            new_file.write(struct.pack('B', int(new_size / (16 * 16 * 16 * 16)) % (16 * 16)))
            new_file.write(struct.pack('B', int(new_size / (16 * 16 * 16 * 16 * 16 * 16)) % (16 * 16)))
            new_file.write(struct.pack('B', int(new_size / (16 * 16 * 16 * 16 * 16 * 16 * 16)) % (16 * 16)))
            new_file.write(struct.pack('B', int(new_size / (16 * 16 * 16 * 16 * 16 * 16 * 16 * 16)) % (16 * 16)))
            new_file.write(struct.pack('B', int(new_size / (16 * 16 * 16 * 16 * 16 * 16 * 16 * 16 * 16)) % (16 * 16)))
            new_file.write(
                struct.pack('B', int(new_size / (16 * 16 * 16 * 16 * 16 * 16 * 16 * 16 * 16 * 16)) % (16 * 16)))

            # 添加上新大小
            # 写入translate中的内容
            new_size += i
        for id in body:
            if not id.childNodes:
                continue
            translate = str(id.getElementsByTagName('translate')[0].childNodes[0].data)
            tag = True
            i = 0
            tmp = ''
            for text in translate:
                if text == '\\':
                    if tag:
                        i = 0
                        tag = False
                    else:
                        tag = True
                    continue
                if tag:
                    # 转成unicode码
                    if text.encode("utf-8").isalpha():
                        x = switchSome(text)
                    else:
                        x = ord(text)
                    if shift_jis_fan.get(text) is not None:
                        x = int(shift_jis_fan.get(text), 16)
                    # 写入到文件
                    new_file.write(struct.pack('B', int(x / (16 * 16))))
                    new_file.write(struct.pack('B', int(x % (16 * 16))))
                else:
                    # 写入\\中的内容
                    tmp += text
                    i += 1
                    if i == 2:
                        i = 0
                        new_file.write(struct.pack('B', int(tmp, 16)))
                        tmp = ''


# 返回读取到的TBL文件的十六进制数据
def read_tbl(filepath):
    with open(filepath, 'rb') as file_byte:
        file_hex = file_byte.read().hex()
        res = [file_hex[i:i + 2] for i in range(0, len(file_hex), 2)]
    return res


# 生成tbl的xml文件，第一个是生成文件位置，第二个读取的十六进制数据
def write_tbl_to_xml(filepath, file_hex):
    doc = xml.dom.minidom.Document()
    # 创建一些标签
    tree_root = doc.createElement("tbl")
    numbers = doc.createElement("numbers")
    body = doc.createElement('body')
    doc.appendChild(tree_root)
    tree_root.appendChild(numbers)
    tree_root.appendChild(body)
    # 读取数量
    numbers.appendChild(doc.createTextNode(''.join(file_hex[0:2])))
    number = file_hex[0:2]
    number.reverse()
    number = int(''.join(number), 16)
    number = 2 + number * 2
    # 读取文本
    i = 0
    ii = 0
    text = ''
    text1 = ''
    id = doc.createElement("id")
    id.setAttribute("id", str(ii))
    ii += 1
    for code in file_hex[number:]:
        if int(code, 16) == 0:
            origin = doc.createElement('origin')
            translate = doc.createElement('translate')
            origin.appendChild(doc.createTextNode(text1))
            translate.appendChild(doc.createTextNode(text1))
            id.appendChild(origin)
            id.appendChild(translate)
            body.appendChild(id)
            ii += 1
            id = doc.createElement("id")
            id.setAttribute("id", str(ii))
            text1 = ''
            continue
        text += code
        i += 1
        if i == 2:
            i = 0
            text1 += shift_jis.get(text.upper())
            text = ''
    fp = open(filepath, 'w', encoding="UTF-8")
    doc.writexml(fp, indent='\t', addindent='\t', newl='\n', encoding="UTF-8")


# 从xml中生成tbl
def write_xml_to_tbl(filepath, out_filepath):
    with open(out_filepath, 'wb') as new_file:
        root = xml.dom.minidom.parse(filepath)
        root_node = root.documentElement
        numbers = root_node.getElementsByTagName('numbers')[0].childNodes[0].data
        numbers = [numbers[i:i + 2] for i in range(0, len(numbers), 2)]
        # 写入文本条数
        for i in numbers:
            s = struct.pack('B', int(i, 16))
            new_file.write(s)
        ids = root_node.getElementsByTagName('body')[0].getElementsByTagName('id')
        size = 0
        for id in ids:
            text = id.getElementsByTagName('translate')[0].childNodes[0].data
            size = size + len(text) * 2 + 1
            new_file.write(struct.pack('B', int(size % (16 * 16))))
            new_file.write(struct.pack('B', int(size / (16 * 16))))
        for id in ids:
            text = id.getElementsByTagName('translate')[0].childNodes[0].data
            for code in text:
                code = ord(code)
                if int(code / (16 * 16)) == 0 or int(code % (16 * 16)) == 0:
                    new_file.write(struct.pack('B', 81))
                    new_file.write(struct.pack('B', 48))
                new_file.write(struct.pack('B', int(code / (16 * 16))))
                new_file.write(struct.pack('B', int(code % (16 * 16))))
            new_file.write(struct.pack('b', 0))


def write_file1(filepath, file_hex):
    with open(filepath, 'wb') as new_file:
        for i in file_hex:
            s = struct.pack('B', int(i, 16))
            new_file.write(s)


# 返回读取到的TBL文件的十六进制数据
def read_code(filepath):
    with open(filepath, 'rb') as file_byte:
        file_hex = file_byte.read().hex()
        res = [file_hex[i:i + 2] for i in range(0, len(file_hex), 2)]
    return res


def write_new_code1(filepath, code):
    with open('feiqi/code.txt', 'r', encoding='UTF-8') as codetext:
        with open(filepath, 'wb') as new_file:
            i = 0
            codetext1 = codetext.readline()
            codetext1 = codetext1.split(' ==')
            print(codetext1)
            while i < len(code):
                if codetext1[0] != '' and i == int(codetext1[3][:len(codetext1[3]) - 1]):
                    a = 0
                    for code1 in codetext1[1]:
                        if a == len(codetext1[0]):
                            break
                        if code1.encode("utf-8").isalpha():
                            print(code1)
                            code2 = switchSome(code1)
                            print(code1)
                        else:
                            code2 = ord(code1)
                        if int(code2 / (16 * 16)) == 0 or int(code2 % (16 * 16)) == 0:
                            new_file.write(struct.pack('B', 81))
                            new_file.write(struct.pack('B', 48))
                        else:
                            if shift_jis_fan.get(code1) is not None:
                                print(code1)
                                x = int(shift_jis_fan.get(code1), 16)
                                code2 = x
                            new_file.write(struct.pack('B', int(code2 / (16 * 16))))
                            new_file.write(struct.pack('B', int(code2 % (16 * 16))))
                        a += 1
                    while a < len(codetext1[0]):
                        new_file.write(struct.pack('B', 81))
                        new_file.write(struct.pack('B', 40))
                        a += 1
                    i += a * 2
                    codetext1 = codetext.readline()
                    codetext1 = codetext1.split(' ==')
                    print(codetext1)
                    continue
                new_file.write(struct.pack('B', int(code[i], 16)))
                i += 1
            print(i)


# 写入新的.code文件
def write_new_code(filepath, code):
    with open(filepath, 'wb') as new_file:
        c = 0
        cc = {23, 24, 25, 27, 28, 33, 56, 57, 58, 60, 61, 62, 63, 70, 71, 72, 92, 95, 102, 125, 126, 132, 133, 134, 183,
              251, 243}
        cccc = True
        i = 0
        ii = True
        iii = True
        tmp2 = ''
        tmp3 = 0
        while i < len(code):
            if c > 250:
                new_file.write(struct.pack('B', int(code[i], 16)))
                # print(i)
                i += 1
                continue
            if code[i] == '00' and iii:
                new_file.write(struct.pack('B', int(code[i], 16)))
                # print(i)
                i += 1
                tmp3 = i
                iii = False
            if iii:
                new_file.write(struct.pack('B', int(code[i], 16)))
                # print(i)
                i += 1
                continue
            tmp = code[i] + code[i + 1]
            tmp1 = shift_jis.get(tmp.upper())
            # print(tmp1)
            if tmp1 is not None:
                tmp2 += tmp1
                i += 2
                # ii = True
                # print(tmp2)
                continue
            # else:
            # ii = False
            # i = tmp3
            if ii:
                if tmp2 != '' and len(tmp2) > 3:
                    cccc = True
                    for ccc in cc:
                        if c == ccc or 16 >= c >= 0:
                            cccc = False
                    if cccc:
                        time.sleep(0.1)
                        args = {
                            'format_type': 'text',
                            'source_language': 'auto',
                            'target_language': 'zh',
                            'source_text': tmp2,
                            'scene': 'general'
                        }
                        tmp4 = aliyun.Sample.main(args)
                        # print(tmp4[0]['postprocessed_sentence'])
                        print(tmp2, '==' + tmp4, "==" + str(c), "==" + str(tmp3))
                        a = 0
                        for code1 in tmp4:
                            if a == len(tmp2):
                                break
                            code1 = ord(code1)
                            if int(code1 / (16 * 16)) == 0 or int(code1 % (16 * 16)) == 0:
                                new_file.write(struct.pack('B', 81))
                                new_file.write(struct.pack('B', 48))
                            new_file.write(struct.pack('B', int(code1 / (16 * 16))))
                            new_file.write(struct.pack('B', int(code1 % (16 * 16))))
                            a += 1
                        while a < len(tmp2):
                            new_file.write(struct.pack('B', 81))
                            new_file.write(struct.pack('B', 40))
                            a += 1
                    else:
                        while tmp3 < i:
                            new_file.write(struct.pack('B', int(code[tmp3], 16)))
                            # print(tmp3)
                            tmp3 += 1
                    c += 1
                else:
                    while tmp3 < i:
                        new_file.write(struct.pack('B', int(code[tmp3], 16)))
                        # print(tmp3)
                        tmp3 += 1
                # ii = False
            iii = True
            tmp2 = ''


if __name__ == '__main__':
    init_shift_jis()
    # write_xml_to_mbm('HPI2/ANIMTABLE/ANIM_A01.xml', 'D.MBM')
    # with open("./TBL1.txt", encoding="utf-8") as f:
    #     with open("./TBL2.txt", encoding="utf-8") as ff:
    #         f_lines = f.readlines()
    #         ff_lines = ff.readlines()
    #         i = 0
    #         while i < len(f_lines):
    #
    #             fileoutput = ff_lines[i][:len(ff_lines[i]) - 1] + ".xml"
    #             filepat =ff_lines[i][:len(ff_lines[i]) - 1]+".TBL"
    #             write_xml_to_tbl(fileoutput,filepat)
    #             i = i + 1
    # switchSome("A")
    # text = "均"
    # if text.encode("utf-8").isalpha():
    #     print("ok")
    # else:
    #     print("no")
    code = read_code('feiqi/.code')
    with open('feiqi/new.code', 'wb') as new_file:
        for i in code:
            s = struct.pack('B', int(i, 16))
            new_file.write(s)
    write_new_code1('feiqi/new.code', code)
    # c = 0
    # cc = {23, 24, 25, 27, 28, 33, 56, 57, 58, 60, 61, 62, 63, 70, 71, 72, 92, 95, 102, 125, 126, 132, 133, 134, 183,
    #       251}
    # cccc = True
    # i = 0
    # ii = True
    # iii = True
    # tmp2 = ''
    # tmp3 = 0
    # while i < len(code) - 2:
    #     if code[i] == '00' and iii:
    #         i += 1
    #         tmp3 = i
    #         iii = False
    #     if iii:
    #         i += 1
    #         continue
    #     tmp = code[i] + code[i + 1]
    #     tmp1 = shift_jis.get(tmp.upper())
    #     # print(tmp1)
    #     if tmp1 is not None:
    #         tmp2 += tmp1
    #         i += 2
    #         # ii = True
    #         # print(tmp2)
    #         continue
    #     # else:
    #     # ii = False
    #     # i = tmp3
    #     if ii:
    #         if tmp2 != '' and len(tmp2) > 3:
    #             cccc = True
    #             for ccc in cc:
    #                 if c == ccc or 16 >= c >= 0:
    #                     cccc = False
    #             if cccc:
    #                 print(tmp2, "  " + str(c), "   " + str(tmp3))
    #             c += 1
    #         else:
    #             i = tmp3
    #         # ii = False
    #     iii = True
    #     tmp2 = ''
