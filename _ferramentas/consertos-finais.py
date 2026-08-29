# -*- coding: utf-8 -*-
"""
Tres consertos que fecham o que da para fechar sem o dono:

A-3  copyright invisivel: um bloco do tema, DEPOIS do rodape customizado,
     com texto branco sobre fundo branco. Nao da para corrigir com cor --
     ficariam dois copyrights, com grafias diferentes ("Wrap N Glass" e
     "Wrapnglass"). Some o bloco duplicado.
     No WordPress: Aparencia -> Editor -> Partes do modelo -> Rodape.

A-7  a home nao tinha nenhum <h1>. O texto principal do topo existe, mas
     como <p>. Nao invento titulo: promovo o que ja esta la.

     ⚠️ Observacao para o Joao: "Instant Download" e um H1 fraco para busca
     -- nao diz o que o negocio faz. Trocar o TEXTO e decisao do dono; o
     que eu conserto aqui e a ESTRUTURA.

S-6b o link "Cookie Policy" dentro do texto legal (Termos, 8.3) apontava
     para /cookies, que nao existe. Reaponto para a Politica de Privacidade,
     que tem secao de cookies. NAO reescrevo o texto juridico -- so o link.
"""
import io, os, re, sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass


def fim_da_div(h, ini):
    prof, k = 0, ini
    pad = re.compile(r'<(/?)div\b[^>]*>')
    while k < len(h):
        m = pad.search(h, k)
        if not m:
            return None
        prof += -1 if m.group(1) else 1
        k = m.end()
        if prof == 0:
            return k
    return None


if __name__ == '__main__':
    n_copy = n_h1 = n_ck = 0
    for raiz, dirs, arqs in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in {'wp-content', 'wp-includes',
                                                '_ferramentas', '.git'}]
        for a in arqs:
            if a != 'index.html':
                continue
            cam = os.path.join(raiz, a)
            h = io.open(cam, encoding='utf-8', errors='replace').read()
            orig = h

            # A-3 -- o bloco do copyright duplicado
            m = re.search(r'<p class="[^"]*has-light-color[^"]*">\s*&copy;|'
                          r'<p class="[^"]*has-light-color[^"]*">\s*©', h)
            if m:
                ini = h.rfind('<div class="wp-block-group alignwide'
                              ' is-content-justification-center', 0, m.start())
                if ini > 0:
                    fim = fim_da_div(h, ini)
                    if fim and 'All rights reserved' in h[ini:fim] and fim - ini < 900:
                        h = h[:ini] + h[fim:]
                        n_copy += 1

            # A-7 -- o titulo do topo da home vira <h1>
            velho = '<p class="elementor-heading-title elementor-size-default">Instant Download</p>'
            if velho in h:
                h = h.replace(
                    velho,
                    '<h1 class="elementor-heading-title elementor-size-default">'
                    'Instant Download</h1>', 1)
                n_h1 += 1

            # S-6b -- o link morto dentro do texto legal
            if 'href="/cookies"' in h:
                h = h.replace('href="/cookies"', 'href="/privacy-policy/"')
                n_ck += 1

            if h != orig:
                io.open(cam, 'w', encoding='utf-8').write(h)

    print('copyright duplicado removido : %d paginas' % n_copy)
    print('h1 da home corrigido         : %d pagina' % n_h1)
    print('link de cookies no texto     : %d pagina' % n_ck)
