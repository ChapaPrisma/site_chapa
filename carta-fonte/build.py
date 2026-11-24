#!/usr/bin/env python3
"""Gera a carta-proposta (versão do site) a partir de conteudo.txt. Uso: python3 build.py saida.pdf"""
import asyncio, html, re, subprocess, sys, os
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
AZ, LA, AM, LI, OFF = '#0F2347', '#FF6B3D', '#FFC845', '#C9A7FF', '#F8F6F2'
SIMB = ("<polygon points='122,8 12,81 123,148' fill='#FFC845'/>"
        "<polygon points='132,9 371,156 260,230 132,153' fill='#FF6B3D'/>"
        "<polygon points='10,88 123,156 123,324 9,404' fill='#F8F6F2'/>"
        "<polygon points='132,240 193,200 252,235 132,319' fill='#C9A7FF'/>")
SIMB_CLARO = SIMB.replace("fill='#F8F6F2'", "fill='#0F2347'")

def e(s):
    return html.escape(s, quote=False)

def inline(s):
    s = e(s)
    # "Rótulo: texto" no começo de item de lista vira negrito
    return s

def bullet(s):
    m = re.match(r'^([^:]{2,48}):\s(.*)$', s)
    if m:
        return f"<li><b>{e(m.group(1))}:</b> {e(m.group(2))}</li>"
    return f"<li>{e(s)}</li>"

# ---------- blocos especiais ----------
RDS = [
    ("Congregação", "instância máxima da Poli", "7 + 7", "Plano Diretor aberto aos estudantes e posições da Escola construídas com consulta aos alunos."),
    ("CG", "Comissão de Graduação", "3 + 3", "Regras de estágio que não atrapalhem quem trabalha, transições curriculares sem prejuízo e recursos com prazos conhecidos."),
    ("CCB", "Comissão do Ciclo Básico", "4 + 4", "Pilar padronizado, calendário de provas sem semanas sobrecarregadas e vagas suficientes nas disciplinas que mais travam a grade."),
    ("CCEx", "Comissão de Cultura e Extensão", "2 + 2", "Informação clara sobre cada atividade de extensão, editais para os grupos e credenciamento do Engenharia na Prática."),
    ("CIP", "Comissão de Inclusão e Pertencimento", "2 + 2", "Permanência, acessibilidade a partir do Mapa de problemas, acolhimento e saúde mental."),
    ("CTA", "Conselho Técnico-Administrativo", "1 + 1", "Defesa dos espaços dos CAs, dos coletivos e do Escritório Piloto, e alunos no Plano Diretor."),
    ("CBiblio", "Comissão de Bibliotecas", "1 + 1", "Mais horários e lugares para estudar, e acervo e salas no Portal."),
]
PROJ = [
    ("Autoatendimento no Triedro", "Estudar e prototipar o autoatendimento para compras rápidas.", "6.1"),
    ("Triedro eficiente", "Filas, estoque, cardápio e desperdício estudados com dados reais.", "6.1"),
    ("Casa do Politécnico", "Continuar o estudo de viabilidade da reconstrução da CADOPÔ.", "5.3"),
    ("Diagnóstico dos espaços", "Transformar o Mapa de problemas num diagnóstico técnico de acessibilidade, tomadas e bebedouros.", "2.3"),
    ("Portal e Memória", "Novas partes do Portal, como a Memória da Representação e o rastreador.", "2.4"),
]
NUMS = [("1.000+", "estudantes de escolas públicas no Poli Vai à Escola"), ("75", "alunas do ensino médio no Meninas na Poli em 2025"),
        ("900+", "auxílios para idiomas na Poliglota"), ("50+", "grupos na Feira de Extensão de 2026")]
TRI = [("< R$ 8 mil", "faturamento do Triedro em janeiro"), ("> R$ 165 mil", "faturamento do Triedro em maio")]
PORTAL = [("Bandejões", "Cardápio do dia, o que está aberto agora e o caminho a pé."),
          ("Salas e grade", "Salas livres agora e montador de grade, com dados do USPolis e do JúpiterWeb."),
          ("Guia dos cursos", "Escrito pelos CAs, com as matérias do primeiro semestre."),
          ("Demandas", "Mapa de problemas do campus e contato com cada diretoria."),
          ("Transparência", "Saldo, dívida, gráfico mensal e extrato, prontos para a gestão."),
          ("Sou bixo burro", "Manual do bixo e as vantagens de quem acabou de entrar.")]

