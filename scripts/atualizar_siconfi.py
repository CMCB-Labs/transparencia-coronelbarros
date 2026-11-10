#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de sincronização de dados do Relatório de Gestão Fiscal (RGF)
Câmara Municipal de Coronel Barros - RS (IBGE: 4305871)
Fonte oficial: API Siconfi / Secretaria do Tesouro Nacional (STN)
"""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

COD_IBGE = 4305871
ENTE_NOME = "Câmara Municipal de Coronel Barros - RS"
BASE_URL = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt"
ANOS_CONSULTA = list(range(2021, datetime.now().year + 2))

def fetch_json(url, retries=3, delay=2):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "TransparenciaCoronelBarros/1.0 (https://camaracoronelbarros.rs.gov.br; transparencia@camaracoronelbarros.rs.gov.br)",
            "Accept": "application/json"
        }
    )
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                if resp.status == 200:
                    raw = resp.read().decode("utf-8")
                    return json.loads(raw)
        except Exception as e:
            print(f"  [Aviso] Falha ao tentar {url} (tentativa {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(delay * (attempt + 1))
    return None

def obter_entregas_camara(ano):
    url = f"{BASE_URL}/extrato_entregas?an_referencia={ano}&id_ente={COD_IBGE}"
    dados = fetch_json(url)
    if not dados or "items" not in dados:
        return []
    
    entregas = []
    for item in dados["items"]:
        instituicao = item.get("instituicao", "") or ""
        entregavel = item.get("entregavel", "") or ""
        if ("Câmara" in instituicao or "Camara" in instituicao) and "Gestão Fiscal" in entregavel:
            entregas.append(item)
    return entregas

def extrair_dados_rgf(ano, periodo):
    tipo_demonstrativo = urllib.parse.quote("RGF Simplificado")
    url = (
        f"{BASE_URL}/rgf?an_exercicio={ano}&in_periodicidade=S"
        f"&nr_periodo={periodo}&co_tipo_demonstrativo={tipo_demonstrativo}"
        f"&id_ente={COD_IBGE}&co_poder=L"
    )
    dados = fetch_json(url)
    if not dados or "items" not in dados:
        return []
    return dados["items"]

def processar_periodo(ano, periodo, entrega_meta=None):
    items = extrair_dados_rgf(ano, periodo)
    if not items:
        return None

    # Estrutura base
    registro = {
        "exercicio": ano,
        "periodo": periodo,
        "periodicidade": "S",
        "periodo_rotulo": f"{periodo}º Semestre de {ano}",
        "status_relatorio": entrega_meta.get("status_relatorio") if entrega_meta else "HO",
        "data_status": entrega_meta.get("data_status") if entrega_meta else None,
        "populacao": items[0].get("populacao") if items else None,
        "lrf": {
            "rcl": 0.0,
            "rcl_ajustada": 0.0,
            "dtp_valor": 0.0,
            "dtp_percentual": 0.0,
            "limite_maximo_valor": 0.0,
            "limite_maximo_percentual": 6.00,
            "limite_prudencial_valor": 0.0,
            "limite_prudencial_percentual": 5.70,
            "limite_alerta_valor": 0.0,
            "limite_alerta_percentual": 5.40,
            "margem_prudencial_valor": 0.0,
            "margem_maxima_valor": 0.0,
            "situacao": "Regular",
            "situacao_classe": "status-regular"
        },
        "detalhamento_pessoal": [],
        "disponibilidade_caixa": [],
        "simplificado": []
    }

    # Percorre os itens do RGF para extrair os valores-chave
    for item in items:
        anexo = item.get("anexo", "")
        coluna = item.get("coluna", "")
        conta = item.get("conta", "")
        valor = item.get("valor")

        if valor is None:
            continue

        try:
            val_float = float(valor)
        except (ValueError, TypeError):
            continue

        # Identificação de campos da LRF (Anexo 01)
        if anexo == "RGF-Anexo 01":
            registro["detalhamento_pessoal"].append({
                "conta": conta,
                "coluna": coluna,
                "valor": val_float
            })

            conta_upper = conta.upper()
            if "RECEITA CORRENTE LIQUIDA - RCL" in conta_upper and "(IV)" in conta_upper and coluna == "Valor":
                registro["lrf"]["rcl"] = val_float
            elif "RECEITA CORRENTE LÍQUIDA AJUSTADA" in conta_upper and coluna == "Valor":
                registro["lrf"]["rcl_ajustada"] = val_float
            elif "DESPESA TOTAL COM PESSOAL - DTP" in conta_upper:
                if coluna == "Valor":
                    registro["lrf"]["dtp_valor"] = val_float
                elif "%" in coluna:
                    registro["lrf"]["dtp_percentual"] = val_float
            elif "LIMITE MÁXIMO" in conta_upper or "LIMITE MAXIMO" in conta_upper:
                if coluna == "Valor":
                    registro["lrf"]["limite_maximo_valor"] = val_float
                elif "%" in coluna:
                    registro["lrf"]["limite_maximo_percentual"] = val_float
            elif "LIMITE PRUDENCIAL" in conta_upper:
                if coluna == "Valor":
                    registro["lrf"]["limite_prudencial_valor"] = val_float
                elif "%" in coluna:
                    registro["lrf"]["limite_prudencial_percentual"] = val_float
            elif "LIMITE DE ALERTA" in conta_upper:
                if coluna == "Valor":
                    registro["lrf"]["limite_alerta_valor"] = val_float
                elif "%" in coluna:
                    registro["lrf"]["limite_alerta_percentual"] = val_float

        elif anexo == "RGF-Anexo 05":
            registro["disponibilidade_caixa"].append({
                "conta": conta,
                "coluna": coluna,
                "valor": val_float
            })

        elif anexo == "RGF-Anexo 06":
            registro["simplificado"].append({
                "conta": conta,
                "coluna": coluna,
                "valor": val_float
            })

    # Cálculos derivados
    dtp_val = registro["lrf"]["dtp_valor"]
    lim_prud = registro["lrf"]["limite_prudencial_valor"]
    lim_max = registro["lrf"]["limite_maximo_valor"]
    dtp_pct = registro["lrf"]["dtp_percentual"]

    registro["lrf"]["margem_prudencial_valor"] = round(max(0.0, lim_prud - dtp_val), 2)
    registro["lrf"]["margem_maxima_valor"] = round(max(0.0, lim_max - dtp_val), 2)

    if dtp_pct > 6.00:
        registro["lrf"]["situacao"] = "Acima do Limite Legal"
        registro["lrf"]["situacao_classe"] = "status-perigo"
    elif dtp_pct > 5.70:
        registro["lrf"]["situacao"] = "Limite Prudencial Ultrapassado"
        registro["lrf"]["situacao_classe"] = "status-prudencial"
    elif dtp_pct > 5.40:
        registro["lrf"]["situacao"] = "Limite de Alerta Atingido"
        registro["lrf"]["situacao_classe"] = "status-alerta"
    else:
        registro["lrf"]["situacao"] = "Conforme (Abaixo dos Limites)"
        registro["lrf"]["situacao_classe"] = "status-regular"

    return registro

def main():
    print("=" * 60)
    print(f"Iniciando sincronização SICONFI - {ENTE_NOME}")
    print(f"Data de execução: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    periodos_homologados = []

    for ano in ANOS_CONSULTA:
        print(f"\nConsultando entregas para {ano}...")
        entregas = obter_entregas_camara(ano)
        if not entregas:
            print(f"  Nenhuma entrega de RGF encontrada para {ano}.")
            continue

        for entrega in sorted(entregas, key=lambda x: x.get("periodo", 0)):
            p = entrega.get("periodo")
            print(f"  Baixando RGF de {ano} - {p}º Semestre...")
            dado = processar_periodo(ano, p, entrega)
            if dado:
                periodos_homologados.append(dado)
                print(f"    -> OK! DTP: R$ {dado['lrf']['dtp_valor']:,.2f} ({dado['lrf']['dtp_percentual']}%)")
            else:
                print(f"    -> Dados não retornados para {ano} - {p}º Semestre.")
            time.sleep(0.5)

    if not periodos_homologados:
        print("\n[Erro] Nenhum dado foi coletado. Abortando sem sobrescrever arquivo anterior.")
        sys.exit(1)

    # Ordenação decrescente (mais recente primeiro)
    periodos_homologados.sort(key=lambda x: (x["exercicio"], x["periodo"]), reverse=True)

    dados_finais = {
        "metadata": {
            "ente": ENTE_NOME,
            "cod_ibge": COD_IBGE,
            "municipio": "Coronel Barros",
            "uf": "RS",
            "fonte": "Secretaria do Tesouro Nacional - SICONFI / API Data Lake",
            "data_sincronizacao": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_periodos": len(periodos_homologados),
            "exercicios_disponiveis": sorted(list(set(x["exercicio"] for x in periodos_homologados)), reverse=True)
        },
        "periodos": periodos_homologados
    }

    caminho_saida = os.path.join(os.path.dirname(__file__), "..", "data", "rgf.json")
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)

    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(dados_finais, f, ensure_ascii=False, indent=2)

    print(f"\n[Sucesso] {len(periodos_homologados)} períodos consolidados com sucesso em:")
    print(f"  {os.path.abspath(caminho_saida)}")

if __name__ == "__main__":
    main()
