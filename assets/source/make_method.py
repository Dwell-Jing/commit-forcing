#!/usr/bin/env python3
"""Render the committing computation for current + immediately preceding block.

The adopted computation layout, native data glyphs, and operators are retained.
Denoising uses the base history policy. Committing receives the clean current
block and KV of the immediately preceding block; other stored history is not
directly read during committing. Three slabs and front grids are schematic,
not counts of latent frames or layers. --draft reviews lighter fills only.
"""
from pathlib import Path
from html import escape
import argparse
import os
import copy
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from paper_palette import (INK, MUTED, RULE, NONRECENT as SINK,
                           NONRECENT_LIGHT as SINK_LIGHT,
                           BLUE as RECENT, BLUE_LIGHT as RECENT_LIGHT,
                           ACCENT, ACCENT_LIGHT, TENSOR_FILL, LATENT_FILL,
                           COMMIT_FILL, WINDOW_CURRENT_FILL, GRID_RULE)

ROOT=Path(__file__).resolve().parents[2]
UPPER=ROOT/'assets/source/method_upper.svg'
parser=argparse.ArgumentParser()
parser.add_argument('--draft',action='store_true')
args=parser.parse_args()
FIG=Path(os.environ.get('FIGURE_OUTPUT_DIR', ROOT/'assets/drafts' if args.draft else ROOT/'assets'))
PRE=FIG
STEM='method_draft' if args.draft else 'method'
W,H=2200,460
WIDTH_MM=178
NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)

base=ET.parse(UPPER).getroot()
upper=copy.deepcopy(base.find(f'{{{NS}}}g'))
upper.set('id','method-computation')
upper.set('transform','translate(0 -32)')
palette_map = {'#607C68': SINK, '#DCE8DF': SINK_LIGHT,
               '#557F9C': RECENT, '#D7E6F0': RECENT_LIGHT,
               '#F0D4C7': ACCENT_LIGHT, '#AD5036': ACCENT}
if args.draft:
    # Review the Figure1-matched lighter fills without replacing the adopted PDF.
    palette_map.update({'#F4F6F7':'white', '#FCF6F2':COMMIT_FILL,
                        '#AEB8BE':RULE})

def apply_palette(element):
    for node in element.iter():
        for attribute in ('fill', 'stroke'):
            value = node.attrib.get(attribute)
            if value in palette_map:
                node.set(attribute, palette_map[value])

apply_palette(upper)
# The generated clean latent uses the same blue type color as Figure 1.
# Map the archived clean-latent colors before the approved native rebuild.
for node in upper.iter():
    if (node.tag == f'{{{NS}}}rect' and node.attrib.get('x') == '773'
            and node.attrib.get('width') == '136'):
        node.set('fill', RECENT_LIGHT)
        node.set('stroke', RECENT)
    elif (node.tag == f'{{{NS}}}path'
          and node.attrib.get('d', '').startswith(('M818.333', 'M863.666', 'M773 '))):
        node.set('stroke', RECENT)
removed=[]
for child in list(upper):
    if child.tag!=f'{{{NS}}}text':
        continue
    label=''.join(child.itertext())
    if label in {'(a) One generated block','sink / memory / replay','Noisy','block','Previous cache'}:
        removed.append(label)
        upper.remove(child)
        continue
    if label=='Nonrecent sources':
        child.text='Nonrecent'
        child.set('font-size','40')
        if float(child.attrib['x'])>1000:
            child.set('x','1185')
    elif label=='Recent' and float(child.attrib.get('x','0'))>1000:
        child.text='Previous block'
        child.set('x','1425')
    elif label=='Base denoising':
        child.text='Denoising'
    elif label=='Clean':
        child.text='Clean block'
        child.set('fill', RECENT)
    if float(child.attrib.get('font-size','38'))<38:
        child.set('font-size','38')
    if args.draft and label in {'Clean','New KV'}:
        child.set('fill', INK)

defs=copy.deepcopy(base.find(f'{{{NS}}}defs'))
apply_palette(defs)
pattern=defs.find(f"{{{NS}}}pattern[@id='blocked-hatch']")
for child in pattern:
    if child.tag==f'{{{NS}}}rect':
        child.set('fill','#FAFBFC')
    elif child.tag==f'{{{NS}}}path':
        child.set('stroke',RULE if args.draft else '#CBD4DB')
        child.set('stroke-width','1.6')

from method_glyphs import build_upper_draft
upper,glyph_records,upper_contract=build_upper_draft(upper,defs,{
    'ink':INK,'muted':MUTED,'rule':RULE,
    'nonrecent':SINK,'nonrecent_light':TENSOR_FILL if args.draft else SINK_LIGHT,
    'recent':RECENT,'recent_light':LATENT_FILL if args.draft else RECENT_LIGHT,
    'accent':ACCENT,'accent_light':TENSOR_FILL if args.draft else ACCENT_LIGHT})

