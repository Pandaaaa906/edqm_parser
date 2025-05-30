from base64 import b64encode
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
from typing import Optional, List, Union

from PIL import Image as PILImage
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pdfminer.layout import LTImage


ROOT = Path(__file__).parent

env = Environment(
    loader=FileSystemLoader(ROOT / 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


def is_paragraph(value):
    return isinstance(value, Paragraph)


def is_image(value):
    return isinstance(value, Image)


env.filters['is_paragraph'] = is_paragraph
env.filters['is_image'] = is_image


@dataclass
class Content:
    pass


@dataclass
class Paragraph(Content):
    content: str


class Image(Content):
    src: str

    def __init__(self, image: Union[LTImage, bytes]):
        if isinstance(image, LTImage):
            image = image.stream.rawdata
        try:
            img = PILImage.open(BytesIO(image))
        except Exception as e:
            return
        b = BytesIO()
        img.save(b, format='png')
        b.seek(0)
        self.src = f"data:image/png;base64,{b64encode(b.getvalue()).decode()}"


@dataclass
class Section:
    subtitle: str
    id: Optional[str] = None
    contents: List[Content] = field(default_factory=list)

    def add_content(self, content: Content):
        self.contents.append(content)


@dataclass
class Document:
    code: str
    title: Optional[str] = field(default="")
    contents: List[Section] = field(default_factory=list)

    def __post_init__(self):
        self.template = env.get_template('template_with_img.html')

    def add_content(self, content: Section):
        self.contents.append(content)

    @property
    def html(self):
        return self.template.render({"doc": self}).encode('u8')

    @property
    def normalized_title(self):
        return self.title.translate(str.maketrans('', '', '\n'))

    def render(self, root="html"):
        fname = f"{self.normalized_title}.html"
        root = Path(root)
        root.mkdir(exist_ok=True)
        fp = root / fname
        with fp.open('wb') as f:
            f.write(self.html)