def bloco(nome):
    if nome == 'rds':
        rows = "".join(f"<tr><td><b>{a}</b><small>{b}</small></td><td class='cad'>{c}</td><td>{d}</td></tr>" for a, b, c, d in RDS)
        return f"<table class='tab rds'><thead><tr><th>Colegiado</th><th>Cadeiras</th><th>O que vamos defender</th></tr></thead><tbody>{rows}</tbody></table><p class='nota'>Cadeiras: titulares + suplentes. As CoCs e os Conselhos de Departamento têm RDs indicados pelos CAs, e o Grêmio trabalha junto com eles.</p>"
    if nome == 'projetos':
        rows = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td class='cad'>{c}</td></tr>" for a, b, c in PROJ)
        return f"<table class='tab'><thead><tr><th>Projeto</th><th>O que faz</th><th>Ver</th></tr></thead><tbody>{rows}</tbody></table>"
    if nome == 'numeros':
        return "<div class='nums'>" + "".join(f"<div><b>{a}</b><span>{b}</span></div>" for a, b in NUMS) + "</div>"
    if nome == 'triedro':
        return ("<div class='nums dois'>" + "".join(f"<div><b>{a}</b><span>{b}</span></div>" for a, b in TRI) +
                "</div><p class='nota'>Demonstração financeira do Triedro de outubro de 2024 a setembro de 2025.</p>")
    if nome == 'portal':
        return "<div class='feat'>" + "".join(f"<div><b>{a}</b><span>{b}</span></div>" for a, b in PORTAL) + "</div>"
    raise ValueError(nome)

# ---------- capítulos ----------
def capitulos():
    txt = open('conteudo.txt', encoding='utf-8').read()
    caps, cur, sec = [], None, None
    for raw in txt.splitlines():
        line = raw.rstrip()
        if not line:
            continue
        if line.startswith('# '):
            n, t = [x.strip() for x in line[2:].split('|')]
            cur = {'n': n, 't': t, 'lead': '', 'secs': []}; caps.append(cur); sec = None
        elif line.startswith('> '):
            cur['lead'] = line[2:]
        elif line.startswith('## '):
            n, t = [x.strip() for x in line[3:].split('|')]
            sec = {'n': n, 't': t, 'body': []}; cur['secs'].append(sec)
        else:
            sec['body'].append(line)
    return caps

def corpo(lines):
    out, ul = [], []
    def flush():
        if ul:
            out.append("<ul>" + "".join(ul) + "</ul>"); ul.clear()
    for l in lines:
        if l.startswith('- '):
            ul.append(bullet(l[2:])); continue
        flush()
        if l.startswith('### '):
            out.append(f"<h3>{e(l[4:])}</h3>")
        elif l.startswith('=> '):
            out.append(f"<p class='res'><span>Resultado esperado</span>{e(l[3:][0].upper() + l[4:])}</p>")
        elif l.startswith('!'):
            out.append(bloco(l[1:]))
        else:
            out.append(f"<p>{e(l)}</p>")
    flush()
    return "".join(out)

GEO_BAND = (f"<svg class='geo' viewBox='0 0 120 42' preserveAspectRatio='xMaxYMin meet'>"
            f"<polygon points='120,0 120,42 78,0' fill='{LI}'/><polygon points='84,42 120,42 102,24' fill='{LA}' opacity='0'/>"
            f"<polygon points='96,0 70,26 58,0' fill='{LA}'/><polygon points='70,42 50,42 70,22' fill='{AM}'/></svg>")

NOVA = set()
def cap_html(c):
    secs = "".join(
        f"<div class='sec'><span class='sn'>{s['n']}</span><div class='sb'><h2>{e(s['t'])}</h2>{corpo(s['body'])}</div></div>"
        for s in c['secs'])
    cls = 'cap nova' if c['n'] in NOVA else 'cap'
    return (f"<section class='{cls}' id='cap{c['n']}'><header class='band'>{GEO_BAND}<span class='cn'>{c['n']}</span>"
            f"<h1>{e(c['t'])}</h1></header><div class='flow'><p class='lead'>{e(c['lead'])}</p>{secs}</div></section>")

