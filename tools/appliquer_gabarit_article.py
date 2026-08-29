#!/usr/bin/env python3
"""Applique le gabarit d'article a trois colonnes a une page de blog.

Le site est statique et ne dispose pas de moteur de template : la mise en
page vit dans blog.css et blog.js, ce script pose le squelette de grille
dans le fichier HTML. Il est idempotent, relancer ne change rien.

Usage :
  python3 tools/appliquer_gabarit_article.py blog/mon-article.html
"""
import io, re, sys

MARQUE = ('<span class="mark"><svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
          '<path class="shackle" d="M8 10V7a4 4 0 0 1 7.5-1.9" stroke-width="2" stroke-linecap="round"/>'
          '<rect class="body" x="5" y="10" width="14" height="10" rx="2"/>'
          '<circle cx="12" cy="14.5" r="1.3" fill="#16233B"/>'
          '<rect x="11.4" y="15" width="1.2" height="2.6" rx="0.6" fill="#16233B"/></svg></span>')


def transformer(chemin):
    s = io.open(chemin, encoding='utf-8').read()
    if 'class="article-layout"' in s:
        return 'deja au gabarit'

    # --- 1. extraction du sommaire, qui part en colonne gauche ---
    m = re.search(r'[ \t]*<nav class="toc".*?</nav>\n', s, re.S)
    if not m:
        sys.exit('%s : sommaire introuvable' % chemin)
    toc = m.group(0)
    s = s[:m.start()] + s[m.end():]
    # le nav devient un details repliable, le titre passe dans summary
    corps_toc = re.search(r'<ol>.*</ol>', toc, re.S).group(0)
    titre_toc = re.search(r'<h2 id="sommaire-titre">(.*?)</h2>', toc).group(1)
    toc_neuf = ('      <details class="toc" open>\n'
                '        <summary><h2 id="sommaire-titre">%s</h2></summary>\n'
                '        %s\n'
                '      </details>\n' % (titre_toc, corps_toc.replace('\n', '\n  ')))

    # --- 2. extraction du bloc auteur, deplace en colonne droite ---
    m = re.search(r'[ \t]*<div class="auteur">.*?</div>\s*</div>\n', s, re.S)
    if not m:
        sys.exit('%s : bloc auteur introuvable' % chemin)
    auteur = m.group(0)
    s = s[:m.start()] + s[m.end():]
    nom = re.search(r'<h2>(.*?)</h2>', auteur).group(1)
    desc = re.search(r'<p>(.*?)</p>', auteur, re.S).group(1)

    # --- 3. squelette de grille autour de l'article ---
    aside = ('''    <aside class="col-toc" aria-label="Sommaire de l'article">
%s    </aside>

''' % toc_neuf)

    lateral = ('''
    <aside class="col-aside" aria-label="À propos et contact">
      <div class="side-box side-auteur">
        %s
        <h2>%s</h2>
        <p>%s</p>
      </div>
      <div class="side-box side-cta">
        <h2>Besoin d'aide&nbsp;?</h2>
        <p>Nous analysons votre dossier par écrit et vous disons ce qui est défendable en l'état. Obligation de moyens, la décision appartient à Amazon.</p>
        <a class="btn btn-primary btn-sm" href="/#formulaire">Faire analyser mon dossier</a>
      </div>
    </aside>
''' % (MARQUE, nom, desc))

    s = s.replace('<article class="article">\n',
                  '<div class="article-layout">\n\n' + aside + '  <article class="article">\n', 1)
    s = s.replace('</article>\n', '  </article>\n' + lateral + '\n</div>\n', 1)

    # --- 4. script partage, avant la fermeture du body ---
    if 'blog.js' not in s:
        s = s.replace('</body>', '<script src="/blog.js" defer></script>\n</body>', 1)

    io.open(chemin, 'w', encoding='utf-8').write(s)
    return 'gabarit applique'


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for f in sys.argv[1:]:
        print('%-46s %s' % (f, transformer(f)))
