# Wrap N Glass — cópia de trabalho

Espelho estático de `https://wrapnglass.com/`, capturado em **28/08/2026**.
Feito por **Sites JM** para desenvolver as alterações antes de aplicá-las no
site real.

## O que isto é

Uma **foto** do site: 21 páginas, HTML/CSS/JS/imagens, idêntico ao original.

## O que isto NÃO é

Não é o WordPress rodando. **Carrinho, checkout, conta e formulários não
funcionam** — eles precisam do PHP e do banco de dados por trás. Aqui só a
camada visual está viva.

## Regra de trabalho

Todo CSS que a gente escrever vai em **`wng-custom.css`**, e só nele.

Motivo: no WordPress esse arquivo vira, sem alterar uma vírgula,
*Aparência → Personalizar → CSS adicional*. Ele está injetado como último
item do `<head>` nas 21 páginas — a mesma posição que o WordPress usa —,
então a cascata se comporta igual nos dois lugares.

**Nunca editar o CSS do tema.** Se editar, o trabalho não volta pro site real.

## Não indexar

Todas as páginas levam `noindex, nofollow`, há `robots.txt` bloqueando tudo
e o `vercel.json` manda o cabeçalho `X-Robots-Tag`. O site de verdade é
`https://wrapnglass.com/`.

## Como rodar na sua máquina

```bash
python -m http.server 8899
```

Depois abra `http://localhost:8899`. Precisa de servidor: os caminhos são
absolutos a partir da raiz e não funcionam abrindo o arquivo direto.

## Como o espelho foi feito

`_ferramentas/espelhar.py` — lê o sitemap, baixa páginas e ativos, reescreve
os endereços e injeta o `noindex`. Rodar de novo regenera tudo.
