#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sincronização de Licitações e Contratos da Câmara de Coronel Barros - RS
Fonte Oficial: Dados Abertos TCE-RS / Sistema LicitaCon
Órgão TCE: 75101 (CM de Coronel Barros)

Gera:
  - data/licitacoes.json
  - data/contratos.json
"""

import csv
import io
import json
import os
import sys
import time
import urllib.request
import zipfile
from datetime import datetime, timezone

COD_ORGAO_TCE = 75101
URL_LICITACOES_ZIP = f"https://dados.tce.rs.gov.br/dados/licitacon/licitacao/orgao/{COD_ORGAO_TCE}.csv.zip"
URL_CONTRATOS_ZIP = f"https://dados.tce.rs.gov.br/dados/licitacon/contrato/orgao/{COD_ORGAO_TCE}.csv.zip"

MODALIDADES_MAP = {
    "PRI": "Inexigibilidade",
    "PRD": "Dispensa de Licitação",
    "RPO": "Registro de Preços",
    "TMP": "Tomada de Preços",
    "PRP": "Pregão Presencial",
    "PRE": "Pregão Eletrônico",
    "CV": "Convite",
    "CP": "Concorrência",
    "DL": "Dispensa Eletrônica",
    "INX": "Inexigibilidade"
}

FASES_MAP = {
    "INT": "Fase Interna",
    "PUB": "Publicado / Homologado",
    "HAB": "Habilitação",
    "JUL": "Julgamento",
    "HOM": "Homologado",
    "REV": "Revogado / Anulado",
    "DES": "Deserto / Fracassado"
}

TIPOS_DOC_MAP = {
    "EDT": "Edital",
    "AVS": "Aviso de Licitação",
    "ATA": "Ata de Sessão",
    "HOM": "Termo de Homologação",
    "ADJ": "Termo de Adjudicação",
    "TFD": "Termo de Dispensa",
    "TFI": "Termo de Inexigibilidade",
    "PFC": "Proposta Comercial",
    "CTR": "Contrato",
    "TAD": "Termo Aditivo",
    "RES": "Termo de Rescisão",
    "OUT": "Outros Documentos"
}

def formatar_cnpj_cpf(doc):
    doc = str(doc or "").strip()
    if len(doc) == 14:
        return f"{doc[:2]}.{doc[2:5]}.{doc[5:8]}/{doc[8:12]}-{doc[12:]}"
    elif len(doc) == 11:
        return f"{doc[:3]}.{doc[3:6]}.{doc[6:9]}-{doc[9:]}"
    return doc

def download_zip(url, retries=3, delay=2):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "TransparenciaCoronelBarros/1.0 (https://cmcb-labs.github.io/transparencia-coronelbarros; camara@coronelbarros.rs.gov.br)"
        }
    )
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=40) as resp:
                if resp.status == 200:
                    return zipfile.ZipFile(io.BytesIO(resp.read()))
        except Exception as e:
            print(f"  [Aviso] Falha ao baixar {url} (tentativa {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(delay * (attempt + 1))
    return None

def processar_licitacoes():
    print(f"\n[LicitaCon] Baixando licitações da Câmara ({URL_LICITACOES_ZIP})...")
    z = download_zip(URL_LICITACOES_ZIP)
    if not z:
        print("[Erro] Não foi possível baixar licitacoes.zip")
        return []

    # 1. Pessoas
    pessoas = {}
    if "pessoas.csv" in z.namelist():
        with z.open("pessoas.csv") as f:
            for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8", errors="replace")):
                doc = r.get("NR_DOCUMENTO", "").strip()
                if doc:
                    pessoas[doc] = r.get("NM_PESSOA", "").strip()

    # 2. Documentos
    docs = {}
    if "documento_lic.csv" in z.namelist():
        with z.open("documento_lic.csv") as f:
            for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8", errors="replace")):
                nr = r.get("NR_LICITACAO")
                ano = r.get("ANO_LICITACAO")
                mod = r.get("CD_TIPO_MODALIDADE")
                key = (nr, ano, mod)
                cd_tipo = r.get("CD_TIPO_DOCUMENTO", "")
                docs.setdefault(key, []).append({
                    "tipo_codigo": cd_tipo,
                    "tipo_rotulo": TIPOS_DOC_MAP.get(cd_tipo, "Documento"),
                    "nome_arquivo": r.get("NOME_ARQUIVO_DOCUMENTO", "").split("\\")[-1],
                    "url": r.get("ARQUIVO_URL_DOWNLOAD", "")
                })

    # 3. Licitações
    licitacoes = []
    if "licitacao.csv" in z.namelist():
        with z.open("licitacao.csv") as f:
            for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8", errors="replace")):
                nr = r.get("NR_LICITACAO")
                ano = r.get("ANO_LICITACAO")
                mod_cod = r.get("CD_TIPO_MODALIDADE", "")
                fase_cod = r.get("CD_TIPO_FASE_ATUAL", "")

                doc_fornec = (r.get("NR_DOCUMENTO_VENCEDOR") or r.get("NR_DOCUMENTO_FORNECEDOR") or "").strip()
                nome_fornec = pessoas.get(doc_fornec, "")

                val_estimado = float(r.get("VL_LICITACAO") or 0)
                val_homologado = float(r.get("VL_HOMOLOGADO") or 0)
                valor_final = val_homologado if val_homologado > 0 else val_estimado

                anexos = docs.get((nr, ano, mod_cod), [])

                licitacoes.append({
                    "id": f"{ano}_{nr}_{mod_cod}",
                    "numero": nr,
                    "ano": int(ano) if ano and ano.isdigit() else None,
                    "modalidade_codigo": mod_cod,
                    "modalidade": MODALIDADES_MAP.get(mod_cod, mod_cod or "Não informada"),
                    "processo": r.get("NR_PROCESSO"),
                    "ano_processo": r.get("ANO_PROCESSO"),
                    "objeto": (r.get("DS_OBJETO") or "").strip(),
                    "fase_codigo": fase_cod,
                    "fase": FASES_MAP.get(fase_cod, "Publicado"),
                    "data_abertura": r.get("DT_ABERTURA") or None,
                    "data_homologacao": r.get("DT_HOMOLOGACAO") or None,
                    "data_adjudicacao": r.get("DT_ADJUDICACAO") or None,
                    "valor_estimado": val_estimado,
                    "valor_homologado": val_homologado,
                    "valor_final": valor_final,
                    "fornecedor_doc": formatar_cnpj_cpf(doc_fornec),
                    "fornecedor_nome": nome_fornec or "Não informado / Em andamento",
                    "link_licitacon": r.get("LINK_LICITACON_CIDADAO", ""),
                    "documentos": anexos
                })

    # Ordenar por ano decrescente, depois por data de abertura ou número decrescente
    def chave_ordem(item):
        ano = item.get("ano") or 0
        dt = item.get("data_abertura") or "1900-01-01"
        try:
            nr = int(item.get("numero") or 0)
        except ValueError:
            nr = 0
        return (ano, dt, nr)

    licitacoes.sort(key=chave_ordem, reverse=True)
    return licitacoes

def processar_contratos():
    print(f"\n[LicitaCon] Baixando contratos da Câmara ({URL_CONTRATOS_ZIP})...")
    z = download_zip(URL_CONTRATOS_ZIP)
    if not z:
        print("[Erro] Não foi possível baixar contratos.zip")
        return []

    # 1. Pessoas
    pessoas = {}
    if "pessoas.csv" in z.namelist():
        with z.open("pessoas.csv") as f:
            for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8", errors="replace")):
                doc = r.get("NR_DOCUMENTO", "").strip()
                if doc:
                    pessoas[doc] = r.get("NM_PESSOA", "").strip()

    # 2. Documentos
    docs = {}
    if "documento_con.csv" in z.namelist():
        with z.open("documento_con.csv") as f:
            for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8", errors="replace")):
                nr = r.get("NR_CONTRATO")
                ano = r.get("ANO_CONTRATO")
                key = (nr, ano)
                cd_tipo = r.get("CD_TIPO_DOCUMENTO", "")
                docs.setdefault(key, []).append({
                    "tipo_codigo": cd_tipo,
                    "tipo_rotulo": TIPOS_DOC_MAP.get(cd_tipo, "Contrato/Aditivo"),
                    "nome_arquivo": r.get("NOME_ARQUIVO_DOCUMENTO", "").split("\\")[-1],
                    "url": r.get("ARQUIVO_URL_DOWNLOAD", "")
                })

    # 3. Termos Aditivos / Alterações
    alteracoes = {}
    if "alteracao.csv" in z.namelist():
        with z.open("alteracao.csv") as f:
            for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8", errors="replace")):
                nr = r.get("NR_CONTRATO")
                ano = r.get("ANO_CONTRATO")
                key = (nr, ano)
                alteracoes.setdefault(key, []).append({
                    "tipo_alteracao": r.get("TP_ALTERACAO_CONTRATUAL"),
                    "data": r.get("DT_ALTERACAO"),
                    "novo_fim_vigencia": r.get("DT_FINAL_VIGENCIA"),
                    "valor_acrescimo": float(r.get("VL_ACRESCIMO") or 0),
                    "justificativa": r.get("DS_JUSTIFICATIVA", "")
                })

    hoje = datetime.now().date()

    # 4. Contratos
    contratos = []
    if "contrato.csv" in z.namelist():
        with z.open("contrato.csv") as f:
            for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8", errors="replace")):
                nr = r.get("NR_CONTRATO")
                ano = r.get("ANO_CONTRATO")
                mod_cod = r.get("CD_TIPO_MODALIDADE", "")
                doc_fornec = r.get("NR_DOCUMENTO", "").strip()
                nome_fornec = pessoas.get(doc_fornec, "")

                val_contrato = float(r.get("VL_CONTRATO") or 0)
                dt_fim_str = r.get("DT_FINAL_VIGENCIA")

                # Calcular situação de vigência
                situacao = "Concluído"
                situacao_classe = "badge-neutral"
                if dt_fim_str:
                    try:
                        dt_fim = datetime.strptime(dt_fim_str[:10], "%Y-%m-%d").date()
                        if dt_fim >= hoje:
                            situacao = "Vigente"
                            situacao_classe = "badge-success"
                        else:
                            situacao = "Encerrado"
                            situacao_classe = "badge-neutral"
                    except ValueError:
                        pass

                anexos = docs.get((nr, ano), [])
                aditivos = alteracoes.get((nr, ano), [])

                contratos.append({
                    "id": f"{ano}_{nr}",
                    "numero": nr,
                    "ano": int(ano) if ano and ano.isdigit() else None,
                    "licitacao_origem": f"{r.get('NR_LICITACAO')}/{r.get('ANO_LICITACAO')}" if r.get("NR_LICITACAO") else "Não vinculada",
                    "modalidade_codigo": mod_cod,
                    "modalidade": MODALIDADES_MAP.get(mod_cod, mod_cod or "Contratação"),
                    "processo": r.get("NR_PROCESSO"),
                    "ano_processo": r.get("ANO_PROCESSO"),
                    "objeto": (r.get("DS_OBJETO") or "").strip(),
                    "fornecedor_doc": formatar_cnpj_cpf(doc_fornec),
                    "fornecedor_nome": nome_fornec or "Não identificado",
                    "valor_contrato": val_contrato,
                    "data_assinatura": r.get("DT_ASSINATURA") or None,
                    "inicio_vigencia": r.get("DT_INICIO_VIGENCIA") or None,
                    "fim_vigencia": dt_fim_str or None,
                    "dias_prazo": r.get("NR_DIAS_PRAZO"),
                    "situacao": situacao,
                    "situacao_classe": situacao_classe,
                    "link_licitacon": r.get("LINK_LICITACON_CIDADAO", ""),
                    "documentos": anexos,
                    "aditivos": aditivos
                })

    def chave_ordem_con(item):
        ano = item.get("ano") or 0
        dt = item.get("data_assinatura") or item.get("inicio_vigencia") or "1900-01-01"
        try:
            nr = int(item.get("numero") or 0)
        except ValueError:
            nr = 0
        return (ano, dt, nr)

    contratos.sort(key=chave_ordem_con, reverse=True)
    return contratos

def main():
    print("=" * 70)
    print("SINCRONIZAÇÃO DE LICITAÇÕES E CONTRATOS (LICITACON / TCE-RS)")
    print("Câmara Municipal de Coronel Barros - RS (Órgão TCE: 75101)")
    print("=" * 70)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, ".."))
    data_dir = os.path.join(repo_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    # 1. Licitações
    licitacoes = processar_licitacoes()
    resumo_lic = {
        "ente": "Câmara Municipal de Coronel Barros - RS",
        "orgao_tce": COD_ORGAO_TCE,
        "fonte": "Tribunal de Contas do Estado do Rio Grande do Sul (TCE-RS) / LicitaCon",
        "url_origem": URL_LICITACOES_ZIP,
        "data_atualizacao": datetime.now(timezone.utc).isoformat(),
        "total_licitacoes": len(licitacoes),
        "total_dispensas": sum(1 for l in licitacoes if l["modalidade_codigo"] == "PRD"),
        "total_inexigibilidades": sum(1 for l in licitacoes if l["modalidade_codigo"] in ["PRI", "INX"]),
        "total_outras": sum(1 for l in licitacoes if l["modalidade_codigo"] not in ["PRD", "PRI", "INX"]),
        "licitacoes": licitacoes
    }
    lic_path = os.path.join(data_dir, "licitacoes.json")
    with open(lic_path, "w", encoding="utf-8") as f:
        json.dump(resumo_lic, f, ensure_ascii=False, indent=2)
    print(f"[Sucesso] Licitações salvas: {lic_path} ({len(licitacoes)} registros, {os.path.getsize(lic_path)/1024:.1f} KB)")

    # 2. Contratos
    contratos = processar_contratos()
    resumo_con = {
        "ente": "Câmara Municipal de Coronel Barros - RS",
        "orgao_tce": COD_ORGAO_TCE,
        "fonte": "Tribunal de Contas do Estado do Rio Grande do Sul (TCE-RS) / LicitaCon",
        "url_origem": URL_CONTRATOS_ZIP,
        "data_atualizacao": datetime.now(timezone.utc).isoformat(),
        "total_contratos": len(contratos),
        "vigentes": sum(1 for c in contratos if c["situacao"] == "Vigente"),
        "encerrados": sum(1 for c in contratos if c["situacao"] != "Vigente"),
        "valor_total": sum(c["valor_contrato"] for c in contratos),
        "contratos": contratos
    }
    con_path = os.path.join(data_dir, "contratos.json")
    with open(con_path, "w", encoding="utf-8") as f:
        json.dump(resumo_con, f, ensure_ascii=False, indent=2)
    print(f"[Sucesso] Contratos salvos: {con_path} ({len(contratos)} registros, {os.path.getsize(con_path)/1024:.1f} KB)")

    print("\n" + "=" * 70)
    print("SINCRONIZAÇÃO DO LICITACON FINALIZADA COM SUCESSO!")
    print("=" * 70)

if __name__ == "__main__":
    main()
