# -*- coding: utf-8 -*-
"""
Troca S/M/L/XL por medidas de verdade, uma regua por familia de produto.

POR QUE UMA REGUA POR FAMILIA
60 cm nao faz sentido para o casco de um barco; 600 cm nao faz sentido para
uma janela. Usar a mesma escala nas tres seria mais simples e mais errado.

DE ONDE VEM CADA NUMERO
  Architectural Glass -- COM FONTE. Pelicula de janela e produzida em
  larguras padrao de 91 cm (36"), 122 cm (48") e 152 cm (60"). 152 cm e o
  padrao internacional maximo de producao; acima disso o fornecedor entrega
  em duas partes para emendar.
     window-film-solaris.co.uk/window-film/sizes

  Vehicle Wraps -- PARCIALMENTE COM FONTE. A pesquisa da os paineis
  (decalque de porta 30-61 cm; lateral de van 46-91 cm e acima), mas nao
  existe escala unica de mercado porque cada kit e feito para um modelo de
  carro. A escada abaixo esta ancorada em medidas reais de veiculo -- porta
  ~100-120 cm, lateral inteira ~350-450 cm -- mas a ESCADA e proposta nossa.
     4over4.com/guide/custom-car-decal-sticker-size-chart

  Marine Wraps -- SEM FONTE. Nao achei padrao publicado para grafismo de
  casco; a medida acompanha o tamanho do barco. Proposta coerente com a de
  veiculo, escalada para embarcacao de 5 a 10 m.

⚠️ Os tres conjuntos sao PROPOSTA para o dono confirmar. A diferenca em
relacao ao que havia antes e que agora ele confirma ou corrige um numero,
em vez de preencher um espaco vazio.
"""
import io
import re

JS = 'wng-catalogo.js'

NOVO_TAMANHOS = """  /* ---------------------------------------------------------------
     2. TAMANHOS -- uma regua por familia

     Nao da para usar a mesma escala nas tres: 60 cm nao serve para casco
     de barco e 600 cm nao serve para janela.

     `nome` e o que o cliente ve E o que vira o atributo no WooCommerce --
     tem de bater com gerar-produtos.py. `conferir-catalogo.py` checa.

     ⚠️ [A CONFIRMAR] com o dono. Os de vidro tem fonte (largura padrao de
     rolo de pelicula); os de carro estao ancorados em medida de veiculo;
     os de barco sao proposta nossa.
     --------------------------------------------------------------- */
  var TAMANHOS = {
    'vehicle-wraps': [
      { id: 'v60',  nome: '60 cm',  medida: 'door panel, accent' },
      { id: 'v120', nome: '120 cm', medida: 'full door, hood' },
      { id: 'v200', nome: '200 cm', medida: 'side section' },
      { id: 'v300', nome: '300 cm', medida: 'full side, van' }
    ],
    'marine-wraps': [
      { id: 'm150', nome: '150 cm', medida: 'transom, small panel' },
      { id: 'm250', nome: '250 cm', medida: 'hull side, up to 6 m' },
      { id: 'm400', nome: '400 cm', medida: 'hull side, up to 9 m' },
      { id: 'm600', nome: '600 cm', medida: 'full hull side' }
    ],
    'architectural-glass': [
      { id: 'g91',  nome: '91 cm',  medida: 'standard film width, 36 in' },
      { id: 'g122', nome: '122 cm', medida: 'standard film width, 48 in' },
      { id: 'g152', nome: '152 cm', medida: 'widest single sheet, 60 in' }
    ]
  };"""

j = io.open(JS, encoding='utf-8').read()

# --- 1. substitui o bloco de TAMANHOS ---------------------------------
antigo = re.search(r'  /\* -+\n     2\. TAMANHOS.*?\n  \];', j, re.S)
if not antigo:
    antigo = re.search(r'  var TAMANHOS = \[.*?\n  \];', j, re.S)
assert antigo, 'nao achei o bloco TAMANHOS'
j = j[:antigo.start()] + NOVO_TAMANHOS + j[antigo.end():]

# --- 2. dentro de iniciar(), pegar a regua da familia -----------------
alvo = "    var padA = CORES[0], padB = CORES[1];"
assert alvo in j
j = j.replace(alvo,
              "    var padA = CORES[0], padB = CORES[1];\n"
              "    /* a regua de tamanho depende da familia desta pagina */\n"
              "    var TAMS = TAMANHOS[raiz.getAttribute('data-wng-catalogo')] || [];",
              1)

# --- 3. todos os usos passam a ser TAMS -------------------------------
usos = [
    ("var atual = { d: null, a: padA, b: padB, t: TAMANHOS[1] };",
     "var atual = { d: null, a: padA, b: padB, t: TAMS[1] || TAMS[0] };"),
    ("atual.t = TAMANHOS.filter(function (x) { return x.id === tm.dataset.tam; })[0];",
     "atual.t = TAMS.filter(function (x) { return x.id === tm.dataset.tam; })[0];"),
    ("document.getElementById('wcat-tam').innerHTML = TAMANHOS.map(function (t) {",
     "document.getElementById('wcat-tam').innerHTML = TAMS.map(function (t) {"),
]
for a, b in usos:
    assert a in j, 'nao achei: %s' % a[:50]
    j = j.replace(a, b, 1)

# --- 4. o CSV de exemplo dentro do JS ---------------------------------
j = j.replace("var tams = TAMANHOS.map(function (t) { return t.nome; }).join(', ');",
              "var tams = TAMS.map(function (t) { return t.nome; }).join(', ');", 1)

io.open(JS, 'w', encoding='utf-8').write(j)
print('wng-catalogo.js: uma regua de tamanho por familia')
for fam in ['vehicle-wraps', 'marine-wraps', 'architectural-glass']:
    bloco = re.search(r"'%s': \[(.*?)\]" % fam, j, re.S).group(1)
    print('  %-22s %s' % (fam, ', '.join(re.findall(r"nome: '([^']+)'", bloco))))
