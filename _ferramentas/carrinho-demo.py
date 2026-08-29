# -*- coding: utf-8 -*-
"""
Da um carrinho de DEMONSTRACAO ao catalogo, so no espelho.

O PROBLEMA
O espelho e HTML estatico -- zero arquivos PHP. O "add to cart" do
WooCommerce faz um POST que nao tem para onde ir: nao ha servidor, nao ha
banco. Nenhuma compra pode funcionar ali, por melhor que seja o codigo.
Entao o botao ficava desativado e clicar nao dava nada.

A SAIDA
Um carrinho de mentirinha que roda no proprio navegador (localStorage).
Da para escolher design, cor e tamanho, adicionar, ver a lista, remover e
ver o total. E o suficiente para o Joao clicar e para MOSTRAR ao cliente
como vai funcionar.

⚠️ POR QUE ISTO NAO E O FORMULARIO MENTIROSO DE NOVO
O formulario de newsletter dizia "Thanks for subscribing!" num site NO AR,
para o cliente final, sem avisar. Este carrinho:
  - so existe no espelho (detecta o dominio; no site real nem carrega)
  - a pagina inteira ja se anuncia como prototipo
  - o painel do carrinho diz, em cima, que e demonstracao
  - nao existe botao de pagar, nao pede dado nenhum
Demonstracao anunciada e trabalho; simulacao disfarcada e mentira.

ONDE ELE NAO APARECE
`ehEspelho()` compara o dominio. Em wrapnglass.com o botao volta a ser o
link de verdade para o produto (ou o aviso, se a loja ainda estiver vazia).
"""
import io
import re

ARQ = 'wng-catalogo.js'

# --------------------------------------------------------------- 1
PRECOS = """
  /* Precos de exemplo, um por tamanho. Tem de bater com gerar-produtos.py
     -- `conferir-catalogo.py` compara. ⚠️ [A CONFIRMAR] com o dono. */
  var PRECOS = {
    'vehicle-wraps':       { '60 cm': 12, '120 cm': 18, '200 cm': 26, '300 cm': 34 },
    'marine-wraps':        { '150 cm': 22, '250 cm': 32, '400 cm': 44, '600 cm': 58 },
    'architectural-glass': { '91 cm': 16, '122 cm': 22, '152 cm': 28 }
  };

  /* O carrinho de demonstracao so roda no espelho. No site do cliente esta
     funcao devolve false e nada disto aparece. */
  function ehEspelho() {
    var h = location.hostname;
    return h === 'localhost' || h === '127.0.0.1' || h === '' ||
           /\\.vercel\\.app$/.test(h);
  }
"""

# --------------------------------------------------------------- 2
CARRINHO = """
    /* ==============================================================
       CARRINHO DE DEMONSTRACAO  (so no espelho -- ver ehEspelho)
       ============================================================== */
    var CHAVE = 'wng-carrinho-demo';

    function lerCarrinho() {
      try { return JSON.parse(localStorage.getItem(CHAVE)) || []; }
      catch (e) { return []; }
    }
    function gravarCarrinho(itens) {
      try { localStorage.setItem(CHAVE, JSON.stringify(itens)); } catch (e) {}
      pintarBotaoCarrinho();
    }
    function precoDe(d, t) {
      var tab = PRECOS[raiz.getAttribute('data-wng-catalogo')] || {};
      return tab[t.nome] || 0;
    }
    function totalCarrinho(itens) {
      return itens.reduce(function (s, i) { return s + i.preco * i.qtd; }, 0);
    }

    function pintarBotaoCarrinho() {
      var b = document.getElementById('wcat-cesta');
      if (!b) return;
      var itens = lerCarrinho();
      var n = itens.reduce(function (s, i) { return s + i.qtd; }, 0);
      b.hidden = n === 0;
      b.querySelector('.wcat-cesta-n').textContent = n;
      b.querySelector('.wcat-cesta-v').textContent =
        '\\u20ac' + totalCarrinho(itens).toFixed(2);
      b.setAttribute('aria-label', n + ' item(s) in the demo cart, total \\u20ac'
        + totalCarrinho(itens).toFixed(2) + '. Open cart.');
    }

    function adicionar() {
      var itens = lerCarrinho();
      var sku = atual.d.id + ' \\u00b7 ' + atual.a.nome + ' \\u00b7 ' + atual.t.nome;
      var achou = itens.filter(function (i) { return i.sku === sku; })[0];
      if (achou) { achou.qtd += 1; }
      else {
        itens.push({ sku: sku, design: atual.d.nome, ref: atual.d.id,
                     cor: atual.a.nome, destaque: atual.b.nome,
                     tam: atual.t.nome, nota: atual.t.medida,
                     preco: precoDe(atual.d, atual.t), qtd: 1 });
      }
      gravarCarrinho(itens);
      painel.close();
      abrirCesta();
    }

    function abrirCesta() {
      var d = document.getElementById('wcat-cesta-painel');
      var itens = lerCarrinho();
      var corpo = d.querySelector('.wcat-cesta-lista');
      if (!itens.length) {
        corpo.innerHTML = '<p class="wcat-cesta-vazia">Nothing here yet.</p>';
      } else {
        corpo.innerHTML = '<ul>' + itens.map(function (i, k) {
          return '<li><div><strong>' + i.design + '</strong> <span>' + i.ref
            + '</span><br><small>' + i.cor + ' + ' + i.destaque + ' \\u00b7 '
            + i.tam + ' \\u00b7 ' + i.nota + '</small></div>'
            + '<div class="wcat-cesta-dir"><span class="wcat-cesta-p">\\u20ac'
            + (i.preco * i.qtd).toFixed(2) + '</span>'
            + '<span class="wcat-cesta-q">\\u00d7' + i.qtd + '</span>'
            + '<button class="wcat-cesta-x" data-k="' + k
            + '" aria-label="Remove ' + i.design + '">Remove</button></div></li>';
        }).join('') + '</ul>'
          + '<p class="wcat-cesta-total">Total <strong>\\u20ac'
          + totalCarrinho(itens).toFixed(2) + '</strong></p>';
      }
      if (!d.open) d.showModal();
    }

    function montarCesta() {
      var b = document.createElement('button');
      b.id = 'wcat-cesta';
      b.type = 'button';
      b.hidden = true;
      b.innerHTML = '<span class="wcat-cesta-n">0</span>'
        + '<span class="wcat-cesta-v">\\u20ac0.00</span>';
      document.body.appendChild(b);

      var d = document.createElement('dialog');
      d.id = 'wcat-cesta-painel';
      d.innerHTML =
        '<form method="dialog" class="wcat-fechar-form">'
        + '<button class="wcat-fechar" aria-label="Close">&times;</button></form>'
        + '<div class="wcat-cesta-corpo">'
        + '<p class="wcat-cesta-aviso"><strong>Demonstration cart.</strong> '
        + 'This runs in your browser only, on the preview site. On the live '
        + 'site this is the WooCommerce cart. Prices are examples.</p>'
        + '<h2>Your selection</h2>'
        + '<div class="wcat-cesta-lista"></div>'
        + '<button class="wcat-cta" type="button" disabled>Checkout '
        + '<span>no payment method is connected yet</span></button>'
        + '</div>';
      document.body.appendChild(d);

      b.addEventListener('click', abrirCesta);
      d.addEventListener('click', function (e) {
        if (e.target === d) { d.close(); return; }
        var x = e.target.closest('.wcat-cesta-x');
        if (x) {
          var itens = lerCarrinho();
          itens.splice(+x.dataset.k, 1);
          gravarCarrinho(itens);
          abrirCesta();
        }
      });
      pintarBotaoCarrinho();
    }
"""

