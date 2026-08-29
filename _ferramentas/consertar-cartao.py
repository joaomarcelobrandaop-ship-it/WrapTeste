# -*- coding: utf-8 -*-
"""
Conserta os dois botoes de compra do estudio de cartao (pagina /services/).

O PROBLEMA
  goToPay() mandava para /producto/business-card-single e -both.
  Nenhum dos dois existe no WordPress: os dois dao 404, confirmado no site
  real. Ou seja, a ferramenta inteira funciona -- monta o cartao, desenha
  em canvas, deixa baixar a previa -- e trava exatamente na hora de pagar.

O CONSERTO CERTO (nao e este)
  Criar dois produtos no WooCommerce, 3 EUR e 5 EUR, e apontar os botoes
  para eles. Sao 15 minutos la dentro, mas depende de o dono ter o
  pagamento ligado -- coisa que o Joao nao faz por ele.

O CONSERTO POSSIVEL AGORA (este)
  O botao abre o e-mail ja endereçado, com assunto e com a configuracao
  que a pessoa montou (template, paleta, fonte e todos os campos). Nao
  perde o trabalho dela e nao leva a uma pagina de erro.
"""
import io
import re

CAMINHO = 'services/index.html'

NOVO = """function goToPay(type){
  /* Interim: os produtos /producto/business-card-single e -both nao existem
     no WooCommerce (404 confirmado). Ate serem criados, o botao abre o
     e-mail ja com a configuracao montada, para nao perder o trabalho de
     quem desenhou o cartao. Quando os produtos existirem, e so voltar a:
       window.location.href = type==='single' ? WC_SINGLE : WC_BOTH; */
  var v = getV();
  var NL = String.fromCharCode(10);
  var corpo = [
    'Card: ' + (type === 'single' ? 'one side (3 EUR)' : 'both sides (5 EUR)'),
    'Template: ' + TEMPLATES[curT].id,
    'Palette: ' + PALETTES[curP].id,
    'Font: ' + FONTS[curF].id,
    '',
    'FRONT',
    'Brand: ' + v.brand,
    'Tagline: ' + v.tag,
    'Website: ' + v.web,
    '',
    'BACK',
    'Name: ' + v.name,
    'Title: ' + v.role,
    'Phone: ' + v.phone,
    'Email: ' + v.email,
    'Social: ' + v.social
  ].join(NL);
  try {
    sessionStorage.setItem('wng_card_config', JSON.stringify({
      template: TEMPLATES[curT].id,
      palette: PALETTES[curP].id,
      font: FONTS[curF].id,
      type: type,
      vals: v
    }));
  } catch (e) { /* navegador em modo privado; segue sem guardar */ }
  window.location.href = 'mailto:studio@wrapnglass.com'
    + '?subject=' + encodeURIComponent('Print-ready business card - '
        + (type === 'single' ? '1 side' : 'both sides'))
    + '&body=' + encodeURIComponent(corpo);
}"""


def bloco_da_funcao(h, nome):
    m = re.search(r'function\s+' + nome + r'\s*\([^)]*\)\s*\{', h)
    if not m:
        return None
    prof, k = 0, m.end() - 1
    while k < len(h):
        if h[k] == '{':
            prof += 1
        elif h[k] == '}':
            prof -= 1
            if prof == 0:
                return m.start(), k + 1
        k += 1
    return None


h = io.open(CAMINHO, encoding='utf-8', errors='replace').read()
lim = bloco_da_funcao(h, 'goToPay')
assert lim, 'nao achei a funcao goToPay'
ini, fim = lim
antigo = h[ini:fim]
h = h[:ini] + NOVO + h[fim:]

# WC_SINGLE / WC_BOTH ficam declarados, com um aviso do porque
h = h.replace(
    "const WC_SINGLE = '/producto/business-card-single';",
    "/* ainda nao existem no WooCommerce -- ver goToPay() */\n"
    "  const WC_SINGLE = '/producto/business-card-single';", 1)

io.open(CAMINHO, 'w', encoding='utf-8').write(h)
print('goToPay trocada.')
print('  antes: %d caracteres' % len(antigo))
print('  agora: %d caracteres' % len(NOVO))
print('  ainda aponta direto para /producto/business-card?',
      'SIM' if "location.href = type==='single'" in h else 'nao')
