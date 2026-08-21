from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from xml.etree.ElementTree import Element, ElementTree, SubElement


def write_xml(output_path: Path, headers: Sequence[str], rows: Iterable[Mapping[str, str]]) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    root = Element("rows")
    for row in rows:
        row_element = SubElement(root, "row")
        for header in headers:
            value_element = SubElement(row_element, header)
            value_element.text = row[header]

    ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    return path
