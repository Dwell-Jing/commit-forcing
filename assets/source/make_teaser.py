#!/usr/bin/env python3
"""Fig1: shared denoising roles and two committing contexts.

Layered tensor glyphs continue to authentic SGF examples; access masks belong to Figure 4.
The schematic is a policy overview, not a fixed-clean paired reconstruction.
"""
from pathlib import Path
import hashlib
import json
import math
import random
import os
from math import hypot

from teaser_drawing import Drawing, INK, MUTED, RULE, BLUE, ACCENT, ASSET, FRAME

ROOT = Path(__file__).resolve().parents[2]
STEM = 'teaser_draft'
FIG = Path(os.environ.get('FIGURE_OUTPUT_DIR', ROOT / 'assets'))
PREVIEW = FIG
W, H = 3200, 1500
FONT = 54
HISTORICAL_KV_LABEL = 'Historical KV'
PREVIOUS_KV_LABEL = 'Previous KV'
CLEAN_LABEL_DX = 16
# Exact native-shape coordinates from the user's 2026-10-21 PowerPoint edits.
# Brackets include the current clean input; unedited vertical arrows stay put.
COMMITTING_BRACKETS = {
    'nonrecent': 'M1059 315.2 V328.2 H2124.133333333333 V315.2',
    'recent': 'M1580 1035.2 V1043.2 H2122 V1035.2',
}
RESULT_ARROWS = {
    'nonrecent': (
        'M2477.8 500.000052104598 L2532 500.000052104598 '
        'M2513.9333333333334 504.46666666666664 L2532 500.000052104598 '
        'L2513.9333333333334 495.53333333333336'
    ),
    'recent': (
        'M2478.5333333333333 1222.0334091571888 L2532 1222.0334091571888 '
        'M2514.1777777777775 1228.5333333333333 L2532 1222.0334091571888 '
        'L2514.1777777777775 1215.5333333333333'
    ),
}



def _arrow(d, x1, y1, x2, y2, color=MUTED, width=2.6):
    """Thin straight connector with a small open head, confined to Fig1."""
    length = hypot(x2 - x1, y2 - y1)
    if not length:
        return
    ux, uy = (x2 - x1) / length, (y2 - y1) / length
    bx, by = x2 - 9 * ux, y2 - 9 * uy
    px, py = -4.5 * uy, 4.5 * ux
    d.items.append(
        f'<path class="open-arrow" d="M{x1} {y1} L{x2} {y2} '
        f'M{bx+px} {by+py} L{x2} {y2} L{bx-px} {by-py}" '
        f'fill="none" stroke="{color}" stroke-width="{width}" '
        'stroke-linecap="butt" stroke-linejoin="miter"/>'
    )

def line(d, path, color=INK, width=2.4, dash=None):
    extra = f' stroke-dasharray="{dash}"' if dash else ''
    d.items.append(f'<path d="{path}" fill="none" stroke="{color}" '
                   f'stroke-width="{width}" stroke-linecap="butt" '
                   f'stroke-linejoin="miter"{extra}/>')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def input_noise(d,x,y,width,height,ident):
    """Illustrative pure-noise latent; no scene or person is drawn beneath it."""
    pattern=f'pure-input-noise-{ident}'
    rng=random.Random(417)
    d.items.append(f'<defs><pattern id="{pattern}" width="48" height="48" '
                   'patternUnits="userSpaceOnUse">')
    # Coarser, lighter grain leaves the full-cell tensor grid readable in print.
    for row in range(6):
        for col in range(6):
            value=max(0,min(255,round(rng.gauss(194,27))))
            d.items.append(f'<rect x="{col*8}" y="{row*8}" width="8" height="8" '
                           f'fill="rgb({value},{value},{value})"/>')
    d.items.append('</pattern></defs>')
    d.items.append(f'<g id="noise-input-{ident}" data-content="pure-noise-no-scene" '
                   'data-is-measured-noise="false">')
    d.rect(x,y,width,height,'none',0,f'url(#{pattern})')
    d.items.append('</g>')


