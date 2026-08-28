# -*- coding: utf-8 -*-
"""
Espelha wrapnglass.com como site estatico, pronto pra subir na Vercel.

O que ele faz:
  1. le o sitemap e junta todas as paginas e produtos
  2. baixa cada pagina
  3. baixa CSS, JS, imagens e fontes, inclusive os url(...) de dentro do CSS
  4. reescreve https://wrapnglass.com/ -> / (caminho a partir da raiz)
  5. injeta noindex em TODA pagina

Nao e o site funcionando. Carrinho, checkout e formulario precisam do
WordPress atras. Isso aqui e uma FOTO, pra olhar e pra mexer no visual.

Uso: python espelhar.py
"""
import io, os, re, sys, time, gzip, urllib.request, urllib.parse, urllib.error

BASE = "https://wrapnglass.com"
HOST = "wrapnglass.com"
SAIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site-espelho")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")

baixados = set()
falhas = []


def pegar(url, binario=False):
    """Baixa uma URL. Devolve bytes ou str."""
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept-Encoding": "gzip",
        "Accept": "*/*",
    })
    with urllib.request.urlopen(req, timeout=45) as r:
        dados = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            dados = gzip.decompress(dados)
    return dados if binario else dados.decode("utf-8", "replace")


def caminho_local(url):
    """URL do site -> caminho de arquivo dentro de site-espelho/."""
    p = urllib.parse.urlparse(url)
    caminho = urllib.parse.unquote(p.path)
    if caminho.endswith("/") or caminho == "":
        caminho = caminho + "index.html"
    elif "." not in os.path.basename(caminho):
        caminho = caminho + "/index.html"
    return os.path.join(SAIDA, caminho.lstrip("/").replace("/", os.sep))


def salvar(caminho, dados):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    modo = "wb" if isinstance(dados, bytes) else "w"
    with io.open(caminho, modo, **({} if isinstance(dados, bytes)
                                   else {"encoding": "utf-8"})) as f:
        f.write(dados)


def absolutizar(url, base):
    """Resolve //, /caminho e caminho relativo para URL completa."""
    if url.startswith("//"):
        return "https:" + url
    return urllib.parse.urljoin(base, url)


def do_site(url):
    return urllib.parse.urlparse(url).netloc.endswith(HOST)


def limpar_versao(url):
    """Tira ?ver=1.2.3 — no WordPress e so quebra-cache."""
    p = urllib.parse.urlparse(url)
    if not p.query:
        return url
    q = [(k, v) for k, v in urllib.parse.parse_qsl(p.query)
         if k not in ("ver", "v", "_")]
    return urllib.parse.urlunparse(p._replace(query=urllib.parse.urlencode(q)))


# ------------------------------------------------------------- 1. paginas
def listar_paginas():
    urls = {BASE + "/"}
    try:
        indice = pegar(BASE + "/wp-sitemap.xml")
    except Exception as e:
        print("  sitemap principal falhou:", e)
        return sorted(urls)
    for sub in re.findall(r"<loc>([^<]+)</loc>", indice):
        if "users" in sub:
            continue
        try:
            xml = pegar(sub)
            for u in re.findall(r"<loc>([^<]+)</loc>", xml):
                urls.add(u)
        except Exception as e:
            print("  falhou", sub, e)
        time.sleep(0.3)
    return sorted(urls)


# ------------------------------------------------------------- 2. ativos
RE_ATIVO = re.compile(
    r'(?:href|src|data-src|content)\s*=\s*["\']([^"\']+\.(?:css|js|png|jpe?g|gif|webp|avif|svg|ico|woff2?|ttf|otf|eot|mp4|webm))(\?[^"\']*)?["\']',
    re.I)
RE_SRCSET = re.compile(r'srcset\s*=\s*["\']([^"\']+)["\']', re.I)
RE_CSS_URL = re.compile(r'url\(\s*["\']?([^"\')]+)["\']?\s*\)', re.I)


def ativos_do_html(html, base):
    achados = set()
    for m in RE_ATIVO.finditer(html):
        achados.add(absolutizar(m.group(1), base))
    for m in RE_SRCSET.finditer(html):
        for parte in m.group(1).split(","):
            u = parte.strip().split(" ")[0]
            if u:
                achados.add(absolutizar(u, base))
    for m in RE_CSS_URL.finditer(html):
        u = m.group(1)
        if not u.startswith("data:"):
            achados.add(absolutizar(u, base))
    return {u for u in achados if do_site(u)}


def baixar_ativo(url, profundidade=0):
    url = limpar_versao(url)
    if url in baixados or not do_site(url):
        return
    baixados.add(url)
    try:
        ehcss = url.lower().split("?")[0].endswith(".css")
        dados = pegar(url, binario=not ehcss)
    except Exception as e:
        falhas.append((url, str(e)))
        return
    if ehcss:
        # dentro do CSS ainda ha fontes e imagens de fundo
        if profundidade < 3:
            for u in {absolutizar(m.group(1), url)
                      for m in RE_CSS_URL.finditer(dados)
                      if not m.group(1).startswith("data:")}:
                if do_site(u):
                    baixar_ativo(u, profundidade + 1)
        dados = dados.replace(BASE + "/", "/").replace("//" + HOST + "/", "/")
    salvar(caminho_local(url), dados)


# ------------------------------------------------------------- 3. pagina
NOINDEX = ('<meta name="robots" content="noindex, nofollow">\n'
           '<!-- COPIA DE TRABALHO - Sites JM. Nao indexar. '
           'O site real e https://wrapnglass.com/ -->\n')


def tratar_pagina(url):
    try:
        html = pegar(url)
    except Exception as e:
        falhas.append((url, str(e)))
        return set()
    ativos = ativos_do_html(html, url)
    # links e caminhos absolutos viram caminhos a partir da raiz
    html = html.replace(BASE + "/", "/").replace("//" + HOST + "/", "/")
    html = html.replace('href="' + BASE + '"', 'href="/"')
    # noindex logo depois do <head>
    html = re.sub(r"(<head[^>]*>)", r"\1\n" + NOINDEX, html, count=1, flags=re.I)
    salvar(caminho_local(url), html)
    return ativos


# ------------------------------------------------------------- roda
if __name__ == "__main__":
    print("1) lendo sitemap...")
    paginas = listar_paginas()
    print("   %d paginas" % len(paginas))

    todos_ativos = set()
    print("2) baixando paginas...")
    for i, u in enumerate(paginas, 1):
        a = tratar_pagina(u)
        todos_ativos |= a
        print("   [%d/%d] %s  (+%d ativos)" % (i, len(paginas), u[:70], len(a)))
        time.sleep(0.25)

    print("3) baixando %d ativos..." % len(todos_ativos))
    for i, u in enumerate(sorted(todos_ativos), 1):
        baixar_ativo(u)
        if i % 25 == 0:
            print("   %d/%d" % (i, len(todos_ativos)))
        time.sleep(0.08)

    # robots.txt proprio, bloqueando tudo
    salvar(os.path.join(SAIDA, "robots.txt"),
           "# Copia de trabalho. O site real e https://wrapnglass.com/\n"
           "User-agent: *\nDisallow: /\n")

    n = sum(len(f) for _, _, f in os.walk(SAIDA))
    tam = sum(os.path.getsize(os.path.join(r, f))
              for r, _, fs in os.walk(SAIDA) for f in fs)
    print("\nPRONTO: %d arquivos, %.1f MB em %s" % (n, tam / 1048576.0, SAIDA))
    if falhas:
        print("\n%d falhas:" % len(falhas))
        for u, e in falhas[:15]:
            print("  -", u[:80], "->", e[:60])
