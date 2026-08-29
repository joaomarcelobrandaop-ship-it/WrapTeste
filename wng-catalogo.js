/* =====================================================================
   WRAP N GLASS — catálogo de designs com personalização
   Sites JM · 28/08/2026
   =====================================================================

   ⚠️ ISTO É UM PROTÓTIPO. Os designs são gerados por código, não são os
   arquivos reais do cliente. Preço, medida e nome estão marcados com
   [PREENCHER] de propósito — regra 2 do método Sites JM: não se inventa
   número, nome nem promessa.

   ---------------------------------------------------------------------
   COMO ISTO VIRA WORDPRESS

   Esta página é a APARÊNCIA do catálogo. No site real, ela é substituída
   por duas coisas:

     · a grade  → arquivo de categoria do WooCommerce
     · cor e tamanho → PRODUTO VARIÁVEL, com "Cor" e "Tamanho" como
       atributos. As amostras clicáveis (em vez da lista suspensa padrão)
       precisam de um plugin do tipo "Variation Swatches for WooCommerce".

   Os produtos entram por CSV (WooCommerce → Produtos → Importar). Este
   arquivo gera o CSV correspondente em `window.wngCatalogo.paraCSV()`.

   ---------------------------------------------------------------------
   POR QUE OS DESIGNS SÃO SVG E NÃO IMAGEM

   Porque o pedido era "mesmo design, cores diferentes". Com SVG a cor é
   um atributo do desenho e troca na hora, sem gerar uma imagem por
   combinação. Com JPG seriam 9 designs × 6 cores = 54 arquivos.
   ===================================================================== */