def current_grid(d,x,y,width,height,noisy,ident):
    """Flat tensor grid occupies a film cell; cells are symbolic, not frames."""
    d.items.append(f'<g id="current-grid-{ident}" data-type="current-latent" '
                   f'data-state="{"noise" if noisy else "clean"}" data-grid="5x3" '
                   'data-grid-count-is-symbolic="true">')
    if noisy:
        input_noise(d,x,y,width,height,ident)
    else:
        d.rect(x,y,width,height,'none',0,'#EDF3F6')
    color=INK if noisy else BLUE
    for col in range(1,5):
        xx=x+width*col/5
        line(d,f'M{xx} {y} V{y+height}',color,1.6)
    for row in range(1,3):
        yy=y+height*row/3
        line(d,f'M{x} {yy} H{x+width}',color,1.6)
    d.items.append('</g>')


def filmstrip(d,x,y,width,name,labels=False,masked_indices=(),noisy_current=False):
    """N / R / R / Current. Current is a live input, never stored history."""
    pad,gap,rail,current_gap=12,14,13,28
    cell=(width-2*pad-3*gap-current_gap)/4
    height=cell*240/416
    total=height+2*rail+10
    d.items.append(f'<g id="filmstrip-{name}" data-role="history-and-current-input-context" '
                   f'data-current-input-noisy="{str(noisy_current).lower()}">')
    # One continuous dark film base restores both end rails and the inter-frame
    # separators, rather than letting thumbnails float between only two rails.
    d.rect(x,y,width,total,MUTED,1.8,'#48545C')
    for ry in (y,y+total-rail):
        d.rect(x,ry,width,rail,'none',0,'#48545C')
    n=round(width/27); step=width/n
    for i in range(n):
        xx=x+step*(i+.5)-4
        for yy in (y+3,y+total-rail+3):
            d.items.append(f'<path class="film-direction" d="M{xx} {yy} l8 4 l-8 4 Z" '
                           'fill="#DDE3E7" opacity=".78"/>')
    for side,xx in (('left',x+3),('right',x+width-8)):
        for yy in range(round(y+rail+10),round(y+total-rail-5),20):
            d.items.append(f'<rect class="film-side-perforation" data-side="{side}" '
                           f'x="{xx}" y="{yy}" width="5" height="7" '
                           'fill="#DDE3E7" opacity=".78"/>')
    rects=[];roles=('nonrecent','recent','recent','current')
    for i,(role,scene) in enumerate(zip(roles,('initial','nearby','nearby','nearby'))):
        xx=x+pad+i*(cell+gap)+(current_gap if i==3 else 0)
        yy=y+rail+5
        color=MUTED if i==0 else ACCENT if i==3 else BLUE
        d.rect(xx-1,yy-1,cell+2,height+2,color,2.3 if i==3 else 1.8,'white')
        masked=i in set(masked_indices)
        if masked:d.items.append('<g opacity=".20">')
        if role=='current':
            current_grid(d,xx,yy,cell,height,noisy_current,name)
        else:
            scene_start=len(d.items)
            d.scene(scene,xx,yy,cell,height)
            for idx in range(scene_start,len(d.items)):
                for local in ('street','woman'):
                    d.items[idx]=d.items[idx].replace(f'id="{local}"',f'id="{name}-{i}-{local}"')
        if masked:d.items.append('</g>')
        if masked:
            clip=f'scene-hatch-{name}-{i}'
            d.items.append(f'<defs><clipPath id="{clip}"><rect x="{xx}" y="{yy}" '
                           f'width="{cell}" height="{height}"/></clipPath></defs>')
            d.items.append(f'<g data-texture="excluded-history" clip-path="url(#{clip})">')
            for off in range(-round(height),round(cell+height),18):
                line(d,f'M{xx+off} {yy+height} l{height} {-height}',RULE,1.5)
            d.items.append('</g>')
        rects.append([xx,yy,cell,height])
    d.items.append('</g>')
    if labels:
        history_center=(rects[0][0]+rects[2][0]+cell)/2
        d.text(history_center,y-50,HISTORICAL_KV_LABEL,FONT,MUTED,'middle')
        d.text(rects[3][0]+cell/2,y-50,'Noise',FONT,ACCENT,'middle')
    return {'id':name,'rect':[x,y,width,total],'cell_rects':rects,
            'roles':list(roles),'masked_indices':list(masked_indices),
            'noisy_current':noisy_current,'current_is_live_input_not_historical_KV':True,
            'current_rendering':'Flat noise-filled grid with no scene underneath' if noisy_current else 'Flat clean-latent grid, not a decoded image',
            'current_grid':[5,3],'current_depth_layers':0,
            'rails':True,'rail_motif':'Top/bottom direction triangles; perforated left/right end rails; dark frame dividers',
            'end_rails':True,'inter_frame_dividers':True,
            'cell_count_is_symbolic':True}


