# coding=utf-8
from collections import Iterable
from functools import cmp_to_key
from string import ascii_letters

from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTChar
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter, PDFTextExtractionNotAllowed
from pdfminer.pdfparser import PDFParser, PDFDocument

from utils import Document, Section

file_path = r"drug part_European Pharmacopoeia 8.0.pdf"
file_path = r"1384-1386.pdf"

fp = open(file_path, 'rb')
parser = PDFParser(fp)
laparams = LAParams(line_overlap=0.1, char_margin=1.0, line_margin=0.1)
document = PDFDocument()
parser.set_document(document)
document.set_parser(parser)
# document = PDFDocument(parser)
# 检查文件是否允许文本提取
if document.encryption:
    raise PDFTextExtractionNotAllowed

# 创建一个PDF资源管理器对象来存储共享资源
rsrcmgr = PDFResourceManager()
# 创建一个pdf设备对象
# device = PDFDevice(rsrcmgr)
device = PDFPageAggregator(rsrcmgr, laparams=laparams)
# 创建一个PDF解析器对象
interpreter = PDFPageInterpreter(rsrcmgr, device)


def char_cmp(char1, char2):
    page_width = 622
    if char1.x0 > page_width / 2 and char2.x0 > page_width / 2 or char1.x0 < page_width / 2 and char2.x0 < page_width / 2:
        # if char1.y0==char2.y0:
        if abs(char1.y0 - char2.y0) < char1.height * .6:
            if char1.x0 > char2.x0:
                return 1
            elif char1.x0 < char2.x0:
                return -1
            else:
                return 0
        elif char1.y0 > char2.y0:
            return -1
        else:
            return 1
    else:
        if char1.x0 < page_width / 2:
            return -1
        else:
            return 1


def extract_char(obj):
    if isinstance(obj, LTChar):
        yield obj
    elif isinstance(obj, Iterable):
        for i in obj:
            for m in extract_char(i):
                yield m


current_doc = None
current_section = None
line_height = 2
paragraph_space_ratio = 0.826
paragraph_height = 10.5
char_width = 2.1
line = ""
last_char = None
i = 1
# 处理文档当中的每个页面
print("start extracting pdf")
for page in document.get_pages():
    interpreter.process_page(page)
    layout = device.get_result()

    raw_chars = extract_char(layout)
    chars = sorted(raw_chars, key=cmp_to_key(char_cmp))
    for char in chars:
        if not isinstance(char, LTChar):
            continue
        # 跳过页眉页脚
        if not 800 > char.y0 > 30:
            continue

        if last_char is None:
            line += char.get_text()

        # 如果是同一行
        elif abs(last_char.y0 - char.y0) < last_char.height * paragraph_space_ratio:
            space = char.x0 - last_char.x1
            if abs(last_char.y0 - char.y0) < line_height:
                if space > char_width:
                    line += " " * int(space / char_width)
            else:
                if char.get_text() in "123456789(" or last_char.get_text() in ascii_letters + ",.)" and char.get_text() in ascii_letters:
                    line += " "

            line += char.get_text()
        else:
            if "MinionPro-Bold" in last_char.fontname:
                if int(last_char.size) == 13:
                    if 290 < last_char.x0 < 300 or 540 < last_char.x0 < 550:
                        # 打印上一个文档
                        if current_doc is not None:
                            current_doc.add_contents(current_section)
                            try:
                                current_doc.render()
                            except BaseException as e:
                                print("error", e)
                        # 新建文档
                        current_doc = Document(line)

                        current_section = None
                elif int(last_char.size) == 18:
                    current_doc.title = line.title()
                    # print current_doc
                    current_section = Section(line)

            elif current_doc is not None:
                if line == line.upper():
                    if current_section is not None:
                        current_doc.add_contents(current_section)
                    current_section = Section(line)
                    # print current_section
                elif current_section is not None:
                    current_section.add_contents(line)
                else:
                    print("Error", current_doc)
                    print(line, last_char.x0)
            # print line
            # 新行
            line = char.get_text()
        last_char = char
    i += 1
    if i >= 3:
        pass
        # break

'''
last_char = None
for char in figure:
    if not 800 > char.y0 > 50:
        continue
    if not isinstance(char, LTChar):
        continue
    # print char.get_text(),char.width, char.size, char.x0,char.y0
    if last_char is not None:
        print char.get_text(), char.x0, char.y0
    last_char = char
'''
if __name__ == '__main__':
    pass