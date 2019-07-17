# coding=utf-8
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines, PDFTextExtractionNotAllowed
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage, LTRect, LTChar, LTTextBoxHorizontal
from pdfminer.converter import PDFPageAggregator

# file_path = r"1721-1723.pdf"
from utils import Document, Section

file_path = r"drug part_European Pharmacopoeia 8.0.pdf"
# file_path = r"1384-1386.pdf"

fp = open(file_path, 'rb')
parser = PDFParser(fp)
laparams = LAParams()
document = PDFDocument(parser)
# 检查文件是否允许文本提取
if not document.is_extractable:
    raise PDFTextExtractionNotAllowed

# 创建一个PDF资源管理器对象来存储共享资源
rsrcmgr = PDFResourceManager()
# 创建一个pdf设备对象
# device = PDFDevice(rsrcmgr)
device = PDFPageAggregator(rsrcmgr, laparams=laparams)
# 创建一个PDF解析器对象
interpreter = PDFPageInterpreter(rsrcmgr, device)

# 处理文档当中的每个页面

current_doc = None
current_section = None
line_height = 2
paragraph_height = 10.5
char_width = 2.1
line = ""
last_char = None

print "start extracting pdf"
for page in PDFPage.create_pages(document):
    interpreter.process_page(page)
    layout = device.get_result()

    for figure in layout:
        print type(figure)
        if isinstance(figure, LTTextBoxHorizontal):
            break
        if not isinstance(figure, LTFigure):
            continue
        for char in figure:
            if not isinstance(char, LTChar):
                continue
            if not 800 > char.y0 > 30:
                continue
            if last_char is None:
                line += char.get_text()
                
            elif abs(last_char.y0 - char.y0) < paragraph_height:
                space = char.x0 - last_char.x1
                if abs(last_char.y0 - char.y0) < line_height and space > char_width:
                    line += " " * int(space / char_width)
                line += char.get_text()
            else:
                # print line, last_char.fontname, last_char.size
                if "MinionPro-Bold" in last_char.fontname:
                    if int(last_char.size) == 13:
                        # 打印上一个文档
                        if current_doc is not None:
                            current_doc.add_contents(current_section)
                            current_doc.render()
                        # 新建文档
                        current_doc = Document(line)
                        
                        current_section = None
                    elif int(last_char.size) == 18:
                        current_doc.title = line.title()
                        print current_doc
                        current_section = Section(line)
                        
                elif current_doc is not None:
                    if line == line.upper():
                        if current_section is not None:
                            current_doc.add_contents(current_section)
                        current_section = Section(line)
                        print current_section
                    else:
                        current_section.add_contents(line)
                print line
                # 新行
                line = char.get_text()
            last_char = char
    break

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
