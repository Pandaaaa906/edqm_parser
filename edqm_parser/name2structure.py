from indigo import Indigo
from loguru import logger
from requests import Session
from models import Session as DBSession, Impurity


class ExtractStructure:
    base_url = 'https://cactus.nci.nih.gov/chemical/structure/{chemical_ids}/{format}'

    def __init__(self):
        self.session = Session()

    def extract(self, value, out_format='smiles'):
        r = self.session.get(self.base_url.format(chemical_ids=value, format=out_format))
        if r.status_code == 404:
            return
        return r.text


def extract_smiles_from_names():
    logger.info('starting')
    db = DBSession()
    es = ExtractStructure()
    ind = Indigo()
    chemicals = db.query(Impurity).filter(Impurity.smiles == None)
    for chem in chemicals:
        try:
            smiles = es.extract(chem.chemical_name)
            if not smiles:
                continue
            m = ind.loadMolecule(smiles)
            m.dearomatize()
            smiles, *_ = m.smiles().split()
        except BaseException as e:
            logger.warning(f'{chem.impurity_name} got error: {e}')
            continue
        db.query(Impurity).filter(
            Impurity.id == chem.id
        ).update({
            'smiles': smiles
        })
        db.commit()


if __name__ == '__main__':
    extract_smiles_from_names()