def selection_bracket(d,strip,recent_only=False):
    x,y,w,h=strip['rect'];cells=strip['cell_rects']
    x0=cells[1][0]-3 if recent_only else cells[0][0]-3
    x1=cells[2][0]+cells[2][2]+3
    yy=y+h+14;color=BLUE if recent_only else MUTED
    path=COMMITTING_BRACKETS.get(strip['id'],f'M{x0} {yy-7} V{yy} H{x1} V{yy-7}')
    line(d,path,color,2.5)
    return yy


def tensor(d,x,cy,width,label,color=BLUE,height=140,ident='clean-latent'):
    """Layered tensor glyph, not a literal model-layer/frame count."""
    slabs=[]
    d.items.append(f'<g id="tensor-{ident}" data-type="clean-latent" data-layer-count-is-symbolic="true">')
    for off,fill in [(14,'#FAFCFD'),(7,'#F5F9FB'),(0,'#EDF3F6')]:
        d.rect(x+off,cy-height/2-off,width,height,color,1.9,fill)
        slabs.append([x+off,cy-height/2-off,width,height])
    if label:d.text(x+width/2,cy+18,label,FONT,INK,'middle')
    d.items.append('</g>')
    return {'id':ident,'front_rect':[x,cy-height/2,width,height],
            'slabs':slabs,'label':label,'text_inside':bool(label),'slab_count_is_symbolic':True,
            'slabs_are_not_transformer_layers':True}


def photo(d,key,x,y,width=610):
    # Identical display framing for both authentic frames; PNG pixels stay intact.
    roi=[90,0,326,240]
    height=width*roi[3]/roi[2]
    d.rect(x-2,y-2,width+4,height+4,RULE,1.8,'white')
    d.items.append(f'<g id="real-SGF-{key}" data-role="recursive-rollout-example-not-direct-kv-decoding" '
                   'data-display-crop="90,0,326,240">')
    d.items.append(f'<svg x="{x}" y="{y}" width="{width}" height="{height}" '
                   'viewBox="90 0 326 240" preserveAspectRatio="xMidYMid meet" overflow="hidden">')
    d.photo(key,0,0,416,240)
    d.items.append('</svg></g>')
    return {'arm':key,'path':str(FRAME[key].relative_to(ROOT)),'sha256':sha(FRAME[key]),
            'display_rect':[x,y,width,height],'source_frame_size':[416,240],
            'display_crop_xywh':roi,'same_crop_for_both_arms':True,
            'pixels_repainted_or_generated':False,
            'crop_reason':'Fixed horizontal crop shared by both arms; no scene retouching.',
            'seconds':238,'prompt':0,'seed':0}


