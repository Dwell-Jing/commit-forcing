"""Native data glyphs for the independent Figure 4 upper-flow draft.

The three slabs and 3-by-3 front grid are a shared schematic grammar. They
encode neither network layers nor latent-frame counts; a clean latent remains
a latent, even though historical and new KV use the same drawing grammar.
"""

from collections import Counter
import copy
import hashlib
import json
import re
import xml.etree.ElementTree as ET


NS = "http://www.w3.org/2000/svg"
_Q = "{" + NS + "}"
_SOURCE_IDS = {
    "nonrecent-denoising", "recent-denoising",
    "nonrecent-committing", "recent-committing",
}
_BOXES = {
    (235.0, 254.0, 455.0, 126.0): "denoising",
    (1105.0, 254.0, 350.0, 126.0): "committing",
    (1840.0, 131.0, 270.0, 90.0): "previous-cache-container",
    (1785.0, 259.0, 365.0, 126.0): "cache-update",
    (1833.0, 420.0, 275.0, 40.0): "next-block-output",
}
_GRID_ZONES = (
    (773.0, 277.0, 909.0, 349.0),
    (1560.0, 267.0, 1698.0, 367.0),
    (1857.0, 151.0, 2097.0, 209.0),
    (1803.0, 317.0, 2120.0, 375.0),
)


def _number(value):
    return format(float(value), ".12g")


def _element(parent, tag, **attributes):
    return ET.SubElement(parent, _Q + tag, {
        key.replace("_", "-"): str(value)
        for key, value in attributes.items()
    })


def _digest(elements):
    payload = [ET.tostring(element, encoding="unicode") for element in elements]
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False).encode()).hexdigest()


def _rect_geometry(element):
    return tuple(float(element.get(key, 0)) for key in ("x", "y", "width", "height"))


def _is_old_grid(element):
    # Connector markers always take precedence over any coordinate filter.
    if any(key.startswith("marker-") for key in element.attrib):
        return False
    if float(element.get("stroke-width", 0)) not in (1.0, 1.3):
        return False
    values = [float(value) for value in re.findall(
        r"[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?", element.get("d", "")
    )]
    if not values or len(values) % 2:
        return False
    points = tuple(zip(values[::2], values[1::2]))
    return any(all(x0 - 1e-6 <= x <= x1 + 1e-6 and y0 - 1e-6 <= y <= y1 + 1e-6
                   for x, y in points)
               for x0, y0, x1, y1 in _GRID_ZONES)


def _install_noise_pattern(defs, muted):
    pattern = defs.find(f"{_Q}pattern[@id='draft-noise-hatch']")
    if pattern is None:
        pattern = _element(defs, "pattern", id="draft-noise-hatch")
    pattern.clear()
    pattern.attrib.update({"id": "draft-noise-hatch", "width": "8", "height": "8",
                           "patternUnits": "userSpaceOnUse"})
    # Falling diagonals distinguish noise from the rising exclusion hatch.
    _element(pattern, "path", d="M0 0 L8 8 M-4 4 L4 12 M4 -4 L12 4",
             fill="none", stroke=muted, stroke_width="1.7")


def _glyph(parent, name, role, content_kind, x, y, width, height,
           stroke, fill, noise_opacity=None):
    if abs(width / height - 4 / 3) > 1e-12:
        raise ValueError(f"Front face for {name} must be 4:3")
    step = width * .055
    group = _element(parent, "g", id=f"draft-glyph-{name}",
                     **{"class": "draft-data-glyph", "data-role": role,
                        "data-content-kind": content_kind, "data-slab-count": "3",
                        "data-front-aspect-ratio": "4:3", "data-grid": "3x3",
                        "data-slab-count-is-symbolic": "true"})
    # Far-to-near order exposes two ungridded slabs behind one full front face.
    for depth in (2, 1, 0):
        _element(group, "rect", x=_number(x + depth * step),
                 y=_number(y - depth * step), width=_number(width),
                 height=_number(height), fill=fill, stroke=stroke,
                 stroke_width="2", **{"class": "glyph-slab",
                                     "data-depth": depth,
                                     "data-front": str(depth == 0).lower()})
    if noise_opacity is not None:
        _element(group, "rect", x=_number(x), y=_number(y), width=_number(width),
                 height=_number(height), fill="url(#draft-noise-hatch)",
                 stroke="none", opacity=_number(noise_opacity),
                 **{"class": "glyph-noise-overlay"})
    for position in (1, 2):
        gx = x + width * position / 3
        gy = y + height * position / 3
        _element(group, "path", d=f"M{_number(gx)} {_number(y)} V{_number(y + height)}",
                 fill="none", stroke=stroke, stroke_width="1.1",
                 **{"class": "glyph-front-grid"})
        _element(group, "path", d=f"M{_number(x)} {_number(gy)} H{_number(x + width)}",
                 fill="none", stroke=stroke, stroke_width="1.1",
                 **{"class": "glyph-front-grid"})
    return {
        "id": group.get("id"), "role": role, "content_kind": content_kind,
        "front_rect": {"x": x, "y": y, "width": width, "height": height},
        "front_aspect_ratio": "4:3", "slab_count": 3, "slab_offset": step,
        "front_grid": [3, 3], "front_grid_count": 1,
        "back_slabs_gridded": False, "noise_opacity": noise_opacity,
        "noise_is_front_only": noise_opacity is not None,
        "stroke": stroke, "fill": fill, "transform": None,
    }


