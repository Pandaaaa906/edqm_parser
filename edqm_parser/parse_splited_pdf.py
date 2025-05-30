from pathlib import Path

from loguru import logger

from .pdf_parser import extract_edqm


def parse_split_pdf(root: Path, output_root: Path):
    pdfs = root.glob('./*.pdf')
    for idx, pdf in enumerate(pdfs):
        extract_edqm(pdf, output_root=output_root)
        logger.info(f"processed file: {pdf.name}")


if __name__ == '__main__':
    root = Path('pdf')
    output_root = Path('html_split')
    parse_split_pdf(root, output_root)
