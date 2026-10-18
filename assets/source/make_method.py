#!/usr/bin/env python3
"""One method diagram: compact computation and finite committing windows.

The editable upper vector snapshot preserves the adopted computation layout.
Current clean input and selected historical KV enter committing separately;
old and new KV enter the unchanged base update separately. Lower blocks show
original trajectory ages, not a shared physical-cache layout. w includes the
current three frames.
"""
from pathlib import Path
from html import escape
import argparse
import copy
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
UPPER=ROOT/'assets/source/method_upper.svg'
parser=argparse.ArgumentParser()
parser.add_argument('--draft',action='store_true')
args=parser.parse_args()
FIG=ROOT/'assets/drafts' if args.draft else ROOT/'assets'
PRE=FIG
STEM='method_draft' if args.draft else 'method'
W,H=2200,1090
WIDTH_MM=178
INK,MUTED,RULE='#202B33','#67717A','#D8DDE0'
SINK,SINK_LIGHT='#607C68','#DCE8DF'
RECENT,RECENT_LIGHT='#557F9C','#D7E6F0'
ACCENT,ACCENT_LIGHT='#AD5036','#F0D4C7'
NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)

base=ET.parse(UPPER).getroot()
upper=copy.deepcopy(base.find(f'{{{NS}}}g'))
upper.set('id','method-computation')
upper.set('transform','translate(0 -32)')
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
    elif label=='Base denoising':
        child.text='Denoising'
    elif label=='Clean':
        child.text='Clean block'
    if float(child.attrib.get('font-size','38'))<38:
        child.set('font-size','38')

defs=copy.deepcopy(base.find(f'{{{NS}}}defs'))
pattern=defs.find(f"{{{NS}}}pattern[@id='blocked-hatch']")
for child in pattern:
    if child.tag==f'{{{NS}}}rect':
        child.set('fill','#FAFBFC')
    elif child.tag==f'{{{NS}}}path':
        child.set('stroke','#CBD4DB')
        child.set('stroke-width','1.6')

svg=[f'<svg xmlns="{NS}" width="{WIDTH_MM}mm" height="{WIDTH_MM*H/W:.6f}mm" viewBox="0 0 {W} {H}">',
 '<title>Commit Forcing: computation and a finite recent-context window</title>',
 '<desc>Panel a preserves base denoising. The current clean block and recent historical KV enter committing at t=0 through separate paths; nonrecent history is excluded from its direct reads. New KV and old cache enter the unchanged base cache update. Panel b shows generic alternative windows w12,w9,w6,w3 over original trajectory blocks b-3,b-2,b-1 and current b. Each temporal block has three latent frames. Filled recent blocks are directly accessed; hatched blocks remain stored but are outside the committing read set. Each bracket includes current. At w3 only current remains, the known self-only endpoint. The nonrecent column is categorical, not a frame count. No common physical-cache geometry, content-age classifier, new cache-update algorithm or extra forward is introduced.</desc>',
 ET.tostring(defs,encoding='unicode'),f'<rect width="{W}" height="{H}" fill="white"/>',
 ET.tostring(upper,encoding='unicode'),
 f'<g font-family="Helvetica, Arial, sans-serif" fill="{INK}">']


def text(x,y,label,size=40,color=INK,anchor='start',bold=False):
    svg.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{"bold" if bold else "normal"}">{escape(label)}</text>')


def math_text(x,y,label,size=40,color=INK,anchor='middle'):
    svg.append(f'<text x="{x}" y="{y}" font-family="Times New Roman, Times, serif" font-style="italic" font-size="{size}" fill="{color}" text-anchor="{anchor}">{escape(label)}</text>')


def rect(x,y,w,h,fill='white',stroke=RULE,width=2):
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')


def path(d,color=INK,width=2.7):
    svg.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>')


text(35,42,'(a)',40,bold=True)
path('M35 454 H2160',RULE,2)
text(35,510,'(b)',40,bold=True)

SOURCE_X,SOURCE_W=460,240
BLOCK_X=[810,1120,1430,1840]
BLOCK_W,CELL_H=270,62
text(SOURCE_X+SOURCE_W/2,600,'Nonrecent',40,SINK,'middle')
text((BLOCK_X[0]+BLOCK_X[2]+BLOCK_W)/2,544,'Recent',40,RECENT,'middle')
path(f'M{BLOCK_X[0]} 558 V568 H{BLOCK_X[2]+BLOCK_W} V558',RECENT,2.5)
text(BLOCK_X[3]+BLOCK_W/2,544,'Current',40,ACCENT,'middle')
for i,x in enumerate(BLOCK_X):
    math_text(x+BLOCK_W/2,600,'b' if i==3 else f'b−{3-i}',40,ACCENT if i==3 else RECENT)

window_records=[]
for row,w in enumerate((12,9,6,3)):
    y=625+117*row
    n_history=w-3
    n_blocks=n_history//3
    svg.append(f'<g class="committing-window" data-window="{w}" data-history-count="{n_history}" data-current-count="3">')
    if w==3:
        svg.append(f'<text x="35" y="{y+43}" font-size="40" fill="{ACCENT}"><tspan font-family="Times New Roman, Times, serif" font-style="italic">w = 3</tspan><tspan font-size="38"> · Self-only</tspan></text>')
    else:
        math_text(35,y+43,f'w = {w}',41,INK,'start')
    svg.append('<g class="nonrecent-access" data-access="false" data-source-is-categorical="true">')
    rect(SOURCE_X,y,SOURCE_W,CELL_H,'url(#blocked-hatch)','#A9B7C0',2)
    svg.append('</g>')
    for i,x in enumerate(BLOCK_X):
        current=i==3
        accessible=current or i>=3-n_blocks
        color=ACCENT if current else RECENT
        fill=ACCENT_LIGHT if current else RECENT_LIGHT
        stroke=color if accessible else '#A9B7C0'
        svg.append(f'<g class="block-access" data-source="{"current" if current else "recent"}" data-lag="{0 if current else 3-i}" data-access="{str(accessible).lower()}" data-latent-frames="3">')
        rect(x,y,BLOCK_W,CELL_H,fill if accessible else 'url(#blocked-hatch)',stroke,2)
        for frame in (1,2):
            path(f'M{x+BLOCK_W*frame/3} {y} V{y+CELL_H}',stroke,1.4)
        svg.append('</g>')
    first=BLOCK_X[3-n_blocks]
    last=BLOCK_X[-1]+BLOCK_W
    svg.append(f'<g class="window-bracket" data-first-lag="{n_blocks}" data-includes-current="true">')
    path(f'M{first} {y+76} V{y+88} H{last} V{y+76}',INK,2.8)
    svg.append('</g></g>')
    window_records.append({'window_w':w,'historical_frames_directly_accessed':n_history,
        'historical_blocks_directly_accessed':list(range(-n_blocks,0)),
        'current_frames_directly_accessed':3,'sink_and_nonrecent_directly_accessed':False,
        'known_self_only':w==3,'bracket_x':[first,last]})
svg.append('</g></svg>')

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


print(f'Created {STEM}: compact computation and recent windows')