def build_upper_draft(existing_upper, defs, palette):
    """Return a copied upper group, glyph records, and preservation contract.

    ``existing_upper`` already has the adopted labels and global translation.
    Only ``defs`` is updated in place, to install the native diagonal-noise pattern.
    Processor boxes, connectors, the exclusion cross, and all text are retained
    as byte-identical element copies. This helper performs no file operations.
    """
    upper = copy.deepcopy(existing_upper)
    removed = Counter()
    retained = []
    for child in list(upper):
        tag = child.tag.removeprefix(_Q)
        remove = (tag == "g" and (child.get("id") in _SOURCE_IDS or
                  "denoising-noise-state" in child.get("class", "").split()))
        if tag == "rect":
            remove = _rect_geometry(child) not in _BOXES
        elif tag == "path":
            remove = _is_old_grid(child)
        if remove:
            removed[tag] += 1
            upper.remove(child)
        else:
            retained.append(child)
    expected = {"g": 8, "rect": 39, "path": 58}
    if dict(removed) != expected:
        raise ValueError(f"Upper source changed: expected data removals {expected}, got {dict(removed)}")
    retained_before = _digest(retained)
    labels_before = _digest([node for node in retained if node.tag == _Q + "text"])
    paths_before = _digest([node for node in retained if node.tag == _Q + "path"])
    boxes_before = _digest([node for node in retained if node.tag == _Q + "rect"])
    if any(node.get("transform") for node in retained):
        raise ValueError("Unexpected retained child transform; only the global translation is supported")
    _install_noise_pattern(defs, palette["muted"])

    records = []
    colors = {
        "nonrecent": (palette["nonrecent"], palette["nonrecent_light"]),
        "recent": (palette["recent"], palette["recent_light"]),
        "new": (palette["accent"], palette["accent_light"]),
        "noisy": (palette["muted"], "#F4F6F7"),
    }

    def add(name, role, kind, geometry, color, noise=None):
        stroke, fill = colors[color]
        records.append(_glyph(upper, name, role, kind, *geometry, stroke, fill, noise))

    for name, center, color in (
        ("nonrecent-denoising", 330, "nonrecent"),
        ("recent-denoising", 575, "recent"),
        ("nonrecent-committing", 1185, "nonrecent"),
        ("recent-committing", 1385, "recent"),
    ):
        add(name, name, "historical-kv", (center - 48, 141, 96, 72), color)
    add("noisy-input", "noisy-current-input", "noisy-latent", (30, 271, 112, 84), "noisy", 1)
    add("clean-latent", "clean-current-latent", "clean-latent-not-kv", (785, 271, 112, 84), "recent")
    add("new-kv", "new-committed-kv", "kv", (1573, 271, 112, 84), "new")
    for index, (x, opacity) in enumerate(zip((265, 375, 485, 595), (1, .65, .3, .06)), 1):
        add(f"denoising-state-{index}", "intermediate-denoising-state", "latent",
            (x, 325, 48, 36), "noisy", opacity)
    for index, (x, color) in enumerate(zip((1851, 1917, 1983, 2049),
                                          ("nonrecent", "recent", "recent", "recent")), 1):
        add(f"previous-cache-{index}", f"previous-cache-{color}", "historical-kv",
            (x, 160, 52, 39), color)
    for index, (x, color) in enumerate(zip((1803, 1887, 1971, 2055),
                                          ("nonrecent", "recent", "recent", "new")), 1):
        add(f"updated-cache-{index}", f"updated-cache-{color}", "kv",
            (x, 323, 64, 48), color)

    retained_after = [node for node in upper
                      if "draft-data-glyph" not in node.get("class", "").split()]
    if _digest(retained_after) != retained_before:
        raise AssertionError("A retained operator, connector, cross, or label changed")
    contract = {
        "glyph_count": len(records), "native_vector_primitives": True,
        "grammar": "Three slabs; exactly one 3-by-3 grid on the front slab; 4:3 front aspect",
        "slab_count_and_grid_are_symbolic": True,
        "slabs_encode_neither_layers_nor_latent_frames": True,
        "clean_latent_is_not_kv": True,
        "glyph_nonuniform_transforms": False,
        "global_upper_transform": upper.get("transform"),
        "noise_pattern": "draft-noise-hatch", "noise_overlay_front_only": True,
        "noise_texture": "Falling diagonals with opacity decreasing across denoising states",
        "noise_distinct_from_excluded_history_hatch": True,
        "removed_top_level_elements": dict(removed),
        "removed_top_level_element_count": sum(removed.values()),
        "retained_element_count": len(retained),
        "retained_element_sha256_before": retained_before,
        "retained_element_sha256_after": _digest(retained_after),
        "retained_elements_byte_identical": True,
        "all_labels_sha256": labels_before,
        "all_arrow_and_cross_paths_sha256": paths_before,
        "all_processor_and_container_boxes_sha256": boxes_before,
        "arrow_path_count": sum(node.tag == _Q + "path" and
                                node.get("marker-end") is not None for node in retained),
        "cross_path_count": sum(node.tag == _Q + "path" and
                                node.get("marker-end") is None for node in retained),
        "topology_unchanged": True,
        "current_and_historical_inputs_separate": True,
        "old_cache_and_new_kv_inputs_separate": True,
        "lower_access_masks_touched": False,
    }
    return upper, records, contract