svg=[f'<svg xmlns="{NS}" width="{WIDTH_MM}mm" height="{WIDTH_MM*H/W:.6f}mm" viewBox="0 0 {W} {H}">',
 '<title>Commit Forcing: current and previous block</title>',
 '<desc>The base denoising policy uses historical KV to generate the clean current block. Committing at t=0 receives that clean current block and the immediately preceding block through its KV. The nonrecent source, including sink KV and any earlier memory, remains stored and available under the base denoising policy but has no direct committing access. Separate old-cache and new-KV inputs feed the unchanged base update. Three-slab stacks and front grids are schematic and count neither latent frames nor layers. The current and immediately preceding blocks each contain three latent frames, making the committing context six latent frames once a previous block exists; the first block commits using current only. Falling diagonal strokes fade across denoising states to denote symbolic noise, not a measured magnitude. No extra model forward, new cache allocation, or eviction operation is introduced.</desc>',
 ET.tostring(defs,encoding='unicode'),f'<rect width="{W}" height="{H}" fill="white"/>',
 ET.tostring(upper,encoding='unicode'),'</svg>']

FIG.mkdir(parents=True,exist_ok=True)
PRE.mkdir(parents=True,exist_ok=True)
tmp_svg=FIG/f'.{STEM}.render.svg'
tmp_pdf=FIG/f'.{STEM}.render.pdf'
tmp_png=PRE/f'.{STEM}.render.png'
tmp_svg.write_text('\n'.join(svg)+'\n')
try:
    subprocess.run(['rsvg-convert','-f','pdf','-o',str(tmp_pdf),str(tmp_svg)],check=True)
    subprocess.run(['pdftoppm','-singlefile','-png','-scale-to','2200',str(tmp_pdf),str(PRE/f'.{STEM}.render')],check=True)
    tmp_svg.replace(FIG/f'{STEM}.svg')
    tmp_pdf.replace(FIG/f'{STEM}.pdf')
    tmp_png.replace(PRE/f'{STEM}.png')
finally:
    for p in (tmp_svg,tmp_pdf,tmp_png):
        p.unlink(missing_ok=True)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

manifest={
  'artifact':STEM,
  'method_name':'Commit Forcing',
  'source_overleaf_commit':'3824b58e861e33406f041e17ac884f285d0c9330',
  'status':('Independent fill review of the adopted current-plus-previous rule' if args.draft else 'Canonical Figure4; current-plus-previous committing'),
  'source':'assets/source/make_method.py','source_sha256':sha(Path(__file__).resolve()),
  'physical_size_mm':[WIDTH_MM,WIDTH_MM*H/W],
  'minimum_font_points_at_178mm':38*WIDTH_MM/W*72/25.4,
  'minimum_font_points_at_168mm':38*168/W*72/25.4,
  'upper_computation':{'asset':'assets/source/method_upper.svg','asset_sha256':sha(UPPER),
    'operators_arrows_and_tensor_geometry_preserved':True,
    'label_change':'Committing-side Recent becomes Previous block; denoising Recent is retained',
    'representation':'Native three-slab stacks with one 4:3 front grid; operators and connections preserved',
    'helper':'assets/source/method_glyphs.py',
    'helper_sha256':sha(ROOT/'assets/source/method_glyphs.py'),
    'glyph_contract':upper_contract,'glyphs':glyph_records,
    'flow':'Base denoising -> current clean block -> committing t0 -> new KV -> base cache update -> next block',
    'current_and_history_inputs_separate':True,
    'old_cache_and_new_kv_inputs_separate':True},
  'committing_context':{'current_blocks':1,'historical_blocks':1,
    'historical_selection':'Immediately preceding block in the original generated trajectory',
    'latent_frames_per_block':3,'total_latent_frames':6,
    'first_block_uses_current_only':True,
    'nonrecent_directly_accessed':False,
    'base_denoising_policy_preserved':True,
    'base_cache_update_preserved':True},
  'scientific_boundaries':[
    'The method uses current plus immediately preceding block, not a choice among window options',
    'History outside that direct committing context remains stored under the base policy',
    'Indirect history through the generated current block or previous KV is retained',
    'The first block uses the current block only',
    'No new model forward, memory-eviction algorithm, or inference cache is introduced',
    'Stacks and front grids count neither latent frames nor network layers; Clean block remains latent'],
  'caption_handoff':'Committing constructs new KV from the clean current block and KV of the immediately preceding block at t=0. Denoising and cache update follow the base generator. The current and previous blocks each contain three latent frames; when no previous block exists, committing uses current only. Other stored history, including sink KV, remains available under the base denoising policy but is excluded from direct committing access. Stacks and grids are schematic and count neither frames nor layers.',
  'window_options_removed':True,
  'lettered_panel_labels':False,
  'export_sha256':{'svg':sha(FIG/f'{STEM}.svg'),'pdf':sha(FIG/f'{STEM}.pdf'),
    'actual_pdf_png':sha(PRE/f'{STEM}.png')},
}
(FIG/f'{STEM}.provenance.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(f'Created {STEM}: preserved computation with current-plus-previous committing')