# ---------- páginas fixas ----------
COMPROMISSOS = [
    ("Raio-X das Contas", "Levantar dívidas, compromissos e patrimônio e publicar o relatório até o fim do primeiro bimestre."),
    ("Contas abertas todo mês", "Receitas, despesas, dívida e resultado de cada empresa no Portal, para qualquer aluno conferir."),
    ("Parcerias com regras públicas", "Todo dinheiro no balanço e nenhum acordo que limite as posições do Grêmio."),
    ("RDs em 7 colegiados", "Com coordenação própria, formação para quem chega e reuniões preparadas com dados."),
    ("Consulta antes do voto", "Nas pautas de grande impacto, os alunos opinam pelo Portal antes de os RDs votarem."),
    ("Memória da Representação", "Casos, atas e decisões guardados para cada turma de RDs continuar o trabalho da anterior."),
    ("Prestar contas de cada voto", "Resumo de toda reunião em até sete dias e um rastreador público de demandas."),
    ("Fuja do Nabo", "Juntar o Fuja das P2 e o Fuja das P3 e ampliar para P1, P2 e P3 de mais disciplinas."),
    ("Pré-cálculo", "Curso de nivelamento feito com os CAs, pronto antes das aulas dos ingressantes de 2028."),
    ("Engenharia na Prática", "Projetos reais de engenharia para alunos de qualquer curso, com professor orientador."),
    ("Ações sociais ampliadas", "Poli Vai à Escola, Meninas na Poli e Semana da Mulher Politécnica com mais alcance."),
    ("Comissão Contra Opressão", "Equipe de três pessoas e procedimentos de acolhimento antes da divulgação do canal."),
    ("Escritório Piloto com os coletivos", "O espaço continua com os coletivos, e o Grêmio o defende nas instâncias da Escola."),
    ("Triedro sem fila e nas férias", "Autoatendimento e pedido pelo Portal estudados, e vendas para quem fica no campus."),
    ("Portal Politécnico", "No ar na Semana de Recepção de 2027. O aplicativo vem depois, ao longo da gestão."),
    ("Calourada e IntegraPoli", "O Bixopp de volta, sem prejuízo ao caixa, e apoio às tradições da Escola."),
    ("Memorial do Grêmio", "123 anos de arquivo abertos no Portal, começando pelo Acervo da Resistência."),
    ("Casa do Politécnico", "Continuar o estudo de viabilidade da moradia estudantil, com grupos e parceiros."),
]

REGRAS = [
    ("Cada um no seu quadrado.", "Cada área tem um responsável. Todos opinam, mas decide quem responde pela área, e quem entra para tocar um projeto não precisa participar da parte política."),
    ("Resultado público.", "Metas e indicadores de cada área num painel mensal, e demonstrações financeiras a cada trimestre."),
    ("Estudar antes de gastar.", "Projeto com custo relevante só começa depois de um estudo de viabilidade."),
    ("Prioridades claras.", "Nem tudo começa ao mesmo tempo. Contas e representação vêm primeiro, e cada proposta diz do que depende."),
    ("Porta aberta.", "Para ajudar num projeto do Grêmio não é preciso ter cargo, e quem ajuda recebe crédito."),
    ("Participação com regras.", "Assembleia, plebiscitos e reuniões abertas, cada um com o seu papel."),
]

ANO = [
    ("Antes da posse", "transição", ["Pedido formal de documentos à gestão atual", "Conversa com funcionários e equipes dos projetos", "Montagem das equipes"]),
    ("Primeiros meses", "arrumar a casa", ["Raio-X das Contas e primeiro balanço público", "Coordenação da Representação", "Portal oficial na Semana de Recepção", "Calourada, se viável", "Equipe e procedimentos da CCO"]),
    ("1º semestre", "começar a entregar", ["1ª chamada e 1ª Mostra do Engenharia na Prática", "Memória da Representação no ar", "Fuja do Nabo com P1 e P3 do ciclo básico", "Primeiro Raio-X da Graduação"]),
    ("2º semestre", "crescer", ["2ª chamada e 2ª Mostra de Projetos", "Vagas de estágio e rastreador de demandas", "Pré-cálculo para os ingressantes de 2028", "Aplicativo em desenvolvimento"]),
    ("Fim do mandato", "passar o bastão", ["Dossiês de transição completos", "Relatório final da gestão", "Reunião de passagem com a próxima gestão e os novos RDs"]),
]

