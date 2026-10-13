# Site da chapa Prisma

Site de campanha da chapa Prisma para o Grêmio Politécnico (Poli-USP). É uma página só, sem instalação nem etapa de build: tudo está em `index.html` (HTML, CSS e JavaScript no mesmo arquivo), mais o PDF da carta-programa. Publicar é dar push na branch `main`.

Contato da chapa: chapa.poli.prisma@gmail.com

## O que tem na página

| Seção | O que faz |
| --- | --- |
| Menu | Links das seções, "Como votar" (pop-up com datas e horários) e "Participe" |
| Início | Título, botões e atalhos para cada área de propostas |
| O que muda para você | Três resumos: contas, negócios e serviços |
| Propostas | Abas por área, busca, estrela de prioridade e a chamada da carta-programa |
| Carta-programa | Leitor do PDF com índice de tópicos, aberto pela chamada ou por qualquer cartão de proposta |
| Como vamos trabalhar | Regras, quadrados das frentes e organograma |
| Tem uma ideia? | Formulário que abre o e-mail da pessoa com a ideia pronta para a chapa |
| Perguntas frequentes | Lista `F` no script |
| Participe | Botão "Quero ajudar" abre um pop-up com e-mail e WhatsApp |

O site não guarda nada em servidor. As estrelas de prioridade ficam só no navegador de quem visita.

## Onde mexer no conteúdo

Tudo fica no `<script>` do fim do `index.html`, no bloco "MAPAS":

- `CARTA`: o PDF da carta-programa e o índice de tópicos.
- `P`: as áreas e as propostas (`t` título, `d` descrição, `c` tópico da carta, `lp:1` para prazo mais longo, `l` e `lt` para um link).
- `SQ`: os quadrados das frentes. Cada um lista os títulos das propostas que tratam dele, de qualquer área; uma proposta pode estar em mais de uma frente. Clicar no quadrado mostra só essas propostas. "Expansão" reúne toda ação que liga a Poli a agentes de fora (empresas, poder público, pessoas).
- `F`: perguntas frequentes.

O organograma e os textos fixos estão no HTML, na seção correspondente.

**A carta-programa é a fonte.** As propostas do site são o resumo dela, na mesma ordem e numeração. Sempre que a carta ou uma proposta mudar, revise os três mapas: os quadrados citam as propostas pelo título, e as propostas citam os tópicos pelo `id`. O console do navegador (F12) avisa quando um título, tópico ou proposta citado não é encontrado, e lista os subtópicos da carta que nenhuma proposta cita.

### Datas da eleição

O botão "Como votar", no menu, abre um pop-up com datas, horários, locais e o que levar. O texto está no HTML (`<dialog id="vote">`) e a mesma informação aparece resumida na pergunta "Quem pode votar", na lista `F`. As fontes são o Cronograma Eleitoral (CE.OPR.11) e o Regimento Eleitoral (CE.GOV.01) da Comissão Eleitoral. Se a Comissão alterar o cronograma, atualize os dois lugares. O link `#votar` abre o site já com esse pop-up.

## Carta-programa

O arquivo é `carta-programa.pdf`, na raiz. A versão publicada é a "vf 2" (16 páginas), ligada em 13/10/2026.

Como funciona:

- O PDF é desenhado na própria página com a biblioteca PDF.js, carregada do cdnjs só quando alguém abre a carta. Se ela não carregar, aparece um link para baixar o PDF.
- Ao abrir, a carta sobe do cartão em que a pessoa clicou e cresce até ocupar a tela; o site recua e some, e o índice desliza para o lugar dele, com os tópicos entrando em sequência. A coreografia está na função `cvAnim`, no script. O botão "Sair" (ou Esc, ou o voltar do navegador) faz o caminho inverso e devolve a pessoa ao mesmo ponto do site.
- Clicar num tópico rola o PDF até ele e sublinha o título. O sublinhado é um elemento por cima da página; o arquivo PDF não é alterado.
- O site acha cada título sozinho no texto do PDF: entre os trechos que casam com o `busca` do tópico, vale o de letra maior (o título de verdade, e não a linha do sumário ou uma menção no meio do texto). Por isso não há números de página no código, e mudar a paginação não quebra nada.
- Links diretos: `#carta` abre a carta e `#carta/id` abre já no tópico (por exemplo `#carta/triedro`). `#p-negocios` abre o site na área de propostas indicada e `#frente-expansao`, nas propostas de uma frente.
- O PDF precisa ter texto de verdade (exportado do editor). Num PDF escaneado, que é só imagem, não há como localizar os títulos.
- Se `CARTA.url` for `null`, a carta fica desligada: somem a chamada, o índice e os links dos cartões.

### Quando chegar uma versão nova da carta

1. Substitua `carta-programa.pdf` pelo arquivo novo, com o mesmo nome.
2. Em `CARTA.url`, aumente o número depois de `?v=` (de `?v=1` para `?v=2`, e assim por diante), para ninguém ver a versão antiga guardada pelo navegador.
3. Compare o sumário da versão nova com `CARTA.topicos` e ajuste o que mudou. Cada tópico é `{id, n, t, busca}`:
   - `id`: nome curto, sem espaços nem acentos (vira o link `#carta/id`). Não troque o `id` de um tópico que continua existindo.
   - `n`: a numeração como está no PDF (`"2"` para capítulo, `"2.1"` para subtópico, `""` para a nota final).
   - `t`: o título que aparece no índice.
   - `busca`: só quando o título no PDF ocupa mais de uma linha ou tem aspas; use o começo dele, como está escrito na primeira linha.
   - Mantenha a ordem do documento.
4. Releia a carta e ajuste as propostas em `P`: o que entrou, saiu ou mudou de redação, o campo `c` de cada uma e o `lp:1` nos trechos que a carta marca em itálico (prazo mais longo). Se uma área mudar de nome, ajuste também os atalhos do início (`hero-foot`).
5. Revise `SQ`: os títulos citados precisam existir em `P`, e um quadrado sem link pode ter ganhado proposta.
6. Teste (ver abaixo): abra a carta, clique em todos os tópicos e confira o sublinhado; abra alguns cartões pelo "Ver na carta-programa"; olhe o console.
7. Confira se os textos fixos continuam batendo com a carta: os três resumos de "O que muda para você" e as perguntas frequentes.

O número de propostas no texto de introdução é calculado sozinho.

### Como testar a carta antes de publicar

Abrir o `index.html` direto do disco não basta, porque o navegador bloqueia a leitura do PDF. Suba um servidor local na pasta do projeto e acesse `http://localhost:8000`:

```
python -m http.server 8000
```

## Publicação e versões

- `origin`: https://github.com/ChapaPrisma/site_chapa (branch `main`).
- Tags: `carta-programa-vf2` marca a carta ligada ao site; `preparo-carta-programa`, o leitor pronto ainda sem o PDF; `v1-identidade-original` e as branches `identidade-*`, as identidades visuais anteriores.
- O site está com `<meta name="robots" content="noindex">`, ou seja, fora dos buscadores. Retire essa linha quando quiser que ele apareça no Google.
