# Site da chapa Prisma

Site de campanha da chapa Prisma para o Grêmio Politécnico (Poli-USP). É uma página só, sem instalação nem etapa de build: tudo está em `index.html` (HTML, CSS e JavaScript no mesmo arquivo). Publicar é dar push na branch `main`.

Contato da chapa: chapa.poli.prisma@gmail.com

## O que tem na página

| Seção | O que faz |
| --- | --- |
| Início | Título, botões e atalhos para cada área de propostas |
| O que muda para você | Três resumos: contas, negócios e serviços |
| Propostas | Abas por área, busca, estrela de prioridade e a chamada da carta-programa |
| Como vamos trabalhar | Regras, quadrados das frentes e organograma |
| Tem uma ideia? | Formulário que abre o e-mail da pessoa com a ideia pronta para a chapa |
| Perguntas frequentes | Lista `F` no script |
| Participe | Botão "Quero ajudar" abre um pop-up com e-mail e WhatsApp |

O site não guarda nada em servidor. As estrelas de prioridade ficam só no navegador de quem visita.

## Onde mexer no conteúdo

Tudo fica no `<script>` do fim do `index.html`:

- `P`: as áreas e as propostas (`t` título, `d` descrição, `lp:1` para longo prazo, `l` e `lt` para um link).
- `SQ`: os quadrados das frentes. Cada um aponta para uma área e lista os títulos das propostas que tratam dele. `null` vira "detalhes em breve".
- `F`: perguntas frequentes.
- `CARTA`: o PDF da carta-programa e o índice de tópicos (ver abaixo).

O organograma e os textos fixos estão no HTML, na seção correspondente.

**Sempre que mudar uma proposta, revise os mapas.** Os quadrados citam as propostas pelo título, então renomear ou apagar uma proposta quebra a ligação. O console do navegador (F12) mostra um aviso quando um título ou tópico citado não existe mais.

Trechos entre colchetes como `[CONFIRMAR: ...]` aparecem em amarelo no site: são informações que ainda faltam. A caixa "Destacar pendências", no rodapé, esconde o destaque.

## Carta-programa: o que fazer quando o PDF chegar

O leitor da carta já está pronto e fica desligado enquanto `CARTA.url` for `null`. Para ligar:

1. Salve o PDF na raiz do repositório, ao lado do `index.html` (por exemplo `carta-programa.pdf`).
2. No começo do script, preencha `CARTA`:

   ```js
   const CARTA={url:"carta-programa.pdf",topicos:[
     {id:"contas",   t:"Financeiro e contas", pag:3, busca:"1. Financeiro e contas"},
     {id:"raio-x",   t:"Raio-x das contas",   pag:3, busca:"Raio-x das contas", n2:1},
     {id:"negocios", t:"Negócios",            pag:5, busca:"2. Negócios"}
   ]};
   ```

   - `id`: nome curto, sem espaços nem acentos (vira o link `#carta/id`).
   - `t`: como o tópico aparece no índice.
   - `pag`: página do PDF em que o tópico começa.
   - `busca`: o título exatamente como está escrito no PDF. É esse texto que o site localiza e sublinha. Se não achar, rola até o topo da página e não sublinha.
   - `n2:1`: subtópico (aparece recuado).
   - Liste os tópicos na ordem em que aparecem no PDF.
3. Ligue as propostas aos tópicos em `P`, com o campo `c`:
   - na área, vale para todas as propostas dela: `{id:"negocios",n:"2",g:"Negócios",c:"negocios",b:[...]}`
   - numa proposta, vale mais que o da área: `{t:"Triedro sem fila",d:"...",c:"triedro"}`
4. Abra o site e confira: a chamada "Quer ver os detalhes?" passa a mostrar o botão, cada cartão de proposta ganha "Ver na carta-programa", e cada tópico do índice rola até o lugar certo e sublinha o título.
5. Revise os mapas (`SQ` e os campos `c`) e olhe o console em busca de avisos.

Como funciona, para quem for mexer:

- O PDF é desenhado na própria página com a biblioteca PDF.js, carregada do cdnjs só quando alguém abre a carta. Se ela não carregar, aparece um link para baixar o PDF.
- O sublinhado é um elemento por cima da página; o arquivo PDF não é alterado.
- Ao abrir, a carta cresce a partir de onde a pessoa clicou e o site encolhe para a coluna da esquerda, que vira o índice. O botão "Sair" (ou Esc, ou o voltar do navegador) faz o caminho inverso e devolve a pessoa ao mesmo ponto do site.
- Links diretos: `#carta` abre a carta e `#carta/id` abre já no tópico. `#p-negocios` abre o site na área de propostas indicada.
- O PDF precisa ter texto de verdade (exportado do editor). Num PDF escaneado, que é só imagem, o índice ainda rola até a página, mas não há o que sublinhar.

### Como testar a carta antes de publicar

Abrir o `index.html` direto do disco não basta, porque o navegador bloqueia a leitura do PDF. Suba um servidor local na pasta do projeto e acesse `http://localhost:8000`:

```
python -m http.server 8000
```

## Publicação e versões

- `origin`: https://github.com/ChapaPrisma/site_chapa (branch `main`).
- A tag `preparo-carta-programa` marca o ponto em que o leitor da carta ficou pronto, ainda sem o PDF.
- Identidades visuais anteriores continuam no histórico: tag `v1-identidade-original` e as branches `identidade-*`.
- O site está com `<meta name="robots" content="noindex">`, ou seja, fora dos buscadores. Retire essa linha quando quiser que ele apareça no Google.