def clothing_callout(d,example):
    """Vector annotation only; preserve each embedded photograph and its crop."""
    x,y,width,height=example['display_rect']
    crop_x,crop_y,crop_width,crop_height=example['display_crop_xywh']
    scale=width/crop_width
    # Highlight the specific garment named in each annotation, avoiding the face.
    source_ellipse=([219,163,49,67] if example['arm']=='native' else [225,114,42,47])
    cx=x+(source_ellipse[0]-crop_x)*scale
    cy=y+(source_ellipse[1]-crop_y)*scale
    rx=source_ellipse[2]*scale; ry=source_ellipse[3]*scale
    d.items.append(f'<g id="clothing-callout-{example["arm"]}" '
                   'data-role="qualitative-clothing-annotation-not-a-measurement">')
    for color,stroke in [(INK,22),('#FFD23F',13)]:
        d.items.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" '
                       f'fill="none" stroke="{color}" stroke-width="{stroke}"/>')
    d.items.append('</g>')
    return {'arm':example['arm'],'annotation_kind':'circle only','label':None,'leader':False,
            'source_frame_ellipse_cx_cy_rx_ry':source_ellipse,
            'display_ellipse_cx_cy_rx_ry':[cx,cy,rx,ry],
            'stroke_color':'#FFD23F','stroke_width':13,'halo_color':INK,'halo_width':22,
            'vector_overlay_only':True,
            'source_image_and_crop_unchanged':True}


def trace(d,x,cy,width,height,profile,ident):
    """Source-colored irregular patches; geometry is an illustration only."""
    seed=int(hashlib.sha256(ident.encode('utf-8')).hexdigest()[:12],16)
    rng=random.Random(seed)
    profiles={
        'carried0':[(.43,.40,.17,.20),(.56,.56,.14,.17),(.35,.68,.09,.11)],
        'carried1':[(.25,.31,.105,.13),(.61,.29,.12,.14),
                    (.45,.54,.10,.13),(.72,.70,.09,.12),(.24,.75,.07,.08)],
        'carried2':[(.23,.26,.10,.12),(.52,.25,.09,.11),(.77,.40,.085,.10),
                    (.42,.55,.09,.12),(.22,.76,.08,.09),(.66,.75,.10,.10)]}
    clip=f'patch-clip-{ident}'
    d.items.append(f'<defs><clipPath id="{clip}"><rect x="{x+7}" y="{cy-height/2+7}" '
                   f'width="{width-14}" height="{height-14}"/></clipPath></defs>')
    d.items.append(f'<g id="trace-{ident}" data-layout="irregular-patches" '
                   f'data-profile="{profile}" data-quantitative="false" clip-path="url(#{clip})">')
    patches=[]
    for cx0,cy0,rx0,ry0 in profiles[profile]:
        cx=x+cx0*width; yy=cy-height/2+cy0*height
        rx=rx0*width; ry=ry0*height
        points=[]
        for i in range(14):
            angle=2*math.pi*i/14
            radial=rng.uniform(.80,1.17)
            points.append((cx+math.cos(angle)*rx*radial,
                           yy+math.sin(angle)*ry*radial))
        commands=[f'M{points[0][0]:.3f} {points[0][1]:.3f}']
        for i in range(len(points)):
            p0=points[(i-1)%len(points)]; p1=points[i]
            p2=points[(i+1)%len(points)]; p3=points[(i+2)%len(points)]
            c1=(p1[0]+(p2[0]-p0[0])/6,p1[1]+(p2[1]-p0[1])/6)
            c2=(p2[0]-(p3[0]-p1[0])/6,p2[1]-(p3[1]-p1[1])/6)
            commands.append(f'C{c1[0]:.3f} {c1[1]:.3f} {c2[0]:.3f} {c2[1]:.3f} {p2[0]:.3f} {p2[1]:.3f}')
        path=' '.join(commands)+' Z'
        d.items.append(f'<path class="source-dependent-patch" d="{path}" fill="{MUTED}" opacity=".90"/>')
        patches.append({'normalized_ellipse':[cx0,cy0,rx0,ry0],
                        'control_points':points,'svg_path':path})
    d.items.append('</g>')
    return {'id':ident,'illustration_seed':seed,'profile':profile,
            'patches':patches,'color':MUTED,'color_matches_nonrecent':True,
            'shape_area_or_count_is_measurement':False,'no_dot_lattice':True,
            'no_triangle_or_band':True,'clipped_inside_kv_glyph':True}


