# -*- coding: utf-8 -*-
"""
Monta as tres paginas de catalogo a partir da casca do espelho.

Por que a partir de uma pagina existente: cabecalho e rodape sao gerados
pelo WordPress. Reescrever a mao daria uma pagina que nao bate com o resto
do site. Copiando a casca, o catalogo ja nasce dentro do site verdadeiro.

O <h1> e o aviso ficam AQUI, no HTML, nao no JavaScript: se o script
falhar, a pagina ainda tem cabecalho em vez de ficar em branco.
"""
import io, re, os

CASCA = 'hello-world/index.html'

AVISO = ('<div class="wcat-aviso"><strong>Prototype.</strong> These designs are '
         'drawn by code to show how the catalogue behaves &mdash; they are not the '
         'studio&rsquo;s own artwork. Price, size and the colour range are marked '
         '<code>[TO CONFIRM]</code> on purpose.</div>')

PAGINAS = [
    ('vehicle-wraps', 'Vehicle Wraps',
     'Ready-to-cut stripe designs for vehicle doors, hoods and sides.'),
    ('marine-wraps', 'Marine Wraps',
     'Hull and deck graphics, cut-ready for boats and jet skis.'),
    ('architectural-glass', 'Architectural Glass',
     'Frosted and privacy films for windows, doors and partitions.'),
]

h = io.open(CASCA, encoding='utf-8', errors='replace').read()
ini = h.find('<main class="wp-block-group is-layout-flow')
fim = h.find('<footer class="site-footer')
assert ini > 0 and fim > ini, 'nao achei os limites do conteudo'
antes, depois = h[:ini], h[fim:]

for slug, titulo, linha in PAGINAS:
    corpo = (
        '<main class="wp-block-group is-layout-flow wp-block-group-is-layout-flow">\n'
        '<div class="wcat" data-wng-catalogo="%s">\n'
        '%s\n'
        '<header class="wcat-cab">\n'
        '<h1>%s</h1>\n'
        '<p>%s</p>\n'
        '<p class="wcat-cont">6 designs &middot; 8 colours &middot; 4 sizes</p>\n'
        '</header>\n'
        '<noscript><p class="wcat-noscript">This catalogue needs JavaScript to '
        'show the designs and the colour picker.</p></noscript>\n'
        '</div>\n'
        '</main>\n\n\n' % (slug, AVISO, titulo, linha)
    )
    p = antes + corpo + depois
    p = re.sub(r'<title>.*?</title>', '<title>%s</title>' % titulo, p, count=1, flags=re.S)
    p = re.sub(r'(<meta property="og:title" content=")[^"]*(")',
               r'\g<1>' + titulo + r'\g<2>', p, count=1)
    p = p.replace('</body>', '<script src="/wng-catalogo.js" defer></script>\n</body>', 1)
    p = p.replace('class="post-template-default single single-post',
                  'class="page-template-default page wng-catalogo single single-post', 1)
    os.path.isdir(slug) or os.makedirs(slug)
    io.open(os.path.join(slug, 'index.html'), 'w', encoding='utf-8').write(p)
    print('  %-22s %7d bytes' % (slug + '/', len(p)))
