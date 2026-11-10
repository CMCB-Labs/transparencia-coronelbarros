#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sincronização de Decisões e Julgamentos de Contas do TCE-RS
Município de Coronel Barros - RS
Órgãos:
  - Executivo Municipal de Coronel Barros (Código TCE: 75100)
  - Legislativo Municipal de Coronel Barros (Código TCE: 75101)

Fonte oficial: API Pública de Jurisprudência e Decisões do TCE-RS
https://portal.tce.rs.gov.br/api/pesquisa/v2/jurisprudencia-decisoes
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

BASE_API_URL = "https://portal.tce.rs.gov.br/api/pesquisa/v2/jurisprudencia-decisoes/{pagina}"

ORGAOS = [
    {
        "nome_api": "EXECUTIVO MUNICIPAL DE CORONEL BARROS",
        "nome_exibicao": "Executivo Municipal (Prefeitura)",
        "poder": "E",
        "codigo_tce": 75100,
    },
    {
        "nome_api": "LEGISLATIVO MUNICIPAL DE CORONEL BARROS",
        "nome_exibicao": "Legislativo Municipal (Câmara de Vereadores)",
        "poder": "L",
        "codigo_tce": 75101,
    },
]

def sanitize_link(link):
    if not link:
        return None
    # Forçar HTTPS para evitar bloqueio de conteúdo misto em navegadores
    if link.startswith("http://"):
        return "https://" + link[7:]
    return link

def parse_conclusao(texto, dec_desc):
    txt = (texto or "").strip()
    desc = (dec_desc or "").strip()
    full = f"{desc} {txt}".lower()

    if "parecer desfavorável" in full or "parecer desfavoravel" in full or "desfavorável à aprovação" in full:
        return {"tipo": "desfavoravel", "label": "Parecer Desfavorável", "classe": "badge-danger"}
    elif "ressalva" in full and ("favorável" in full or "favoravel" in full):
        return {"tipo": "favoravel_ressalva", "label": "Favorável com Ressalva", "classe": "badge-warning"}
    elif "parecer favorável" in full or "parecer favoravel" in full or full.startswith("parecer favor"):
        return {"tipo": "favoravel", "label": "Parecer Favorável", "classe": "badge-success"}
    elif "regulares com ressalva" in full:
        return {"tipo": "regulares_ressalva", "label": "Regulares com Ressalva", "classe": "badge-warning"}
    elif "julgar regulares" in full or "contas regulares" in full or "regulares as contas" in full:
        return {"tipo": "regulares", "label": "Contas Regulares", "classe": "badge-success"}
    elif "julgar irregulares" in full or "contas irregulares" in full or "irregulares as contas" in full:
        return {"tipo": "irregulares", "label": "Contas Irregulares", "classe": "badge-danger"}
    elif "arquivamento" in full or "arquivado" in full:
        return {"tipo": "arquivado", "label": "Arquivado", "classe": "badge-neutral"}
    elif "recurso de embargos" in full or "conhece" in full:
        return {"tipo": "recurso", "label": "Recurso Julgado", "classe": "badge-info"}
    elif "admissão" in full or "admissao" in full:
        return {"tipo": "admissao", "label": "Auditoria de Pessoal", "classe": "badge-neutral"}
    else:
        return {"tipo": "decisao", "label": "Decisão Proferida", "classe": "badge-neutral"}

def extrair_exercicio(item_campos):
    ex = item_campos.get("dt_inicio_exercicio")
    if ex:
        try:
            return int(str(ex).strip()[:4])
        except (ValueError, TypeError):
            pass
    # Tenta extrair do número do processo (ex: 000275-0200/24-0 -> ano 2024 se não houver dt_inicio_exercicio)
    ano_ordem = item_campos.get("ano_processo_ordem")
    if ano_ordem:
        try:
            return int(ano_ordem)
        except (ValueError, TypeError):
            pass
    return None

