#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de sincronização de dados fiscais e contábeis do SICONFI
Câmara Municipal de Coronel Barros - RS (IBGE: 4305871)
Fonte oficial: API Siconfi / Secretaria do Tesouro Nacional (STN)

Coleta:
1. RGF (Relatório de Gestão Fiscal) - data/rgf.json
2. DCA (Declaração de Contas Anuais / Balanços) - data/balancos.json
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
            "User-Agent": "TransparenciaCoronelBarros/1.0 (https://cmcb-labs.github.io/transparencia-coronelbarros; camara@coronelbarros.rs.gov.br)",
            "Accept": "application/json"
        }
    )
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=35) as resp:
                if resp.status == 200:
                    raw = resp.read().decode("utf-8")
                    return json.loads(raw)
        except Exception as e:
            print(f"  [Aviso] Falha ao tentar {url} (tentativa {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(delay * (attempt + 1))
    return None

# ==============================================================================
# 1. MÓDULO RGF (RELATÓRIO DE GESTÃO FISCAL)
# ==============================================================================

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

def processar_periodo_rgf(ano, periodo, entrega_meta=None):
    items = extrair_dados_rgf(ano, periodo)
    if not items:
        return None

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

def sincronizar_rgf():
    print("\n--- Sincronizando RGF (Gestão Fiscal) ---")
    periodos_homologados = []

    for ano in ANOS_CONSULTA:
        entregas = obter_entregas_camara(ano)
        if not entregas:
            continue

        for entrega in sorted(entregas, key=lambda x: x.get("periodo", 0)):
            p = entrega.get("periodo")
            dado = processar_periodo_rgf(ano, p, entrega)
            if dado:
                periodos_homologados.append(dado)
                print(f"  RGF {ano} / {p}º Semestre -> DTP: R$ {dado['lrf']['dtp_valor']:,.2f} ({dado['lrf']['dtp_percentual']}%)")
            time.sleep(0.3)

    if not periodos_homologados:
        print("[Aviso] Nenhum dado de RGF retornado.")
        return False

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

    print(f"  [OK] RGF consolidado com {len(periodos_homologados)} semestres em {os.path.abspath(caminho_saida)}")
    return True

# ==============================================================================
# 2. MÓDULO DCA (BALANÇOS E CONTAS ANUAIS)
# ==============================================================================

def processar_ano_dca(ano):
    url = f"{BASE_URL}/dca?an_exercicio={ano}&id_ente={COD_IBGE}"
    dados = fetch_json(url)
    if not dados or "items" not in dados:
        return None

    items = dados["items"]
    if not items:
        return None

    exercicio_data = {
        "exercicio": ano,
        "resumo": {
            "receita_bruta": 0.0,
            "deducoes_receita": 0.0,
            "receita_liquida": 0.0,
            "despesa_empenhada": 0.0,
            "despesa_liquidada": 0.0,
            "despesa_paga": 0.0,
            "resultado_orcamentario": 0.0,
            "ativo_total": 0.0,
            "passivo_total": 0.0,
            "patrimonio_liquido": 0.0,
            "camara_despesa_empenhada": 0.0,
            "camara_despesa_liquidada": 0.0,
            "camara_despesa_paga": 0.0
        },
        "balanco_patrimonial": [],
        "balanco_orcamentario_receitas": [],
        "balanco_orcamentario_despesas": [],
        "despesas_funcao": [],
        "dvp": []
    }

    for item in items:
        anexo = item.get("anexo", "")
        coluna = item.get("coluna", "")
        conta = item.get("conta", "")
        valor = item.get("valor")

        if valor is None:
            continue
        try:
            val = float(valor)
        except (ValueError, TypeError):
            continue

        # Anexo I-AB: Balanço Patrimonial
        if anexo == "DCA-Anexo I-AB":
            exercicio_data["balanco_patrimonial"].append({
                "conta": conta,
                "coluna": coluna,
                "valor": val
            })
            if conta == "1.0.0.0.0.00.00 - Ativo":
                exercicio_data["resumo"]["ativo_total"] = val
            elif conta == "2.0.0.0.0.00.00 - Passivo e Patrimônio Liquido":
                exercicio_data["resumo"]["passivo_total"] = val
            elif conta == "2.3.0.0.0.00.00 - Patrimônio Liquido":
                exercicio_data["resumo"]["patrimonio_liquido"] = val

        # Anexo I-C: Balanço Orçamentário - Receitas
        elif anexo == "DCA-Anexo I-C":
            exercicio_data["balanco_orcamentario_receitas"].append({
                "conta": conta,
                "coluna": coluna,
                "valor": val
            })
            if "RECEITAS (EXCETO INTRA" in conta.upper() or "RECEITAS CORRENTES" in conta.upper():
                if coluna == "Receitas Brutas Realizadas" and "EXCETO" in conta.upper():
                    exercicio_data["resumo"]["receita_bruta"] = val
                elif "FUNDEB" in coluna or "Outras Deduções" in coluna:
                    exercicio_data["resumo"]["deducoes_receita"] += val

        # Anexo I-D: Balanço Orçamentário - Despesas
        elif anexo == "DCA-Anexo I-D":
            exercicio_data["balanco_orcamentario_despesas"].append({
                "conta": conta,
                "coluna": coluna,
                "valor": val
            })
            if "TOTAL GERAL DA DESPESA" in conta.upper():
                if coluna == "Despesas Empenhadas":
                    exercicio_data["resumo"]["despesa_empenhada"] = val
                elif coluna == "Despesas Liquidadas":
                    exercicio_data["resumo"]["despesa_liquidada"] = val
                elif coluna == "Despesas Pagas":
                    exercicio_data["resumo"]["despesa_paga"] = val

        # Anexo I-E: Despesas por Função
        elif anexo == "DCA-Anexo I-E":
            exercicio_data["despesas_funcao"].append({
                "conta": conta,
                "coluna": coluna,
                "valor": val
            })
            if conta == "01 - Legislativa":
                if coluna == "Despesas Empenhadas":
                    exercicio_data["resumo"]["camara_despesa_empenhada"] = val
                elif coluna == "Despesas Liquidadas":
                    exercicio_data["resumo"]["camara_despesa_liquidada"] = val
                elif coluna == "Despesas Pagas":
                    exercicio_data["resumo"]["camara_despesa_paga"] = val

        # Anexo I-HI: DVP (Demonstração das Variações Patrimoniais)
        elif anexo == "DCA-Anexo I-HI":
            exercicio_data["dvp"].append({
                "conta": conta,
                "coluna": coluna,
                "valor": val
            })

    # Ajustes finais dos cálculos
    rec_bruta = exercicio_data["resumo"]["receita_bruta"]
    deducoes = exercicio_data["resumo"]["deducoes_receita"]
    rec_liq = round(rec_bruta - deducoes, 2) if rec_bruta > 0 else 0.0
    desp_liq = exercicio_data["resumo"]["despesa_liquidada"]

    exercicio_data["resumo"]["receita_liquida"] = rec_liq
    exercicio_data["resumo"]["resultado_orcamentario"] = round(rec_liq - desp_liq, 2)

    return exercicio_data

def sincronizar_dca():
    print("\n--- Sincronizando DCA (Balanços e Contas Anuais) ---")
    anos_coletados = []

    for ano in ANOS_CONSULTA:
        print(f"  Consultando balanço anual de {ano}...")
        dado = processar_ano_dca(ano)
        if dado:
            anos_coletados.append(dado)
            res = dado["resumo"]
            print(f"    -> OK! Ativo: R$ {res['ativo_total']:,.2f} | Receita Líq: R$ {res['receita_liquida']:,.2f} | Despesa Líq: R$ {res['despesa_liquidada']:,.2f}")
        else:
            print(f"    -> Balanço não disponível para {ano}.")
        time.sleep(0.5)

    if not anos_coletados:
        print("[Aviso] Nenhum dado de DCA coletado.")
        return False

    anos_coletados.sort(key=lambda x: x["exercicio"], reverse=True)

    dados_finais = {
        "metadata": {
            "ente": "Município de Coronel Barros - RS (Consolidado com Poder Legislativo)",
            "cod_ibge": COD_IBGE,
            "municipio": "Coronel Barros",
            "uf": "RS",
            "fonte": "Secretaria do Tesouro Nacional - SICONFI / Declaração de Contas Anuais (DCA)",
            "data_sincronizacao": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_exercicios": len(anos_coletados),
            "exercicios_disponiveis": [x["exercicio"] for x in anos_coletados]
        },
        "exercicios": anos_coletados
    }

    caminho_saida = os.path.join(os.path.dirname(__file__), "..", "data", "balancos.json")
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(dados_finais, f, ensure_ascii=False, indent=2)

    print(f"  [OK] DCA consolidado com {len(anos_coletados)} exercícios em {os.path.abspath(caminho_saida)}")
    return True

# ==============================================================================
# MAIN
# ==============================================================================

def main():
    print("=" * 65)
    print(f"Sincronização Completa SICONFI - {ENTE_NOME}")
    print(f"Data: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 65)

    ok_rgf = sincronizar_rgf()
    ok_dca = sincronizar_dca()

    print("\n" + "=" * 65)
    if ok_rgf or ok_dca:
        print("Sincronização concluída com êxito!")
    else:
        print("Aviso: Houve falhas na coleta dos dados.")
    print("=" * 65)

if __name__ == "__main__":
    main()
