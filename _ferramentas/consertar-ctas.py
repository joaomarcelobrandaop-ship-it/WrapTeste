# -*- coding: utf-8 -*-
"""
Conserta os botoes de chamada que apontavam para /contact (404) e a faixa
de baixo do rodape.

Nao existe pagina de contato no WordPress. O unico canal de contato que o
site publica e o e-mail. Entao o botao passa a abrir o e-mail ja endereçado
e com assunto -- funciona hoje, nao inventa pagina, e nao mente.

Cada botao leva o assunto do lugar de onde foi clicado, para o dono saber
de onde veio a mensagem.
"""
import io, os, re, sys
from urllib.parse import quote

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

EMAIL = 'studio@wrapnglass.com'


def mailto(assunto):
    return 'mailto:%s?subject=%s' % (EMAIL, quote(assunto))


def nome_do_plano(h, pos):
    """Sobe no HTML ate achar o nome do plano em que o botao esta."""
    trecho = h[max(0, pos - 4000):pos]
    nomes = re.findall(r'class="ds-plan-name">(.*?)<', trecho)
    return re.sub(r'<[^>]+>', '', nomes[-1]).strip() if nomes else None


if __name__ == '__main__':
    n_bt = n_com = n_bottom = 0
    for raiz, dirs, arqs in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in {'wp-content', 'wp-includes',
                                                '_ferramentas', '.git'}]
        for a in arqs:
            if a != 'index.html':
                continue
            cam = os.path.join(raiz, a)
            h = io.open(cam, encoding='utf-8', errors='replace').read()
            orig = h

            # --- botoes /contact -> e-mail com assunto ---------------------
            while True:
                m = re.search(r'<a href="/contact"([^>]*)>(.*?)</a>', h, re.S)
                if not m:
                    break
                rotulo = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', m.group(2))).strip()
                if 'want this one' in rotulo:
                    plano = nome_do_plano(h, m.start())
                    assunto = 'Website plan: %s' % plano if plano else 'Website plan enquiry'
                elif 'Start your project' in rotulo:
                    assunto = 'New website project'
                else:
                    assunto = 'Website enquiry'
                h = h[:m.start()] + '<a href="%s"%s>%s</a>' % (
                    mailto(assunto), m.group(1), m.group(2)) + h[m.end():]
                n_bt += 1

            # --- comentarios de tarefa deixados no HTML publicado ----------
            h2 = re.sub(r'\s*<!--[^>]*?(?:EDIT|TODO|FIXME):[^>]*?-->', '', h)
            n_com += len(re.findall(r'<!--[^>]*?(?:EDIT|TODO|FIXME):[^>]*?-->', h))
            h = h2

            # --- faixa de baixo do rodape ---------------------------------
            velho = ('<a href="/privacy-policy">Privacy</a>\n'
                     '        <a href="/terms-of-use">Terms</a>\n'
                     '        <a href="/cookies">Cookies</a>')
            novo = ('<a href="/privacy-policy/">Privacy</a>\n'
                    '        <a href="/terms-conditions/">Terms</a>')
            if velho in h:
                h = h.replace(velho, novo)
                n_bottom += 1
            else:
                antes = h
                h = re.sub(r'<a href="/terms-of-use">Terms</a>',
                           '<a href="/terms-conditions/">Terms</a>', h)
                h = re.sub(r'\s*<a href="/cookies">Cookies</a>', '', h)
                h = re.sub(r'<a href="/privacy-policy">Privacy</a>',
                           '<a href="/privacy-policy/">Privacy</a>', h)
                if h != antes:
                    n_bottom += 1

            if h != orig:
                io.open(cam, 'w', encoding='utf-8').write(h)

    print('botoes de contato religados : %d' % n_bt)
    print('comentarios de tarefa tirados: %d' % n_com)
    print('faixa de baixo consertada    : %d paginas' % n_bottom)
