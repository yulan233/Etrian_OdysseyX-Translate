import PySimpleGUI as sg  # Part 1 - The import
import base

# Define the window's contents
layout = [[sg.Text("一段无用的文字在这里占个位子,提取文本功能没写，只有生成文件功能，需要将要生成的文本放入HPI2文件夹,物品怪物技能名字在")],
          [sg.Text("MORIS.HPI中")],
          [sg.Button("提取文本")],  # Part 2 - The Layout
          [sg.Button('生成文件')],
          [sg.Button('生成物品技能怪物名字')]]

# Create the window
window = sg.Window('小脚本', layout)  # Part 3 - Window Defintion

# Display and interact with the Window
event, values = window.read()  # Part 4 - Event loop or Window.read call
# if event in "提取文本":
#     base.init_shift_jis()
#     with open('./MBM1.txt', 'r') as items1:
#         with open('./MBM2.txt', 'r') as items:
#             i = 0
#             while i < 412:
#                 mbm = base.read_mbm(items + ".MBM")
#                 base.write_mbm_to_xml(items1 + ".xml", mbm)
#                 i += 1
if event == "生成文件":
    base.init_shift_jis()
    with open('./MBM1.txt', 'r') as items1:
        with open('./MBM3.txt', 'r') as items:
            i = 0
            while i < 412:
                file_path = items1.readline()
                file_out_path = items.readline()
                base.write_xml_to_mbm(file_path[:len(file_path) - 1] + '.xml',
                                      file_out_path[:len(file_out_path) - 1] + '.MBM')
                i += 1
if event == '生成物品技能怪物名字':
    base.init_shift_jis()
    with open("./TBL2.txt", encoding="utf-8") as ff:
        ff_lines = ff.readlines()
        i = 0
        while i < len(ff_lines):
            fileoutput = ff_lines[i][:len(ff_lines[i]) - 1] + ".xml"
            filepat = ff_lines[i][:len(ff_lines[i]) - 1] + ".TBL"
            base.write_xml_to_tbl(fileoutput, filepat)
            i = i + 1

# Finish up by removing from the screen
window.close()  # Part 5 - Close the Window
