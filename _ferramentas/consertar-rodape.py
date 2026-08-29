# -*- coding: utf-8 -*-
"""
Conserta o rodape customizado nas 22 paginas.

PRINCIPIO: um link que da 404 e PIOR do que nenhum link. O rodape antigo
listava o site que alguem gostaria de ter; o novo lista o site que existe.

Resolve de uma vez:
  G-2  17 dos 20 links quebrados (os outros 3 sao do menu do topo)
  S-3  os dois marcadores de endereco diferentes viram um so
  A-5  e-mail e telefone passam a ser clicaveis
  S-6  o aviso de cookies para de presumir consentimento
"""
import io, os, re, sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# --- as tres colunas, so com destino que existe -------------------------
COLUNAS = '''<div class="wng-col-brand">
        <p class="wng-brand-text">&#8220;Your file. Your design. Your rules.&#8221;</p>
        <p class="wng-brand-detail">
          <a href="mailto:studio@wrapnglass.com">studio@wrapnglass.com</a><br>
          <a href="tel:+35679989979">+356 7998 9979</a><br>
          Malta
        </p>
        <div class="wng-socials">
          <a href="https://instagram.com/wrapnglass" target="_blank" rel="noopener">IG</a>
          <a href="https://facebook.com/wrapnglass" target="_blank" rel="noopener">FB</a>
          <a href="https://tiktok.com/@wrapnglass" target="_blank" rel="noopener">TK</a>
          <a href="https://pinterest.com/wrapnglass" target="_blank" rel="noopener">PT</a>
        </div>
      </div>
      <!-- SHOP -->
      <div>
        <div class="wng-col-title">Shop</div>
        <ul class="wng-col-list">
          <li><a href="/vehicle-wraps/">Vehicle Wraps</a></li>
          <li><a href="/marine-wraps/">Marine Wraps</a></li>
          <li><a href="/architectural-glass/">Architectural Glass</a></li>
          <li><a href="/shop/">All Templates</a></li>
        </ul>
      </div>
      <!-- COMPANY -->
      <div>
        <div class="wng-col-title">Company</div>
        <ul class="wng-col-list">
          <li><a href="/services/">Services</a></li>
          <li><a href="/digital-solutions/">Digital Solutions</a></li>
          <li><a href="/gallery/">Gallery</a></li>
        </ul>
      </div>
      <!-- HELP -->
      <div>
        <div class="wng-col-title">Help</div>
        <ul class="wng-col-list">
          <li><a href="mailto:studio@wrapnglass.com">Contact us</a></li>
          <li><a href="/my-account/">My account</a></li>
          <li><a href="/terms-conditions/">Terms &amp; Conditions</a></li>
          <li><a href="/privacy-policy/">Privacy Policy</a></li>
        </ul>
      </div>'''

# --- barra legal: um marcador so de endereco, links que abrem -----------
LEGAL = '''<div class="wng-legal-info">
        <strong>Wrap N Glass</strong> &middot; Self-employed in Malta<br>
        VAT ID: <strong>MT[XXXXXXXX]</strong> &middot; <strong>[Full Address, Malta]</strong><br>
        Email: <a href="mailto:studio@wrapnglass.com">studio@wrapnglass.com</a> &middot;
        Phone: <a href="tel:+35679989979">+356 7998 9979</a><br>
        <span class="wng-legal-nota">Your data is processed per our Privacy Policy.
        You have GDPR rights &mdash; contact us to exercise them.</span>
      </div>
      <div class="wng-legal-links">
        <a href="/privacy-policy/">Privacy Policy</a>
        <a href="/terms-conditions/">Terms &amp; Conditions</a>
        <a href="/terms-conditions/">Refunds</a>
      </div>'''

# --- aviso de cookies: consentimento por ato, nao por continuar ---------
COOKIE_TXT = ('We use cookies to run the shop and understand how the site is used. '
              'You choose: read our <a href="/terms-conditions/">Cookie terms</a> and '
              '<a href="/privacy-policy/">Privacy Policy</a>.')

CSS_EXTRA = '''
#wng-footer .wng-brand-detail a,
#wng-footer .wng-legal-info a {
  color: inherit;
  text-decoration: underline;
  text-underline-offset: 2px;
}
#wng-footer .wng-brand-detail a:hover,
#wng-footer .wng-legal-info a:hover { color: #ff336e; }
#wng-footer .wng-legal-nota { font-size: 12px; display: block; margin-top: 6px; }
'''


def trocar(h, ini_marca, fim_marca, novo):
    i = h.find(ini_marca)
    if i < 0:
        return h, False
    j = h.find(fim_marca, i)
    if j < 0:
        return h, False
    return h[:i] + novo + h[j:], True


if __name__ == '__main__':
    contas = {'colunas': 0, 'legal': 0, 'cookie': 0, 'css': 0}
    for raiz, dirs, arqs in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in {'wp-content', 'wp-includes',
                                                '_ferramentas', '.git'}]
        for a in arqs:
            if a != 'index.html':
                continue
            cam = os.path.join(raiz, a)
            h = io.open(cam, encoding='utf-8', errors='replace').read()
            if 'id="wng-footer"' not in h:
                continue

            h, ok = trocar(h, '<div class="wng-col-brand">',
                           '\n    <!-- NEWSLETTER -->\n', COLUNAS)
            if not ok:
                h, ok = trocar(h, '<div class="wng-col-brand">',
                               '<!-- LEGAL BAR -->', COLUNAS + '\n    </div>\n\n    ')
            contas['colunas'] += ok

            h, ok = trocar(h, '<div class="wng-legal-info">', '<!-- BOTTOM -->',
                           LEGAL + '\n    </div>\n\n    ')
            contas['legal'] += ok

            # aviso de cookies
            m = re.search(r'(<div id="wng-cookie-banner"[^>]*>\s*<p[^>]*>)(.*?)(</p>)', h, re.S)
            if m:
                h = h[:m.start(2)] + COOKIE_TXT + h[m.end(2):]
                contas['cookie'] += 1

            if '.wng-legal-nota' not in h:
                k = h.find('/* LEGAL BAR */')
                if k > 0:
                    h = h[:k] + CSS_EXTRA + '\n' + h[k:]
                    contas['css'] += 1

            io.open(cam, 'w', encoding='utf-8').write(h)
    print('colunas reconstruidas : %d paginas' % contas['colunas'])
    print('barra legal           : %d paginas' % contas['legal'])
    print('aviso de cookies      : %d paginas' % contas['cookie'])
    print('css dos links         : %d paginas' % contas['css'])