(function () {
  'use strict';

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
    return String(t).toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
  }

  /* ---------------------------------------------------------------
     1. PALETA — as cores que o cliente ofereceria
     As duas primeiras são as da marca; o resto são cores comuns de
     vinil automotivo. ⚠️ [PREENCHER] confirmar a cartela real dele.
     --------------------------------------------------------------- */
  var CORES = [
    { id: 'navy',   nome: 'Navy',      hex: '#002046', claro: false },
    { id: 'pink',   nome: 'Hot Pink',  hex: '#FF2362', claro: false },
    { id: 'branco', nome: 'White',    hex: '#FFFFFF', claro: true  },
    { id: 'prata',  nome: 'Silver',     hex: '#B9C0C9', claro: true  },
    { id: 'ouro',   nome: 'Gold',      hex: '#C9A227', claro: false },
    { id: 'verde',  nome: 'Green',     hex: '#0E8F5B', claro: false },
    { id: 'laranja',nome: 'Orange',   hex: '#EE5B1F', claro: false },
    { id: 'preto',  nome: 'Black',     hex: '#14161A', claro: false }
  ];

  /* ---------------------------------------------------------------
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
  };

  /* ---------------------------------------------------------------
     3. OS DESENHOS
     Cada um é uma função que devolve caminhos SVG. `a` é a cor
     principal, `b` a secundária. Assim a mesma forma serve a qualquer
     combinação de cores — que é o ponto do pedido.
     --------------------------------------------------------------- */
  var VB = '0 0 300 160';

  function lasca(a, b) {
    return '<path fill="' + a + '" d="M0 96 L118 22 L166 40 L44 118 Z"/>'
         + '<path fill="' + b + '" d="M32 130 L150 52 L182 66 L64 146 Z"/>'
         + '<path fill="' + a + '" d="M150 28 L262 -4 L300 12 L188 48 Z" opacity=".85"/>'
         + '<path fill="' + b + '" d="M196 92 L300 58 L300 78 L206 110 Z"/>';
  }
  function raio(a, b) {
    return '<path fill="' + a + '" d="M0 118 L96 40 L84 76 L166 30 L120 92 L152 84 L38 152 Z"/>'
         + '<path fill="' + b + '" d="M172 122 L246 52 L238 82 L300 44 L262 108 L286 102 L214 148 Z" opacity=".9"/>';
  }
  function onda(a, b) {
    return '<path fill="' + a + '" d="M0 104 C60 60 110 132 168 88 C214 54 258 118 300 78 L300 128 C258 164 214 104 168 134 C110 172 60 104 0 146 Z"/>'
         + '<path fill="' + b + '" d="M0 70 C56 34 108 96 162 56 C210 20 256 84 300 46 L300 62 C256 100 210 38 162 74 C108 116 56 52 0 90 Z" opacity=".85"/>';
  }
  function respingo(a, b) {
    return '<path fill="' + a + '" d="M6 132 C50 76 106 128 148 78 C186 34 240 96 296 44 L300 88 C246 132 190 82 152 122 C112 164 56 116 10 156 Z"/>'
         + '<circle cx="228" cy="34" r="13" fill="' + b + '"/>'
         + '<circle cx="264" cy="20" r="8" fill="' + b + '" opacity=".8"/>'
         + '<circle cx="196" cy="20" r="6" fill="' + b + '" opacity=".65"/>';
  }
  function fosco(a, b) {
    var s = '<rect x="0" y="0" width="300" height="160" fill="' + a + '" opacity=".16"/>';
    for (var i = 0; i < 22; i++) {
      s += '<rect x="' + (i * 14) + '" y="0" width="5" height="160" fill="' + a + '" opacity="'
        + (0.16 + (i % 4) * 0.12).toFixed(2) + '"/>';
    }
    s += '<rect x="0" y="58" width="300" height="7" fill="' + b + '"/>';
    return s;
  }
  function favo(a, b) {
    var s = '', k = 0;
    for (var y = 8; y < 160; y += 26) {
      for (var x = ((k % 2) ? 22 : 8); x < 300; x += 28) {
        s += '<polygon points="' + [x, y + 8, x + 8, y, x + 20, y, x + 28, y + 8,
          x + 20, y + 16, x + 8, y + 16].join(' ') + '" fill="' + a + '" opacity="'
          + (0.2 + ((x + y) % 3) * 0.22).toFixed(2) + '"/>';
      }
      k++;
    }
    s += '<rect x="0" y="72" width="300" height="5" fill="' + b + '"/>';
    return s;
  }
  function traco(a, b) {
    return '<path fill="' + a + '" d="M0 78 L300 44 L300 66 L0 100 Z"/>'
         + '<path fill="' + b + '" d="M0 108 L300 74 L300 86 L0 120 Z" opacity=".9"/>'
         + '<path fill="' + a + '" d="M0 54 L300 20 L300 28 L0 62 Z" opacity=".55"/>';
  }
  function garra(a, b) {
    var s = '';
    for (var i = 0; i < 5; i++) {
      var o = i * 18;
      s += '<path fill="' + (i % 2 ? b : a) + '" opacity="' + (1 - i * 0.13).toFixed(2)
        + '" d="M' + (10 + o) + ' 150 C' + (60 + o) + ' 96 ' + (96 + o) + ' 60 '
        + (170 + o) + ' 14 L' + (186 + o) + ' 34 C' + (120 + o) + ' 74 ' + (84 + o)
        + ' 108 ' + (34 + o) + ' 156 Z"/>';
    }
    return s;
  }
  function grade(a, b) {
    var s = '';
    for (var x = 0; x <= 300; x += 20) s += '<rect x="' + x + '" y="0" width="2" height="160" fill="' + a + '" opacity=".35"/>';
    for (var y = 0; y <= 160; y += 20) s += '<rect x="0" y="' + y + '" width="300" height="2" fill="' + a + '" opacity=".35"/>';
    s += '<circle cx="150" cy="80" r="46" fill="none" stroke="' + b + '" stroke-width="7"/>';
    s += '<circle cx="150" cy="80" r="18" fill="' + b + '" opacity=".7"/>';
    return s;
  }

  /* ---------------------------------------------------------------
     4. O CATÁLOGO POR CATEGORIA
     ⚠️ Nomes com número são de propósito: não inventar nome comercial
     que pareça um produto real do cliente.
     --------------------------------------------------------------- */
  var FAMILIAS = {
    'vehicle-wraps': {
      titulo: 'Vehicle Wraps',
      linha: 'Ready-to-cut stripe designs for vehicle doors, hoods and sides.',
      desenhos: [
        { id: 'VW-01', f: lasca,  nome: 'Shard' },
        { id: 'VW-02', f: raio,   nome: 'Bolt' },
        { id: 'VW-03', f: traco,  nome: 'Sweep' },
        { id: 'VW-04', f: garra,  nome: 'Claw' },
        { id: 'VW-05', f: lasca,  nome: 'Shard Wide', espelhar: true },
        { id: 'VW-06', f: raio,   nome: 'Bolt Mirror', espelhar: true }
      ]
    },
    'marine-wraps': {
      titulo: 'Marine Wraps',
      linha: 'Hull and deck graphics, cut-ready for boats and jet skis.',
      desenhos: [
        { id: 'MW-01', f: onda,     nome: 'Swell' },
        { id: 'MW-02', f: respingo, nome: 'Spray' },
        { id: 'MW-03', f: traco,    nome: 'Waterline' },
        { id: 'MW-04', f: garra,    nome: 'Wake' },
        { id: 'MW-05', f: onda,     nome: 'Swell Deep', espelhar: true },
        { id: 'MW-06', f: respingo, nome: 'Spray Mirror', espelhar: true }
      ]
    },
    'architectural-glass': {
      titulo: 'Architectural Glass',
      linha: 'Frosted and privacy films for windows, doors and partitions.',
      desenhos: [
        { id: 'AG-01', f: fosco, nome: 'Line Frost' },
        { id: 'AG-02', f: favo,  nome: 'Honey' },
        { id: 'AG-03', f: grade, nome: 'Grid' },
        { id: 'AG-04', f: fosco, nome: 'Line Frost Dense', espelhar: true },
        { id: 'AG-05', f: favo,  nome: 'Honey Wide', espelhar: true },
        { id: 'AG-06', f: grade, nome: 'Grid Mirror', espelhar: true }
      ]
    }
  };

  function svg(d, corA, corB, alt) {
    return '<svg viewBox="' + VB + '" role="img" aria-label="' + alt + '" '
      + 'preserveAspectRatio="xMidYMid slice"' + (d.espelhar ? ' style="transform:scaleX(-1)"' : '') + '>'
      + '<rect width="300" height="160" fill="#F5F7FA"/>' + d.f(corA, corB) + '</svg>';
  }

  /* ---------------------------------------------------------------
     5. MONTAGEM DA PÁGINA
     --------------------------------------------------------------- */
  function iniciar() {
    var raiz = document.querySelector('[data-wng-catalogo]');
    if (!raiz) return;
    var fam = FAMILIAS[raiz.getAttribute('data-wng-catalogo')];
    if (!fam) return;

    var padA = CORES[0], padB = CORES[1];
    /* a regua de tamanho depende da familia desta pagina */
    var TAMS = TAMANHOS[raiz.getAttribute('data-wng-catalogo')] || [];

    /* o aviso e o <h1> ficam no HTML estático da página, não aqui.
       Assim, se este script falhar, a página ainda tem cabeçalho e
       explicação em vez de ficar em branco — e o <h1> existe pro leitor
       de tela e pro Google mesmo sem JavaScript. */
    var h = '<ul class="wcat-grade">';

    fam.desenhos.forEach(function (d, i) {
      h += '<li class="wcat-item"><button class="wcat-cartao" data-i="' + i + '" '
        + 'aria-haspopup="dialog"><span class="wcat-arte">'
        + svg(d, padA.hex, padB.hex, d.nome + ' preview')
        + '</span><span class="wcat-info"><span class="wcat-nome">' + d.nome + '</span>'
        + '<span class="wcat-ref">' + d.id + '</span>'
        + '<span class="wcat-preco">[TO CONFIRM]</span></span></button></li>';
    });
    h += '</ul>';

    /* o painel de personalização */
    h += '<dialog class="wcat-painel" aria-labelledby="wcat-t">'
      + '<form method="dialog" class="wcat-fechar-form">'
      + '<button class="wcat-fechar" aria-label="Close">&times;</button></form>'
      + '<div class="wcat-corpo">'
      + '  <div class="wcat-previa" id="wcat-previa"></div>'
      + '  <div class="wcat-opcoes">'
      + '    <p class="wcat-ref" id="wcat-ref"></p>'
      + '    <h2 id="wcat-t"></h2>'
      + '    <fieldset class="wcat-grupo"><legend>Main colour</legend>'
      + '      <div class="wcat-amostras" id="wcat-cA"></div></fieldset>'
      + '    <fieldset class="wcat-grupo"><legend>Accent colour</legend>'
      + '      <div class="wcat-amostras" id="wcat-cB"></div></fieldset>'
      + '    <fieldset class="wcat-grupo"><legend>Size</legend>'
      + '      <div class="wcat-tams" id="wcat-tam"></div></fieldset>'
      + '    <p class="wcat-resumo" id="wcat-resumo"></p>'
      + '    <p class="wcat-precao">[TO CONFIRM] price</p>'
      + '    <div id="wcat-acao"></div>'
      + '  </div></div></dialog>';

    raiz.insertAdjacentHTML('beforeend', h);

    var painel = raiz.querySelector('.wcat-painel');
    var atual = { d: null, a: padA, b: padB, t: TAMS[1] || TAMS[0] };

    function amostras(alvo, sel, onde) {
      onde.innerHTML = CORES.map(function (c) {
        return '<button type="button" class="wcat-amostra' + (c.id === sel.id ? ' ativa' : '')
          + (c.claro ? ' clara' : '') + '" data-cor="' + c.id + '" data-alvo="' + alvo
          + '" style="--c:' + c.hex + '" aria-pressed="' + (c.id === sel.id) + '">'
          + '<span class="sr">' + c.nome + '</span></button>';
      }).join('');
    }


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

    function repintar() {
      document.getElementById('wcat-previa').innerHTML =
        svg(atual.d, atual.a.hex, atual.b.hex, atual.d.nome + ' in ' + atual.a.nome + ' and ' + atual.b.nome);
      document.getElementById('wcat-resumo').textContent =
        atual.d.nome + ' · ' + atual.a.nome + ' + ' + atual.b.nome
        + ' · size ' + atual.t.nome + ' (' + atual.t.medida + ')';
      amostras('a', atual.a, document.getElementById('wcat-cA'));
      amostras('b', atual.b, document.getElementById('wcat-cB'));
      document.getElementById('wcat-tam').innerHTML = TAMS.map(function (t) {
        return '<button type="button" class="wcat-tam' + (t.id === atual.t.id ? ' ativa' : '')
          + '" data-tam="' + t.id + '" aria-pressed="' + (t.id === atual.t.id) + '">'
          + t.nome + '<small>' + t.medida + '</small></button>';
      }).join('');
      desenharAcao();
    }

    raiz.addEventListener('click', function (e) {
      var cartao = e.target.closest('.wcat-cartao');
      if (cartao) {
        atual.d = fam.desenhos[+cartao.dataset.i];
        document.getElementById('wcat-t').textContent = atual.d.nome;
        document.getElementById('wcat-ref').textContent = atual.d.id;
        repintar();
        painel.showModal();
        return;
      }
      if (e.target === painel) { painel.close(); return; }
      var am = e.target.closest('.wcat-amostra');
      if (am) {
        var c = CORES.filter(function (x) { return x.id === am.dataset.cor; })[0];
        atual[am.dataset.alvo] = c;
        repintar();
        return;
      }
      var tm = e.target.closest('.wcat-tam');
      if (tm) {
        atual.t = TAMS.filter(function (x) { return x.id === tm.dataset.tam; })[0];
        repintar();
      }
    });

    /* CSV do WooCommerce, para quando o projeto for adiante */
    window.wngCatalogo = {
      paraCSV: function () {
        var l = ['Type,SKU,Name,Published,Parent,"Attribute 1 name","Attribute 1 value(s)","Attribute 1 visible","Attribute 1 global","Attribute 2 name","Attribute 2 value(s)","Attribute 2 visible","Attribute 2 global",Categories'];
        var cores = CORES.map(function (c) { return c.nome; }).join(', ');
        var tams = TAMS.map(function (t) { return t.nome; }).join(', ');
        fam.desenhos.forEach(function (d) {
          l.push(['variable', d.id, '"' + d.nome + '"', 1, '', 'Cor', '"' + cores + '"', 1, 1,
                  'Tamanho', '"' + tams + '"', 1, 1, '"' + fam.titulo + '"'].join(','));
        });
        return l.join('\n');
      }
    };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', iniciar);
  } else {
    iniciar();
  }
})();
