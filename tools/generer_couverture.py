#!/usr/bin/env python3
"""Genere la couverture d'un article de blog : PNG 1200x630 + vignette 600x315.

Methode : un SVG est compose avec les polices de la charte incorporees en
data URI, rasterise par qlmanage (QuickLook, fourni avec macOS) puis recadre
par sips. Le resultat est reencode en palette indexee pour alleger le poids.

Usage :
  python3 tools/generer_couverture.py \
      --slug compte-amazon-bloque-que-faire \
      --categorie "Compte suspendu" \
      --titre "Compte Amazon|bloque, que faire" \
      --motif cadenas-souleve

Le caractere | force un retour a la ligne dans le titre. Sans lui, le texte
est reparti automatiquement. Motifs disponibles : voir MOTIFS.
"""
import argparse, base64, os, subprocess, sys, textwrap
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from optimiser_png import optimiser

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.fonts')
SORTIE = os.path.join(RACINE, 'images', 'blog')

INK, AMBRE, CREME = '#16233B', '#C97A2E', '#F6F4EF'

POLICES = {
    'fraunces': 'https://fonts.googleapis.com/css2?family=Fraunces:wght@600',
    'plexsans': 'https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400',
    'plexmono': 'https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500',
}

# Chaque motif est dessine dans un repere local de 100x100 unites.
MOTIFS = {
    # cadenas dont l'anse se souleve, avec marques de mouvement
    'cadenas-souleve': '''
      <g transform="translate(2 -10) rotate(-10 50 40)">
        <path d="M34 52 V36 a16 16 0 0 1 32 0 V46" stroke="{a}" stroke-width="9" stroke-linecap="round" fill="none"/>
      </g>
      <path d="M15 26 L5 19" stroke="{a}" stroke-width="5" stroke-linecap="round" opacity="0.5"/>
      <path d="M26 15 L22 4" stroke="{a}" stroke-width="5" stroke-linecap="round" opacity="0.5"/>
      <rect x="20" y="50" width="60" height="38" rx="8" fill="{c}"/>
      <circle cx="50" cy="65" r="4.6" fill="{i}"/>
      <rect x="47.8" y="67" width="4.4" height="9" rx="2.2" fill="{i}"/>''',
    # deux maillons entrelaces
    'maillons': '''
      <rect x="12" y="34" width="46" height="32" rx="16" stroke="{a}" stroke-width="9" fill="none"/>
      <rect x="42" y="34" width="46" height="32" rx="16" stroke="{c}" stroke-width="9" fill="none"/>''',
    # piece d'identite avec portrait et lignes
    'identite': '''
      <rect x="10" y="24" width="80" height="54" rx="8" fill="{c}"/>
      <circle cx="34" cy="45" r="9" fill="{i}"/>
      <path d="M22 64 a12 12 0 0 1 24 0" fill="{i}"/>
      <rect x="55" y="40" width="26" height="5" rx="2.5" fill="{a}"/>
      <rect x="55" y="52" width="26" height="5" rx="2.5" fill="{i}" opacity="0.35"/>
      <rect x="55" y="62" width="18" height="5" rx="2.5" fill="{i}" opacity="0.35"/>''',
    # bouclier marque
    'marque': '''
      <path d="M50 10 L84 24 V52 c0 18 -14 30 -34 38 c-20 -8 -34 -20 -34 -38 V24 Z" fill="{c}"/>
      <circle cx="50" cy="48" r="15" stroke="{a}" stroke-width="7" fill="none"/>
      <path d="M50 40 v16" stroke="{a}" stroke-width="7" stroke-linecap="round"/>''',
    # facture avec coin plie
    'facture': '''
      <path d="M20 10 h44 l18 18 v62 h-62 Z" fill="{c}"/>
      <path d="M64 10 v18 h18 Z" fill="{i}" opacity="0.25"/>
      <rect x="30" y="42" width="40" height="5" rx="2.5" fill="{a}"/>
      <rect x="30" y="55" width="40" height="5" rx="2.5" fill="{i}" opacity="0.3"/>
      <rect x="30" y="68" width="24" height="5" rx="2.5" fill="{i}" opacity="0.3"/>''',
    # carton de conformite avec coche
    'conformite': '''
      <rect x="12" y="26" width="76" height="58" rx="8" fill="{c}"/>
      <path d="M12 44 h76" stroke="{i}" stroke-width="4" opacity="0.25"/>
      <path d="M32 62 l12 12 l24 -26" stroke="{a}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round" fill="none"/>''',
    # fonds retenus : piece barree
    'fonds': '''
      <circle cx="50" cy="50" r="34" fill="{c}"/>
      <path d="M60 38 a14 16 0 1 0 0 24" stroke="{i}" stroke-width="8" stroke-linecap="round" fill="none"/>
      <path d="M34 46 h22 M34 55 h22" stroke="{i}" stroke-width="6" stroke-linecap="round"/>
      <path d="M22 78 L78 22" stroke="{a}" stroke-width="9" stroke-linecap="round"/>''',
}


