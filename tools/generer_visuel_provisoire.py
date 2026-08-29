#!/usr/bin/env python3
"""Genere un visuel PROVISOIRE a la charte, aux dimensions d'un visuel de contenu.

Sert a eviter toute image cassee en production tant que le visuel definitif
n'est pas produit. Le marquage « visuel provisoire » est visible sur l'image
elle-meme, pour qu'aucun provisoire ne passe inapercu.

Usage :
  python3 tools/generer_visuel_provisoire.py --slug mon-visuel --titre "Ce que|le visuel montrera"
"""
import argparse, base64, os, subprocess, sys, textwrap
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from optimiser_png import optimiser
from generer_couverture import police, echapper, SORTIE, RACINE, INK, AMBRE, CREME


def construire_svg(titre):
    lignes = [l.strip() for l in titre.split('|')] if '|' in titre else textwrap.wrap(titre, 26)
    taille, interligne = 54, 68
    O = 285
    haut = O + 315 - (len(lignes) * interligne) / 2 - 40

    t = ['<text x="80" y="%.1f" font-family="PlexMono" font-weight="500" font-size="24" '
         'fill="%s" letter-spacing="2">VISUEL PROVISOIRE</text>' % (haut, AMBRE)]
    for i, l in enumerate(lignes):
        t.append('<text x="80" y="%.1f" font-family="Fraunces" font-weight="600" font-size="%d" '
                 'fill="%s">%s</text>' % (haut + 58 + i * interligne, taille, CREME, echapper(l)))
    bas = haut + 58 + len(lignes) * interligne
    t.append('<rect x="80" y="%.1f" width="96" height="4" fill="%s"/>' % (bas + 4, AMBRE))
    t.append('<text x="80" y="%.1f" font-family="PlexSans" font-weight="400" font-size="22" '
             'fill="%s" fill-opacity="0.55">À remplacer par le visuel définitif</text>' % (bas + 52, CREME))

    return '''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1200" viewBox="0 0 1200 1200">
<defs><style>
@font-face{{font-family:'Fraunces';font-weight:600;src:url(data:font/ttf;base64,{f}) format('truetype');}}
@font-face{{font-family:'PlexSans';font-weight:400;src:url(data:font/ttf;base64,{s}) format('truetype');}}
@font-face{{font-family:'PlexMono';font-weight:500;src:url(data:font/ttf;base64,{m}) format('truetype');}}
</style></defs>
<rect width="1200" height="1200" fill="{ink}"/>
<rect x="40" y="{cadre_y}" width="1120" height="550" rx="14" fill="none" stroke="{ambre}" stroke-width="3" stroke-dasharray="14 12"/>
{textes}
</svg>'''.format(f=police('fraunces'), s=police('plexsans'), m=police('plexmono'),
                 ink=INK, ambre=AMBRE, cadre_y=O + 40, textes='\n'.join(t))


def rasteriser(svg, slug):
    os.makedirs(SORTIE, exist_ok=True)
    tmp = os.path.join(SORTIE, '.tmp-%s.svg' % slug)
    open(tmp, 'w', encoding='utf-8').write(svg)
    apercu = tmp + '.png'
    if os.path.exists(apercu):
        os.remove(apercu)
    subprocess.run(['qlmanage', '-t', '-s', '1200', '-o', SORTIE, tmp], capture_output=True)
    if not os.path.exists(apercu):
        sys.exit('qlmanage n a produit aucun apercu')
    final = os.path.join(SORTIE, slug + '.png')
    subprocess.run(['sips', '-c', '630', '1200', apercu, '--out', final], capture_output=True)
    os.remove(tmp); os.remove(apercu)
    avant = os.path.getsize(final)
    apres, n = optimiser(final)
    return os.path.relpath(final, RACINE), avant, apres


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--slug', required=True)
    ap.add_argument('--titre', required=True)
    a = ap.parse_args()
    chemin, avant, apres = rasteriser(construire_svg(a.titre), a.slug)
    print('%-56s %6d -> %6d octets' % (chemin, avant, apres))