def new_kv(d,arm,x,cy,stage,marked):
    width,height=220,128
    ident=f'{arm}-{stage}'
    d.items.append(f'<g id="tensor-kv-{ident}" data-type="persistent-KV" data-layer-count-is-symbolic="true">')
    slabs=[]
    for off,fill in [(14,'#FDFAF8'),(7,'#FCF7F3'),(0,'#FAFBFC')]:
        d.rect(x+off,cy-height/2-off,width,height,ACCENT,1.9,fill)
        slabs.append([x+off,cy-height/2-off,width,height])
    d.items.append('<g class="kv-front-grid" data-grid="5x3" data-grid-count-is-symbolic="true">')
    top=cy-height/2
    grid_bottom=cy+height/2
    for col in range(1,5):
        xx=x+width*col/5
        line(d,f'M{xx} {top} V{grid_bottom}',ACCENT,1.5)
    row_lines=(top+height/3,top+height*2/3)
    for yy in row_lines:
        line(d,f'M{x} {yy} H{x+width}',ACCENT,1.5)
    d.items.append('</g>')
    # Marks carry the source-dependency cue across newly constructed KV.
    # They are neither a measured quantity nor a monotone growth curve.
    field_height=96
    field_center=cy
    overlay=trace(d,x+9,field_center,width-18,field_height,f'carried{stage}',ident) if marked else None
    if stage==0:
        # The label hugs the front face below; the whole face remains gridded.
        d.text(x+width/2,cy+height/2+46,'New KV',FONT,INK,'middle')
    d.items.append('</g>')
    return {'arm':arm,'stage_index_is_schematic':stage,'front_rect':[x,cy-height/2,width,height],
            'slabs':slabs,'slab_count_is_symbolic':True,'text_inside':False,
            'label_position':'Immediately below the first front face' if stage==0 else None,
            'front_grid':[5,3],'grid_count_is_symbolic':True,
            'first_glyph_has_merged_label_cell':False,'overlay':overlay,
            'blank_means':'No depicted direct influence from additional older-history reads during committing; not zero-valued KV or zero total drift',
            'marks_mean':'Illustrative source-dependent influence carried through subsequent committing; not area-coded data'}


