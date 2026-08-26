"""Reencode un PNG en palette indexee (type 3).

Les couvertures n'utilisent que trois couleurs de charte et leurs degrades
d'anticrenelage : une palette indexee divise le poids par trois a quatre
sans perte visible. Aucune dependance externe.
"""
import zlib, struct


def _lire(chemin):
    d = open(chemin, 'rb').read()
    assert d[:8] == b'\x89PNG\r\n\x1a\n', 'ce fichier n est pas un PNG'
    i, idat, ihdr = 8, b'', None
    while i < len(d):
        n = struct.unpack('>I', d[i:i+4])[0]
        t = d[i+4:i+8]
        c = d[i+8:i+8+n]
        if t == b'IHDR':
            ihdr = struct.unpack('>IIBBBBB', c)
        elif t == b'IDAT':
            idat += c
        elif t == b'IEND':
            break
        i += 12 + n
    return ihdr, zlib.decompress(idat)


def _defiltrer(brut, w, h, bpp):
    lignes, prec, pos = [], bytearray(w * bpp), 0
    for _ in range(h):
        f = brut[pos]; pos += 1
        ligne = bytearray(brut[pos:pos + w * bpp]); pos += w * bpp
        for x in range(len(ligne)):
            a = ligne[x - bpp] if x >= bpp else 0
            b = prec[x]
            c = prec[x - bpp] if x >= bpp else 0
            if f == 1:   ligne[x] = (ligne[x] + a) & 255
            elif f == 2: ligne[x] = (ligne[x] + b) & 255
            elif f == 3: ligne[x] = (ligne[x] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                ligne[x] = (ligne[x] + pr) & 255
        lignes.append(bytes(ligne)); prec = ligne
    return lignes


def _chunk(t, d):
    return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)


def optimiser(entree, sortie=None, max_couleurs=256):
    sortie = sortie or entree
    (w, h, prof, type_c, _, _, _) = _lire(entree)[0]
    ihdr, brut = _lire(entree)
    assert prof == 8 and type_c in (2, 6), 'seuls les PNG 8 bits RGB ou RGBA sont geres'
    bpp = 4 if type_c == 6 else 3
    lignes = _defiltrer(brut, w, h, bpp)

    compte = {}
    for l in lignes:
        for x in range(0, len(l), bpp):
            px = (l[x], l[x+1], l[x+2])
            compte[px] = compte.get(px, 0) + 1

    palette = [c for c, _ in sorted(compte.items(), key=lambda kv: -kv[1])[:max_couleurs]]
    index = {c: i for i, c in enumerate(palette)}
    cache = {}

    def idx(px):
        i = index.get(px)
        if i is not None:
            return i
        i = cache.get(px)
        if i is None:
            i = min(range(len(palette)),
                    key=lambda k: (px[0]-palette[k][0])**2 + (px[1]-palette[k][1])**2 + (px[2]-palette[k][2])**2)
            cache[px] = i
        return i

    corps = bytearray()
    for l in lignes:
        corps.append(0)
        for x in range(0, len(l), bpp):
            corps.append(idx((l[x], l[x+1], l[x+2])))

    plte = b''.join(bytes(c) for c in palette)
    png = (b'\x89PNG\r\n\x1a\n'
           + _chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 3, 0, 0, 0))
           + _chunk(b'PLTE', plte)
           + _chunk(b'IDAT', zlib.compress(bytes(corps), 9))
           + _chunk(b'IEND', b''))
    open(sortie, 'wb').write(png)
    return len(png), len(palette)


if __name__ == '__main__':
    import sys
    for f in sys.argv[1:]:
        avant = len(open(f, 'rb').read())
        apres, n = optimiser(f)
        print('%-44s %6d -> %6d octets  (%d couleurs)' % (f, avant, apres, n))