def police(nom):
    """Telecharge la police si absente du cache, renvoie son encodage base64."""
    os.makedirs(CACHE, exist_ok=True)
    chemin = os.path.join(CACHE, nom + '.ttf')
    if not os.path.exists(chemin):
        url = subprocess.run(
            ['curl', '-sS', '-A', 'Mozilla/4.0', POLICES[nom]],
            capture_output=True, text=True, check=True).stdout
        import re
        m = re.search(r'https://[^)]*\.ttf', url)
        if not m:
            sys.exit('police %s : aucune URL TTF trouvee' % nom)
        subprocess.run(['curl', '-sS', '-o', chemin, m.group(0)], check=True)
    return base64.b64encode(open(chemin, 'rb').read()).decode()


def lignes_titre(titre, max_car=19):
    if '|' in titre:
        return [l.strip() for l in titre.split('|') if l.strip()]
    return textwrap.wrap(titre, max_car) or [titre]


def echapper(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def construire_svg(titre, categorie, motif):
    lignes = lignes_titre(titre)
    taille = 72 if len(lignes) <= 2 else 60
    interligne = taille + 14
    # la composition occupe la bande centrale du carre : sips recadre par le centre
    O = 285
    haut = O + 315 - (len(lignes) * interligne) / 2 - 46

    textes = []
    textes.append('<text x="80" y="%.1f" font-family="PlexMono" font-weight="500" font-size="26" '
                  'fill="%s" letter-spacing="2">%s</text>'
                  % (haut, AMBRE, echapper(categorie.upper())))
    for i, l in enumerate(lignes):
        textes.append('<text x="80" y="%.1f" font-family="Fraunces" font-weight="600" font-size="%d" '
                      'fill="%s">%s</text>' % (haut + 62 + i * interligne, taille, CREME, echapper(l)))
    bas = haut + 62 + len(lignes) * interligne
    textes.append('<rect x="80" y="%.1f" width="96" height="4" fill="%s"/>' % (bas + 6, AMBRE))
    textes.append('<text x="80" y="%.1f" font-family="PlexMono" font-weight="500" font-size="22" '
                  'fill="%s" fill-opacity="0.55">compte-amazon-bloque.fr</text>' % (bas + 56, CREME))

    dessin = MOTIFS[motif].format(a=AMBRE, c=CREME, i=INK)

    return '''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1200" viewBox="0 0 1200 1200">
<defs><style>
@font-face{{font-family:'Fraunces';font-weight:600;src:url(data:font/ttf;base64,{f}) format('truetype');}}
@font-face{{font-family:'PlexSans';font-weight:400;src:url(data:font/ttf;base64,{s}) format('truetype');}}
@font-face{{font-family:'PlexMono';font-weight:500;src:url(data:font/ttf;base64,{m}) format('truetype');}}
</style></defs>
<rect width="1200" height="1200" fill="{ink}"/>
<circle cx="960" cy="{cy}" r="196" fill="{creme}" fill-opacity="0.05"/>
<g transform="translate(810 {gy}) scale(3)">{dessin}</g>
{textes}
</svg>'''.format(f=police('fraunces'), s=police('plexsans'), m=police('plexmono'),
                 ink=INK, creme=CREME, cy=O + 315, gy=O + 315 - 150,
                 dessin=dessin, textes='\n'.join(textes))


def rasteriser(svg, slug):
    os.makedirs(SORTIE, exist_ok=True)
    tmp = os.path.join(SORTIE, '.tmp-%s.svg' % slug)
    open(tmp, 'w', encoding='utf-8').write(svg)
    apercu = tmp + '.png'
    if os.path.exists(apercu):
        os.remove(apercu)
    subprocess.run(['qlmanage', '-t', '-s', '1200', '-o', SORTIE, tmp],
                   capture_output=True)
    if not os.path.exists(apercu):
        sys.exit('qlmanage n a produit aucun apercu')

    plein = os.path.join(SORTIE, slug + '.png')
    vignette = os.path.join(SORTIE, slug + '-vignette.png')
    subprocess.run(['sips', '-c', '630', '1200', apercu, '--out', plein], capture_output=True)
    subprocess.run(['sips', '-Z', '600', plein, '--out', vignette], capture_output=True)
    os.remove(tmp); os.remove(apercu)

    resultats = []
    for f in (plein, vignette):
        avant = os.path.getsize(f)
        apres, n = optimiser(f)
        resultats.append((os.path.relpath(f, RACINE), avant, apres, n))
    return resultats


def main():
    p = argparse.ArgumentParser(description='Genere la couverture d un article de blog.')
    p.add_argument('--slug', required=True, help='nom de fichier, sans extension')
    p.add_argument('--titre', required=True, help='titre court, | force un retour a la ligne')
    p.add_argument('--categorie', required=True)
    p.add_argument('--motif', required=True, choices=sorted(MOTIFS))
    a = p.parse_args()
    for chemin, avant, apres, n in rasteriser(construire_svg(a.titre, a.categorie, a.motif), a.slug):
        print('%-46s %6d -> %6d octets (%d couleurs)' % (chemin, avant, apres, n))


if __name__ == '__main__':
    main()