def main(draft=True):
    stem = 'teaser'
    figure_dir = FIG
    preview_dir = PREVIEW
    d=Drawing(W,H,'Committing historical dependencies into persistent KV')
    shared=filmstrip(d,40,400,960,'denoising',labels=True,noisy_current=True)
    strips=[shared]
    sy=selection_bracket(d,shared)
    _arrow(d,520,sy+14,520,670,INK,2.7)
    # Current noisy input is distinct from the three historical thumbnails.
    cur=shared['cell_rects'][3]
    _arrow(d,cur[0]+cur[2]/2,shared['rect'][1]+shared['rect'][3]+20,710,750,ACCENT,2.5)
    d.rect(350,690,340,120,INK,2,'white')
    d.text(520,773,'Denoising',FONT,INK,'middle')
    _arrow(d,520,830,520,900,INK,2.7)
    clean=tensor(d,360,1000,320,'Clean block')
    line(d,'M715 1000 H1040 M1040 500 V1220',INK,2.7)
    _arrow(d,1040,500,1250,500,INK,2.7)
    _arrow(d,1040,1220,1250,1220,INK,2.7)

    sequences=[];examples=[];callouts=[]
    # Each authentic frame spans from its branch's film top to the KV bottom.
    # Preserve the same source crop and aspect ratio in both branches.
    photo_height=434
    photo_width=photo_height*326/240
    positions=(1660,1940,2220)
    for name,cy,fy,off,key in [
            ('nonrecent',500,130,(),'native'),
            ('recent',1220,850,(0,1),'commit')]:
        strip=filmstrip(d,1050,fy,1080,name,masked_indices=off)
        strips.append(strip)
        recent_center=strip['cell_rects'][2][0]+strip['cell_rects'][2][2]/2
        history_label = HISTORICAL_KV_LABEL if name=='nonrecent' else PREVIOUS_KV_LABEL
        d.text(1450 if name=='nonrecent' else recent_center,fy-45,
               history_label,FONT,INK,'middle')
        current=strip['cell_rects'][3]
        d.text(current[0]+current[2]/2+CLEAN_LABEL_DX,fy-45,'Clean block',FONT,ACCENT,'middle')
        by=selection_bracket(d,strip,name=='recent')
        _arrow(d,1450 if name=='nonrecent' else recent_center,by+10,1450,cy-85,
               BLUE if name=='recent' else MUTED,2.7)
        d.rect(1280,cy-65,340,130,ACCENT,2,'#FCF9F6')
        d.text(1450,cy+17,'Committing',FONT,ACCENT,'middle')
        _arrow(d,1624,cy,1655,cy,ACCENT,3.1)
        blocks=[]
        for stage,x in enumerate(positions):
            blocks.append(new_kv(d,name,x,cy,stage,name=='nonrecent'))
            if stage<len(positions)-1:
                _arrow(d,x+240,cy,positions[stage+1]-6,cy,INK,3.1)
        d.items.append(f'<path class="open-arrow" d="{RESULT_ARROWS[name]}" '
                       f'fill="none" stroke="{INK}" stroke-width="3.1" '
                       'stroke-linecap="butt" stroke-linejoin="miter"/>')
        py=fy
        example=photo(d,key,2540,py,photo_width)
        examples.append(example)
        callouts.append(clothing_callout(d,example))
        sequences.append({'arm':name,'blocks':blocks,
                          'interpretation':'Repeated construction of later KV, not survival of the original entry',
                          'glyph_count_or_spacing_is_time_data':False})
    for i,item in enumerate(d.items):
        item=item.replace('Helvetica, Arial, sans-serif','Helvetica')
        if '<text ' in item:
            item=item.replace('font-weight="bold"','font-weight="normal"')
            if 'font-family=' not in item:item=item.replace('<text ','<text font-family="Helvetica" ',1)
        d.items[i]=item
    d.export(stem,figure_dir,preview_dir)

    source_record=json.loads((ASSET/'source.json').read_text())
    manifest={
        'artifact':stem, 'status':'Adopted Figure1; actual current-plus-previous six-frame SGF example',
        'source':'assets/source/make_teaser.py','source_sha256':sha(Path(__file__).resolve()),
        'method_name':'Commit Forcing','canvas':[W,H],
        'photo_source_overleaf_commit':source_record['source_overleaf_commit'],
        'manuscript_asset':{'version':'2026-10-30 manuscript assets','source':'figures/opening_teaser.svg','source_svg_sha256':'f3754e6988a567da4ecc831df68555cd1b0f33ec15328470169ca42092830d19'},
        'print_width_mm':178,'minimum_font_pt':FONT/W*178/25.4*72,
        'layout_anchors':source_record['layout_anchors'],
        'clean_latent':clean,'filmstrips':strips,'kv_sequences':sequences,
        'real_examples':examples,'clothing_callouts':callouts,
        'semantics':source_record['semantics'],
        'source_frames_unchanged':True,
        'exports':{ext:sha(figure_dir/f'{stem}.{ext}') for ext in ['pdf','svg']}}
    (figure_dir/f'{stem}.provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(str(preview_dir/f'{stem}.png'))

if __name__=='__main__':
    main(draft=False)
