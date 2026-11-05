"""Localize 2008--2016 SVG annotations without modifying any plotted geometry.

Requires matplotlib, lxml and the Noto Sans CJK SC font.  Already outlined
Matplotlib labels are re-outlined with Chinese glyphs; merely changing an SVG
comment would leave its English drawing untouched.  Running twice is safe.
"""
from pathlib import Path
import re
import html
from lxml import etree as ET
from matplotlib.font_manager import FontProperties, findfont
from matplotlib.textpath import TextPath
from matplotlib.transforms import Affine2D
from matplotlib.path import Path as MplPath

ROOT = Path(__file__).resolve().parents[1]
SVG = "http://www.w3.org/2000/svg"
FONT = FontProperties(fname=findfont(FontProperties(family="Noto Sans CJK SC")))


def chinese(label):
    label = label.replace("$\\omega$ (rad/s)", "角频率 ω（弧度/秒）")
    label = label.replace("ω (rad/s)", "角频率 ω（弧度/秒）")
    label = label.replace("相位 (rad)", "相位（弧度）")
    label = label.replace("(rad/sample)", "（弧度/采样点）")
    label = label.replace("(rad/s)", "（弧度/秒）")
    label = label.replace("(rad)", "（弧度）")
    label = label.replace("Re(s)", "实部(s)").replace("Re(z)", "实部(z)")
    label = label.replace("Im(s)", "虚部(s)").replace("Im(z)", "虚部(z)")
    label = re.sub(r"\bRe ([sz])\b", r"实部 \1", label)
    label = re.sub(r"\bIm ([sz])\b", r"虚部 \1", label)
    label = label.replace("ROC", "收敛域")
    label = label.replace("Hz", "赫兹")
    label = label.replace("arg c_k", "相位 c_k").replace("arg H", "相位 H")
    return label


def svg_path(path):
    commands = []
    for vertices, code in path.iter_segments(curves=True, simplify=False):
        coords = " ".join(f"{v:.6f}".rstrip("0").rstrip(".") for v in vertices)
        command = {MplPath.MOVETO: "M", MplPath.LINETO: "L",
                   MplPath.CURVE3: "Q", MplPath.CURVE4: "C"}.get(code)
        commands.append("Z" if code == MplPath.CLOSEPOLY else command + coords)
    return " ".join(commands)


def outlined_label(group, comment, new_label):
    # Matplotlib places each text run with one immediate g transform.  Its
    # final scale maps 100-point glyph paths to the desired point size.
    old_label = html.unescape(comment.text.strip())
    transform_group = next((c for c in group if isinstance(c.tag, str)
                            and c.tag == f"{{{SVG}}}g" and c.get("transform")), None)
    if transform_group is None:
        return False
    transform = transform_group.get("transform")
    scale = re.search(r"\s*scale\(([-.\d]+)\s+([-.\d]+)\)\s*$", transform)
    if scale:
        size = abs(float(scale[1])) * 100
        transform = transform[:scale.start()]
    else:
        styled = " ".join(c.get("style", "") for c in transform_group.iter())
        sizes = re.findall(r"font-size:\s*([.\d]+)px", styled)
        if not sizes:
            raise ValueError("Cannot determine font size: " + old_label)
        size = max(map(float, sizes))
    old_path = TextPath((0, 0), old_label, size=size, prop=FONT)
    new_path = TextPath((0, 0), new_label, size=size, prop=FONT)
    # Keep the original text's centre and orientation, not its left edge.
    old_box = old_path.get_extents()
    new_box = new_path.get_extents()
    shift = (old_box.x0 + old_box.x1 - new_box.x0 - new_box.x1) / 2
    new_path = Affine2D().translate(shift, 0).transform_path(new_path)
    # Other labels may reference glyphs first declared inside this label.
    # Preserve those shared definitions before replacing its visible paths.
    root = group.getroottree().getroot()
    shared_defs = next((c for c in root if isinstance(c.tag, str)
                        and c.tag == f"{{{SVG}}}defs"), None)
    if shared_defs is None:
        shared_defs = ET.SubElement(root, f"{{{SVG}}}defs")
    for definitions in group.xpath(".//*[local-name()='defs']"):
        for definition in list(definitions):
            definitions.remove(definition)
            shared_defs.append(definition)
    for child in list(group):
        group.remove(child)
    group.append(ET.Comment(" " + new_label + " "))
    new_group = ET.SubElement(group, f"{{{SVG}}}g", transform=transform + " scale(1 -1)")
    ET.SubElement(new_group, f"{{{SVG}}}path", d=svg_path(new_path), fill="#243a3b")
    return True


changed = []
for file in sorted((ROOT / "content/assets").glob("20*.svg")):
    if not 2008 <= int(file.name[:4]) <= 2016:
        continue
    tree = ET.parse(str(file), ET.XMLParser(remove_comments=False))
    root = tree.getroot()
    edits = 0
    # Handle outlined or mathtext labels as a whole before plain text nodes.
    for group in root.xpath("//*[local-name()='g' and starts-with(@id,'text_')]"):
        comment = next((c for c in group if isinstance(c, ET._Comment)), None)
        if comment is not None and comment.text:
            original_label = html.unescape(comment.text.strip())
            replacement = chinese(original_label)
            if replacement != original_label:
                edits += outlined_label(group, comment, replacement)
    for node in root.xpath("//*[local-name()='text']"):
        if len(node) or not node.text:
            continue
        replacement = chinese(node.text)
        if replacement != node.text:
            node.text = replacement
            style = re.sub(r"font-family:\s*[^;]+;?", "", node.get("style", ""))
            node.set("style", style + ";font-family:'Noto Sans CJK SC','Microsoft YaHei',sans-serif")
            edits += 1
    if edits:
        tree.write(str(file), encoding="utf-8", xml_declaration=True)
        changed.append((file.name, edits))

for name, count in changed:
    print(name, count)
print("Changed", len(changed), "of 46 early-year SVG assets.")