# --------------------------------------------------------------- 3
ACAO_NOVA = """
    function desenharAcao() {
      var alvo = document.getElementById('wcat-acao');
      if (!alvo) return;

      /* 1. no espelho: carrinho de demonstracao, para dar para clicar */
      if (ehEspelho()) {
        var p = precoDe(atual.d, atual.t);
        alvo.innerHTML = '<button class="wcat-cta pronta" type="button" '
          + 'id="wcat-add">Add to cart <span>'
          + (p ? '\\u20ac' + p.toFixed(2) + ' \\u00b7 example price \\u00b7 '
               : '') + 'demo</span></button>';
        document.getElementById('wcat-add').addEventListener('click', adicionar);
        return;
      }

      /* 2. site real, loja ainda sem produtos: explica, nao mente */
      if (!LOJA_PRONTA) {
        alvo.innerHTML = '<button class="wcat-cta" type="button" disabled>'
          + 'Add to cart <span>the shop has no products yet</span></button>';
        return;
      }

      /* 3. site real com produtos: link com a variacao ja escolhida */
      var url = BASE_PRODUTO + paraSlug(atual.d.nome) + '/'
        + '?attribute_pa_colour=' + encodeURIComponent(paraSlug(atual.a.nome))
        + '&attribute_pa_size=' + encodeURIComponent(paraSlug(atual.t.nome));
      alvo.innerHTML = '<a class="wcat-cta pronta" href="' + url + '">'
        + 'Add to cart <span>' + atual.d.nome + ' \\u00b7 ' + atual.a.nome
        + ' \\u00b7 size ' + atual.t.nome + '</span></a>';
    }
"""

j = io.open(ARQ, encoding='utf-8').read()

# 1. precos + detector de espelho, logo depois do interruptor
alvo = "  function paraSlug(t) {"
assert alvo in j
j = j.replace(alvo, PRECOS.rstrip() + "\n\n" + alvo, 1)

# 2. troca desenharAcao inteira
antiga = re.search(r'\n    function desenharAcao\(\) \{.*?\n    \}\n', j, re.S)
assert antiga, 'nao achei desenharAcao'
j = j[:antiga.start()] + "\n" + CARRINHO.rstrip() + "\n" + ACAO_NOVA.rstrip() + "\n" + j[antiga.end():]

# 3. monta a cesta no fim de iniciar()
alvo3 = "    /* CSV do WooCommerce, para quando o projeto for adiante */"
assert alvo3 in j
j = j.replace(alvo3, "    if (ehEspelho()) montarCesta();\n\n" + alvo3, 1)

io.open(ARQ, 'w', encoding='utf-8').write(j)
print('carrinho de demonstracao adicionado')
print('  ehEspelho()      :', 'sim' if 'function ehEspelho' in j else 'NAO')
print('  montarCesta()    :', 'sim' if 'function montarCesta' in j else 'NAO')
print('  tres estados     :', j.count('/* 1. no espelho') and j.count('/* 2. site real') and j.count('/* 3. site real'))
print('  tamanho          :', len(j))