def capa():
    tri = (f"<svg class='tri' viewBox='0 0 210 120' preserveAspectRatio='none'>"
           f"<polygon points='0,120 0,62 44,120' fill='{AM}'/>"
           f"<polygon points='92,120 210,0 210,120' fill='{LI}'/>"
           f"<polygon points='92,120 210,0 210,22 118,120' fill='{LA}'/></svg>")
    tri_top = (f"<svg class='tri-top' viewBox='0 0 80 80'><polygon points='80,0 80,80 0,0' fill='{LA}'/>"
               f"<polygon points='80,0 80,34 46,0' fill='{AM}'/></svg>")
    return (f"<section class='capa'>{tri_top}<img class='logo' src='prisma-logo-fundo-escuro.svg' alt='Prisma, Grêmio Politécnico'>"
            f"<div class='capa-txt'><span class='kick'>Chapa Prisma · gestão 2027</span><h1>Carta-proposta</h1><i class='rule'></i>"
            f"<p class='lema'>Diferentes perspectivas.<br>Uma só Poli.</p><p class='ver'>Grêmio Politécnico da USP · novembro de 2026</p></div>{tri}</section>")

def sumario(pgs):
    caps = capitulos()
    itens = [("", "Nossos compromissos", "comp", []), ("", "Lembra do dia em que entrou na Poli?", "abertura", [])]
    for c in caps:
        itens.append((c['n'], c['t'], f"cap{c['n']}", [(s['n'], s['t']) for s in c['secs']]))
    itens += [("", "O primeiro ano", "ano", []), ("", "Nota final e como votar", "final", [])]
    def li(n, t, k, subs):
        p = pgs.get(k, '')
        sub = "".join(f"<li><span>{sn}</span>{e(st)}</li>" for sn, st in subs)
        return (f"<div class='si'><div class='sl'><span class='sn2'>{n}</span><b>{e(t)}</b><i></i><em>{p}</em></div>"
                + (f"<ul>{sub}</ul>" if sub else "") + "</div>")
    meio = (len(itens) + 2) // 2
    col1 = "".join(li(*x) for x in itens[:7]); col2 = "".join(li(*x) for x in itens[7:])
    return (f"<section class='pg sumario'><span class='kick'>Carta-proposta</span><h1 class='titulo'>Sumário</h1>"
            f"<div class='cols'><div>{col1}</div><div>{col2}</div></div>"
            f"<div class='comoler'><span class='kick'>Como ler</span><p>Cada proposta termina com o <b>resultado esperado</b>, que é o que você pode cobrar de nós. "
            f"Esta é a versão direta da carta. A versão completa, com prazo, responsável e prioridade de cada proposta, está em chapaprisma.github.io/links.</p></div></section>")

def compromissos():
    it = "".join(f"<li><span>{i}</span><div><b>{e(t)}</b>{e(d)}</div></li>" for i, (t, d) in enumerate(COMPROMISSOS, 1))
    return (f"<section class='pg comp' id='comp'><span class='kick'>Carta-proposta</span><h1 class='titulo'>Nossos compromissos</h1>"
            f"<p class='lead'>A carta em uma página. Cada item é explicado nos capítulos, com o resultado que você pode cobrar.</p><ol>{it}</ol></section>")