def buscar_decisoes_orgao(orgao_config, retries=3, delay=2):
    resultados = []
    pagina = 1
    total_esperado = None

    print(f"\n[TCE-RS] Consultando: {orgao_config['nome_exibicao']}...")

    while True:
        url = BASE_API_URL.format(pagina=pagina)
        payload = {
            "termo": "",
            "filtros": [
                {
                    "campo": "orgao.keyword",
                    "nome": "Órgão de origem",
                    "valores": [orgao_config["nome_api"]],
                    "tipo": "palavra-chave"
                }
            ],
            "opcoes": [
                {"opcao": "quantidadeResultadosPorPagina", "tipo": "number", "valor": 50}
            ]
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "TransparenciaCoronelBarros/1.0 (https://cmcb-labs.github.io/transparencia-coronelbarros; camara@coronelbarros.rs.gov.br)"
            }
        )

        dados = None
        for attempt in range(retries):
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    if resp.status == 200:
                        dados = json.loads(resp.read().decode("utf-8"))
                        break
            except Exception as e:
                print(f"  [Aviso] Erro na pág. {pagina} (tentativa {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(delay * (attempt + 1))

        if not dados:
            print(f"  [Erro] Falha ao obter dados da página {pagina}.")
            break

        res_obj = dados.get("resultados", {})
        itens = res_obj.get("resultados", [])
        if total_esperado is None:
            total_esperado = res_obj.get("total", {}).get("valor", 0)
            print(f"  Total informado pela API: {total_esperado} decisões.")

        if not itens:
            break

        for it in itens:
            c = it.get("campos", {})
            dt_sessao = c.get("dt_sessao")
            dt_sessao_fmt = dt_sessao[:10] if dt_sessao else None

            # Determinar se é processo principal de Contas
            tp_proc = (c.get("ds_tp_processo") or "").strip()
            eh_contas = any(k in tp_proc.upper() for k in ["CONTAS", "PRESTAÇÃO DE CONTAS", "GOVERNO", "GESTÃO FISCAL", "GESTÃO"])

            item_estruturado = {
                "id": it.get("id") or c.get("nr_processo_fmt"),
                "processo": c.get("nr_processo_fmt"),
                "processo_raw": str(c.get("nr_processo") or ""),
                "orgao": orgao_config["nome_exibicao"],
                "orgao_nome_curto": "Executivo" if orgao_config["poder"] == "E" else "Legislativo",
                "poder": orgao_config["poder"],
                "codigo_orgao_tce": orgao_config["codigo_tce"],
                "exercicio": extrair_exercicio(c),
                "data_sessao": dt_sessao_fmt,
                "ano_sessao": c.get("ano_sessao"),
                "tipo_processo": tp_proc,
                "eh_contas": eh_contas,
                "orgao_julgador": c.get("nm_orgao_julgador"),
                "relator": c.get("nm_magistrado"),
                "gabinete": c.get("nm_gabinete"),
                "conclusao": parse_conclusao(c.get("texto"), c.get("dec_descricao")),
                "resumo_decisao": (c.get("texto") or "").strip(),
                "ementa": (c.get("texto_ementa") or "").strip(),
                "link_decisao": sanitize_link(c.get("link_visualizador_decisao")),
                "link_relatorio_voto": sanitize_link(c.get("link_visualizador_relatorio_voto")),
                "eh_eletronico": c.get("eh_processo_eletronico") == "S",
            }
            resultados.append(item_estruturado)

        print(f"  Página {pagina} processada ({len(resultados)}/{total_esperado} coletados).")

        if len(resultados) >= total_esperado or len(itens) < 50:
            break

        pagina += 1
        time.sleep(0.5)

    return resultados

def main():
    print("=" * 70)
    print("SINCRONIZADOR DE JULGAMENTOS E DECISÕES TCE-RS")
    print("Município de Coronel Barros - RS")
    print("=" * 70)

    todos_registros = []
    totais = {"E": 0, "L": 0}

    for orgao in ORGAOS:
        itens = buscar_decisoes_orgao(orgao)
        totais[orgao["poder"]] = len(itens)
        todos_registros.extend(itens)

    # Ordenar por data da sessão decrescente, depois por exercício decrescente
    def chave_ordenacao(r):
        dt = r.get("data_sessao") or "1900-01-01"
        ex = r.get("exercicio") or 0
        return (dt, ex)

    todos_registros.sort(key=chave_ordenacao, reverse=True)

    # Estatísticas de pareceres e decisões de contas
    contas_favoraveis = sum(1 for r in todos_registros if r["conclusao"]["tipo"] in ["favoravel", "regulares"])
    contas_ressalva = sum(1 for r in todos_registros if r["conclusao"]["tipo"] in ["favoravel_ressalva", "regulares_ressalva"])
    contas_desfavoraveis = sum(1 for r in todos_registros if r["conclusao"]["tipo"] in ["desfavoravel", "irregulares"])

    dados_finais = {
        "ente": "Município de Coronel Barros - RS",
        "ibge": 4305871,
        "tce_orgaos": {"executivo": 75100, "legislativo": 75101},
        "fonte": "Tribunal de Contas do Estado do Rio Grande do Sul (TCE-RS)",
        "api_jurisprudencia": "https://portal.tce.rs.gov.br/api/pesquisa/v2/jurisprudencia-decisoes",
        "data_atualizacao": datetime.now(timezone.utc).isoformat(),
        "total_registros": len(todos_registros),
        "total_executivo": totais["E"],
        "total_legislativo": totais["L"],
        "resumo_contas": {
            "favoraveis_ou_regulares": contas_favoraveis,
            "com_ressalva": contas_ressalva,
            "desfavoraveis_ou_irregulares": contas_desfavoraveis
        },
        "registros": todos_registros
    }

    # Diretório de destino
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, ".."))
    data_dir = os.path.join(repo_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    output_path = os.path.join(data_dir, "julgamentos.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dados_finais, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 70)
    print(f"SINCRONIZAÇÃO CONCLUÍDA COM SUCESSO!")
    print(f"Total coletado: {len(todos_registros)} registros")
    print(f"  - Executivo:   {totais['E']}")
    print(f"  - Legislativo: {totais['L']}")
    print(f"Arquivo gerado: {output_path} ({os.path.getsize(output_path) / 1024:.1f} KB)")
    print("=" * 70)

if __name__ == "__main__":
    main()
