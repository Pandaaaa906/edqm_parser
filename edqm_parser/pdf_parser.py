import re
from pathlib import Path
from typing import Optional, List, Tuple, Union

from loguru import logger
from more_itertools import first, nth

from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTImage, LTContainer, LTChar, LTTextLine, LTAnno
from pdfminer.pdfdocument import PDFDocument, PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

from .utils import Document, Section, Paragraph, Image


def get_images(layout_object: LTContainer):
    if isinstance(layout_object, LTContainer):
        for obj in layout_object:
            yield from get_images(obj)
    elif isinstance(layout_object, LTImage):
        yield layout_object


def guess_font_info(obj: Union[LTTextBox, LTChar]) -> Optional[Tuple[str, float]]:
    if isinstance(obj, LTChar):
        return obj.fontname, obj.size
    if isinstance(obj, LTTextBox):
        first_line = first((line for line in obj if isinstance(line, LTTextLine) and line.get_text()), None)
        if not first_line:
            return
        chars = [char for char in first_line if isinstance(char, LTChar)]
        last_char = nth(chars, len(chars)//2)
        if not last_char:
            return
        return last_char.fontname, last_char.size


def get_upper_nearest_image(images: List[LTImage], x: float, y: float, mid: float) -> Optional[LTImage]:
    img_idx = 0
    while img_idx < len(images):
        img = images[img_idx]
        if (img.x0 < mid) is not (x < mid):
            img_idx += 1
            continue
        if y + 50 > img.y0 > y:
            images.pop(img_idx)
            return img
        img_idx += 1


def extract_edqm(fp: Union[Path, str], /, output_root: Path = Path("html")):
    if isinstance(fp, str):
        fp = Path(fp)
    logger.info(f"start processing {fp.name}")
    f = fp.open('rb')
    parser = PDFParser(f)
    document = PDFDocument(parser)
    parser.set_document(document)
    # document = PDFDocument(parser)
    # 检查文件是否允许文本提取
    if document.encryption:
        raise PDFTextExtractionNotAllowed
    rsrcmgr = PDFResourceManager()
    laparams = LAParams(line_overlap=0.1, line_margin=0.1, char_margin=1.5)
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    current_doc: Optional[Document] = None
    current_section: Optional[Section] = None

    for pageNumber, page in enumerate(PDFPage.get_pages(f)):

        interpreter.process_page(page)
        layout = device.get_result()

        images = list(filter(lambda x: 10 < x.x0 < 560, get_images(layout)))
        lines = [line for line in layout if isinstance(line, LTTextBox) and 800 > line.y0 > 30]
        lines = sorted(lines, key=lambda l: (0 if l.x0 < layout.width / 2 else 1, -l.y0, l.x0))
        l_idx = 0
        page_width = layout.width
        page_mid = page_width / 2

        while l_idx < len(lines):
            line = lines[l_idx]
            line_content = line.get_text().strip('\n')
            if not line_content:
                continue
            font_name, font_size = guess_font_info(line)
            # 融合下一行: 靠得近得，以及
            if l_idx < len(lines) - 1 and (next_line := lines[l_idx + 1]):
                if (
                        re.match(r'[A-Z]\.', line_content) and not re.search(r'[,.]$', line_content)
                ) or (abs(line.y0 - next_line.y1) / font_size <= 0.064):
                    # LTContainer.add(lines[l_idx], LTAnno('\t'))
                    if len(line._objs[0]) and isinstance(line._objs[0]._objs[-1], LTAnno):
                        line._objs[0]._objs.pop(-1)
                    lines[l_idx].extend(next_line)
                    lines.pop(l_idx + 1)
                    continue
            if font_name and 'MinionPro-Bold' in font_name:
                # 识别文档开始的code
                if int(font_size) == 9:
                    if page_mid / 2 < line.x0 < page_mid or (page_mid * 1.5) < line.x0 < page_width:
                        # 打印上一个文档
                        if current_doc is not None:
                            current_doc.add_content(current_section)
                            try:
                                current_doc.render(output_root)
                                pass
                            except BaseException as e:
                                logger.warning(f"error: {current_doc.title}, {e}")
                        # 新建文档
                        current_doc = Document(line_content)
                        current_section = None
                # 识别文档开始的大标题
                elif int(font_size) == 13:
                    current_doc.title = line_content.title()
                    current_section = Section(current_doc.title, "drug_info")
            elif current_doc is not None:
                if re.match(r'^[A-Z]+$', line_content):
                    if current_section is not None:
                        current_doc.add_content(current_section)
                    current_section = Section(line_content)
                elif current_section is not None:
                    if image := get_upper_nearest_image(images, line.x0, line.y0, page_mid):
                        current_section.add_content(Image(image))
                    current_section.add_content(Paragraph(line_content))
                else:
                    logger.warning(f"current_section is None:{current_doc}, {line}")
            l_idx += 1
            pass
        pass
    logger.info(f"finish processing {fp.name}")


if __name__ == '__main__':
    output_root = Path('html')
    file_path = r"drug_part_European Pharmacopoeia 10.0.pdf"
    extract_edqm(file_path, output_root=output_root)
    pass