def abertura():
    regras = "".join(f"<li><b>{e(a)}</b> {e(b)}</li>" for a, b in REGRAS)
    return f"""<section class='pg abertura' id='abertura'>
<span class='kick'>Para quem lembra do primeiro dia</span><h1 class='titulo'>Lembra do dia em que você entrou na Poli?</h1>
<div class='manif'>
<p>A lista saiu, o seu nome estava lá e, por alguns dias, tudo pareceu grande. Depois vieram as P1, as filas e os prazos espalhados por cinco sistemas, e a empolgação do primeiro dia foi ficando para trás. O Grêmio, que deveria estar perto nessa hora, ficou longe. Para muita gente, ele só aparece em época de eleição.</p>
<p>O Grêmio Politécnico tem 123 anos, três empresas, projetos sociais, cadeiras nos colegiados da Escola e milhares de associados. Falta gestão. A Prisma nasceu para mudar isso. Somos alunos de cursos, anos e opiniões diferentes, e as propostas desta carta saíram de mais de cinco semanas de conversa com alunos. Um prisma recebe a luz e mostra as cores que ela carrega. A Poli também é feita de muitas perspectivas dentro de uma mesma Escola.</p>
</div>
<div class='duas'>
<div><h2 class='h2b'>O Grêmio hoje</h2>
<p>Segundo a gestão atual, a dívida do Grêmio foi renegociada para cerca de <b>R$ 1,5 milhão</b>. O acordo precisa ser cumprido, e todo real que vai para a dívida deixa de ir para os estudantes. A demonstração financeira mais recente a que tivemos acesso, de outubro de 2024 a setembro de 2025, não está publicada de forma acessível aos associados.</p>
<p>A receita também depende muito do calendário letivo: nessa demonstração, o Triedro faturou menos de R$ 8 mil em janeiro e mais de R$ 165 mil em maio. E a representação discente recomeça do zero a cada ano. São problemas de organização, e esta carta mostra como resolvê-los.</p></div>
<div><h2 class='h2b'>Como vamos trabalhar</h2><ul class='regras'>{regras}</ul></div>
</div>
<div class='feito'><span class='kick'>Já está no ar, sem dinheiro do Grêmio</span>
<div class='feat tres'>
<div><b>Fuja das P2 e Fuja das P3</b><span>Provas antigas resolvidas e revisadas, com Raio-X do que mais cai e simulado. chapaprisma.github.io/fuja-das-p2</span></div>
<div><b>Portal Politécnico</b><span>Protótipo do novo site do Grêmio, com bandejões, salas livres e montador de grade. chapaprisma.github.io/Site_gremio_poli</span></div>
<div><b>Site da chapa</b><span>Todas as propostas por área, organograma, perguntas frequentes e canal de ideias. chapaprisma.github.io/site_chapa</span></div>
</div></div>
</section>"""

def primeiro_ano():
    cols = "".join(f"<div class='fase'><b>{e(a)}</b><span>{e(b)}</span><ul>{''.join(f'<li>{e(x)}</li>' for x in itens)}</ul></div>" for a, b, itens in ANO)
    return f"""<section class='pg ano' id='ano'><span class='kick'>Fechamento</span><h1 class='titulo'>O primeiro ano</h1>
<p class='lead'>O roteiro da gestão. As datas exatas dependem do calendário da Poli e do Raio-X das Contas, e o andamento de cada item fica público no Portal.</p>
<div class='linha'>{cols}</div>
<div class='duas'><div><h2 class='h2b'>Como você acompanha</h2><p>Todo mês, o Portal mostra cada proposta desta carta com o responsável, o prazo, a situação (não iniciada, em andamento, entregue ou revista) e o resultado alcançado até ali. Quando uma proposta mudar, o motivo é publicado.</p></div>
<div><h2 class='h2b'>O que pode mudar</h2><p>Propostas podem ser ajustadas a partir do Raio-X das Contas, das conversas com os alunos e das decisões da Assembleia e das reuniões abertas. Quando mudarmos alguma coisa, vamos explicar por quê.</p></div></div>
</section>"""

def final():
    marca = (f"<svg class='mk' viewBox='0 0 120 120'><polygon points='60,4 116,100 4,100' fill='none' stroke='{LA}' stroke-width='1'/>"
             f"<polygon points='60,30 92,86 28,86' fill='none' stroke='{LA}' stroke-width='.6'/><polygon points='60,58 76,86 44,86' fill='{LI}'/></svg>")
    return f"""<section class='final' id='final'>
<span class='kick'>Carta-proposta</span><h1>Nota final</h1>
<p>Tudo passa por resolver o problema financeiro, mas o fim é melhorar a vida dos estudantes. Com as contas em ordem, queremos aproximar grupos de extensão e coletivos, alunos e politécnicos formados, empresas e estudantes, representantes e representados, para que haja mais convivência e mais orgulho em estudar e se formar na Poli.</p>
<p class='grande'>O Grêmio tem 123 anos de história. Queremos aprender com ela, trabalhar bem no presente e deixar uma entidade da qual a próxima turma possa se orgulhar. Entrar na Poli foi uma oportunidade, e esta é a nossa forma de retribuir. <span>Que façamos a Poli ser boa para nós e melhor para os que virão!</span></p>
<div class='voto'><span class='kick'>Como votar</span>
<div class='vg'><div><b>24 a 26 de novembro</b><span>terça a quinta, das 8h às 18h</span></div>
<div><b>Urnas na Poli</b><span>nos conjuntos de prédios da Escola</span></div>
<div><b>Apenas e-Card ou carteirinha</b><span>voto secreto</span></div></div>
<p>A votação de 10 a 12 de novembro foi anulada. Quem já votou precisa votar de novo. Vota todo aluno de graduação e de pós-graduação stricto sensu da Poli.</p></div>
<div class='contato'><span>chapaprisma.github.io/links</span><span>@prisma.poli</span><span>chapa.poli.prisma@gmail.com</span></div>
{marca}<img class='logo2' src='prisma-logo-fundo-escuro.svg' alt=''>
<p class='rod'>As cores e a logo são as da chapa, conforme as regras da Comissão Eleitoral.</p>
</section>"""

