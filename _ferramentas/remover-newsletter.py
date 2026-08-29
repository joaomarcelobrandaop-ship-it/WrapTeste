# -*- coding: utf-8 -*-
"""
Remove o bloco de newsletter do rodape customizado das 22 paginas.

MOTIVO (G-1 da vistoria de 28/08/2026): o formulario mostrava
"Thanks for subscribing!" e descartava o e-mail. Nao havia lista, servico,
politica nem descadastro -- so a promessa. Nao existe conserto tecnico para
uma promessa sem nada por tras: ou se cria a coisa, ou se para de prometer.

Isto e edicao do bloco de HTML personalizado do rodape, que e o MESMO que
esta no WordPress. Logo, viaja: o resultado vira copiar-e-colar la.
"""
import io, os, re, sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

AQUI = os.path.dirname(os.path.abspath(__file__))
GUARDA = os.path.join(AQUI, '..', 'referencias', 'newsletter-removida.html')


def bloco_newsletter(h):
    """Devolve (inicio, fim) do <div class="wng-newsletter"> ... </div>,
    incluindo o comentario <!-- NEWSLETTER --> que vem antes."""
    j = h.find('class="wng-newsletter"')
    if j < 0:
        return None
    ini = h.rfind('<div', 0, j)
    c = h.rfind('<!-- NEWSLETTER -->', 0, ini)
    if c > 0 and ini - c < 40:
        ini = c
    prof, k = 0, h.rfind('<div', 0, j)
    while k < len(h):
        m = re.compile(r'<(/?)div\b[^>]*>').search(h, k)
        if not m:
            break
        prof += -1 if m.group(1) else 1
        k = m.end()
        if prof == 0:
            return ini, k
    return None


def tirar_css(h):
    """Apaga as regras de CSS que so serviam a newsletter."""
    h = h.replace('/* NEWSLETTER */\n', '').replace('/* NEWSLETTER */', '')
    return re.sub(r'\n?[^{}\n][^{}]*wng-newsletter[^{}]*\{[^}]*\}', '', h)


if __name__ == '__main__':
    guardado = False
    n_pag = n_css = 0
    for raiz, dirs, arqs in os.walk(AQUI):
        dirs[:] = [d for d in dirs if d not in {'wp-content', 'wp-includes',
                                                '_ferramentas', '.git'}]
        for a in arqs:
            if a != 'index.html':
                continue
            cam = os.path.join(raiz, a)
            h = io.open(cam, encoding='utf-8', errors='replace').read()
            lim = bloco_newsletter(h)
            if not lim:
                continue
            ini, fim = lim
            if not guardado:
                io.open(GUARDA, 'w', encoding='utf-8').write(
                    '<!-- Removido do rodape em 28/08/2026 (G-1 da vistoria).\n'
                    '     Guardado exatamente como estava, para a pergunta ao dono. -->\n'
                    + h[ini:fim] + '\n')
                guardado = True
            novo = h[:ini] + h[fim:]
            antes = novo.count('wng-newsletter')
            novo = tirar_css(novo)
            n_css += antes - novo.count('wng-newsletter')
            io.open(cam, 'w', encoding='utf-8').write(novo)
            n_pag += 1
    print('paginas limpas          : %d' % n_pag)
    print('regras de CSS removidas : %d' % n_css)
    print('original guardado em    : referencias/newsletter-removida.html')
