import re
from pathlib import Path

from loguru import logger
from lxml.etree import HTML
from more_itertools import first

root = Path(r'E:\PythonScripts\edqm_parser\html')
p = re.compile(r'(?P<suffix>[A-Z]).\s+(?P<sub>[^:]+:\s*)?(?P<name>.+)[,.]\n?')


def gen_name(api: str, text: str):
    synonyms = None
    m = p.search(text)
    if m is None:
        logger.error(f'Cant parse {api}: {text}')
        return None
    d = m.groupdict()
    chem_name = d['name']
    # replace '- ' to '-', ' -' to '-'
    chem_name = re.sub(r'\s?([\[-])\s?', lambda m: m.group(1), chem_name)
    if re.search(r'\s\([^)]+\)?$', chem_name):
        chem_name, synonyms = re.match(r'(.+?)\s\(([^)]+)\)', chem_name).groups()
    return f'{api} EP Impurity {d["suffix"]}', chem_name, synonyms


for fp in root.glob('./*html'):
    with fp.open(encoding='u8') as f:
        html = HTML(f.read())
        title = first(html.xpath('//title/text()'), '')
        title = re.sub(r'\s?([([])\s?', lambda m: m.group(1), title)
        t = html.xpath('//div[@id="IMPURITIES"]/div/p/text()')
        if not t:
            continue
        print(title)
        for text in t:
            if not re.match(r'[A-Z]\.\s', text):
                continue
            print(gen_name(title, text))
        pass

if __name__ == '__main__':
    pass
