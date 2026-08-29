# -*- coding: utf-8 -*-
"""
Liga o botao do catalogo ao WooCommerce de verdade.

COMO FUNCIONA
O WooCommerce aceita a variacao pre-selecionada pela barra de endereco:

    /product/shard/?attribute_pa_colour=navy&attribute_pa_size=m

Ele le esses parametros, ja marca a cor e o tamanho na pagina do produto e
mostra o preco certo. A pessoa so confirma e adiciona ao carrinho.

POR QUE ASSIM E NAO PELO ID
O jeito classico (?add-to-cart=123&variation_id=456) exige o numero que o
WooCommerce da ao produto DEPOIS de importar. Slug eu sei de antemao -- e o
nome do design em minusculas. Entao o link ja nasce certo, sem ninguem
precisar voltar aqui para preencher numero.

O INTERRUPTOR
Enquanto os produtos nao existirem, o botao NAO vira link: continua
explicando por que nao da para comprar ainda. Para ligar, depois de importar
o CSV, e so trocar uma linha no topo do wng-catalogo.js:

    var LOJA_PRONTA = false;   ->   var LOJA_PRONTA = true;

Assim o botao nunca leva a uma pagina que nao existe.
"""
import io
import re

ARQ = 'wng-catalogo.js'

# ---------------------------------------------------------------- 1
INTERRUPTOR = """
  /* ---------------------------------------------------------------
     0. A LOJA JA TEM OS PRODUTOS?

     false -> o botao explica que a compra ainda nao esta ligada
     true  -> o botao vira link para a pagina do produto, com a cor e o
              tamanho ja escolhidos

     Virar para true DEPOIS de importar `produtos-wng.csv` no WooCommerce.
     Antes disso o link levaria a uma pagina que nao existe.
     --------------------------------------------------------------- */
  var LOJA_PRONTA = false;

  /* Prefixo das paginas de produto. Hoje o site usa /producto/ (espanhol);
     quando os slugs forem traduzidos vira /product/. Ver TAREFAS-NO-WORDPRESS. */
  var BASE_PRODUTO = '/producto/';

  function paraSlug(t) {
    return String(t).toLowerCase().replace(/\\s+/g, '-').replace(/[^a-z0-9-]/g, '');
  }
"""

# ---------------------------------------------------------------- 2
BOTAO_VELHO = """      + '    <button class="wcat-cta" type="button" disabled>Add to cart '
      + '<span>works on the live site, with WooCommerce</span></button>'"""

BOTAO_NOVO = """      + '    <div id="wcat-acao"></div>'"""

# ---------------------------------------------------------------- 3
ACAO = """
    function desenharAcao() {
      var alvo = document.getElementById('wcat-acao');
      if (!alvo) return;
      if (!LOJA_PRONTA) {
        alvo.innerHTML = '<button class="wcat-cta" type="button" disabled>'
          + 'Add to cart <span>the shop has no products yet</span></button>';
        return;
      }
      var url = BASE_PRODUTO + paraSlug(atual.d.nome) + '/'
        + '?attribute_pa_colour=' + encodeURIComponent(paraSlug(atual.a.nome))
        + '&attribute_pa_size=' + encodeURIComponent(paraSlug(atual.t.nome));
      alvo.innerHTML = '<a class="wcat-cta pronta" href="' + url + '">'
        + 'Add to cart <span>' + atual.d.nome + ' &middot; ' + atual.a.nome
        + ' &middot; size ' + atual.t.nome + '</span></a>';
    }
"""

j = io.open(ARQ, encoding='utf-8').read()

# 1. interruptor logo depois do 'use strict'
assert "'use strict';" in j
j = j.replace("  'use strict';\n", "  'use strict';\n" + INTERRUPTOR, 1)

# 2. o botao fixo vira um espaco que a funcao preenche
assert BOTAO_VELHO in j, 'nao achei o botao antigo'
j = j.replace(BOTAO_VELHO, BOTAO_NOVO, 1)

# 3. a funcao, declarada junto das outras de dentro de iniciar()
alvo = "    function repintar() {"
assert alvo in j
j = j.replace(alvo, ACAO.rstrip() + "\n\n" + alvo, 1)

# 4. repintar() passa a atualizar tambem o botao
alvo2 = """      document.getElementById('wcat-tam').innerHTML = TAMANHOS.map(function (t) {"""
assert alvo2 in j
j = j.replace(alvo2, alvo2, 1)
fecho = """        + t.nome + '<small>' + t.medida + '</small></button>';
      }).join('');
    }"""
assert fecho in j
j = j.replace(fecho, """        + t.nome + '<small>' + t.medida + '</small></button>';
      }).join('');
      desenharAcao();
    }""", 1)

io.open(ARQ, 'w', encoding='utf-8').write(j)
print('wng-catalogo.js ligado ao WooCommerce.')
print('  LOJA_PRONTA        :', 'false (botao ainda explica)' if 'var LOJA_PRONTA = false;' in j else '??')
print('  BASE_PRODUTO       :', re.search(r"var BASE_PRODUTO = '([^']+)'", j).group(1))
print('  funcao desenharAcao:', 'sim' if 'function desenharAcao' in j else 'NAO')
print('  tamanho do arquivo :', len(j))
