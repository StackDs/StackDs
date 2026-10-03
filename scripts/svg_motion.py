"""Static SVG variants selected by the host document's picture media queries."""

import xml.etree.ElementTree as ET

SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)


def static_svg(source, hide_classes=()):
    root = ET.fromstring(source)
    hidden = {"motion", *hide_classes}
    for parent in root.iter():
        for child in list(parent):
            if (child.tag.rsplit("}", 1)[-1] in {"animate", "animateTransform", "animateMotion", "set"}
                    or hidden.intersection(child.get("class", "").split())):
                parent.remove(child)
    style = ET.SubElement(root, f"{{{SVG}}}style", {"id": "static-motion"})
    style.text = "* { animation: none !important; } .typed-char { opacity: 1 !important; }"
    root.set("data-motion", "static")
    return ET.tostring(root, encoding="unicode") + "\n"