CSS = open('carta.css', encoding='utf-8').read()

def montar(pgs):
    caps = "".join(cap_html(c) for c in capitulos())
    return (f"<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><title>Carta-proposta · Chapa Prisma · Grêmio Politécnico</title>"
            f"<style>{CSS}</style></head><body>{capa()}{sumario(pgs)}{compromissos()}{abertura()}{caps}{primeiro_ano()}{final()}</body></html>")

async def pdf(html_path, out):
    async with async_playwright() as p:
        b = await p.chromium.launch(**({"executable_path": os.environ["CHROME"]} if os.environ.get("CHROME") else {}))
        pg = await b.new_page()
        await pg.goto('file://' + html_path, wait_until='networkidle')
        await pg.evaluate('document.fonts.ready')
        await pg.pdf(path=out, prefer_css_page_size=True, print_background=True)
        await b.close()

def paginas(pdfp):
    n = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', pdfp], capture_output=True, text=True).stdout).group(1))
    marcas = {'comp': 'Nossos compromissos', 'abertura': 'Lembra do dia em que você', 'ano': 'O primeiro ano', 'final': 'Nota final'}
    for c in capitulos():
        marcas[f"cap{c['n']}"] = c['t']
    achou = {}
    for i in range(3, n + 1):
        t = subprocess.run(['pdftotext', '-f', str(i), '-l', str(i), pdfp, '-'], capture_output=True, text=True).stdout
        head = " ".join(t.split())[:260]
        for k, v in marcas.items():
            if k in achou:
                continue
            if k.startswith('cap'):
                if re.search(rf'(?m)^{k[3:]} {re.escape(v)}\s*$', t):
                    achou[k] = i
            elif v in head:
                achou[k] = i
    return achou, n

def faixas_no_pe(pdfp, pgs, limite=0.66):
    """capítulos cuja faixa começa no terço de baixo da página"""
    ruins = []
    for c in capitulos():
        k = f"cap{c['n']}"; i = pgs.get(k)
        if not i or c['n'] in NOVA or c['n'] == '1':
            continue
        xml = subprocess.run(['pdftotext', '-f', str(i), '-l', str(i), '-bbox', pdfp, '-'], capture_output=True, text=True).stdout
        h = float(re.search(r'<page width="[\d.]+" height="([\d.]+)"', xml).group(1))
        palavras = re.findall(r'yMin="([\d.]+)"[^>]*>([^<]*)</word>', xml)
        primeira = c['t'].split()[0]
        for j in range(len(palavras) - 1):
            if palavras[j][1] == c['n'] and palavras[j + 1][1] == primeira:
                if float(palavras[j][0]) / h > limite:
                    ruins.append(c['n'])
                break
    return ruins

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'carta.pdf'
    hp = os.path.join(ROOT, 'carta.html')
    pgs, usado = {}, None
    for volta in range(10):
        open(hp, 'w', encoding='utf-8').write(montar(pgs))
        asyncio.run(pdf(hp, out))
        usado = dict(pgs)
        pgs, n = paginas(out)
        baixo = faixas_no_pe(out, pgs)
        if baixo:
            NOVA.add(baixo[0])  # uma de cada vez: mover uma muda a posição das seguintes
            continue
        if pgs == usado:
            break  # o sumário impresso bate com as páginas reais
    assert pgs == usado, 'sumário não estabilizou'
    print('páginas:', n, pgs, 'capítulos em página nova:', sorted(NOVA))
