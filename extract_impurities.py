import re
from pathlib import Path

from loguru import logger
from parsel import Selector

from models import Session, Impurity

root = Path('./html')
p = re.compile(r'(?P<index>[A-Z])\.\s*(?P<chemical_name>.+)[,.]')
p_synonym = re.compile(r'(?P<chemical_name>.+) \((?P<synonyms>[^()]+)\)$')


def main():
    logger.info('starting')

    db = Session()
    for f in root.glob('*.html'):
        html = Selector(f.open(encoding='u8').read())
        api_name = html.xpath('//head/title/text()').get()

        impurities = html.xpath('//div[@id="IMPURITIES"]/div/p/text()').getall()
        for impurity in impurities:
            if (m := p.match(impurity)) is None:
                logger.debug(f'{api_name}: got invalid impurity: {impurity}')
                continue
            raw_chemical_name = chemical_name = m["chemical_name"]
            synonyms = None
            if (m_synonym := p_synonym.search(raw_chemical_name)) is not None:
                chemical_name = m_synonym['chemical_name']
                synonyms = m_synonym['synonyms']
            d = {
                'reference': 'ep',
                'version': '10',
                'api_name': api_name,
                'impurity_name': f'{api_name} EP Impurity {m["index"]}',
                'raw_chemical_name': raw_chemical_name,
                'chemical_name': chemical_name,
                'synonyms': synonyms,
            }
            item = db.query(Impurity).filter(
                Impurity.reference == d['reference'],
                Impurity.version == d['version'],
                Impurity.api_name == d['api_name'],
                Impurity.impurity_name == d['impurity_name'],
            ).first()
            if item:
                db.query(Impurity).filter(Impurity.id == item.id).update(d)
            else:
                db.add(Impurity(**d))
            db.commit()

    logger.info('finished')


if __name__ == '__main__':
    main()
    pass
