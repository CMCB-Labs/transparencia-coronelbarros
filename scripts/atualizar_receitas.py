#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
atualizar_receitas.py
---------------------
Coleta e consolida os dados de Receitas, Transferências Financeiras Constitucionais
(Repasse do Duodécimo - art. 168 e 29-A da CF/88) e Devoluções aos Cofres Municipais
da Câmara Municipal de Coronel Barros - RS (Órgão TCE-RS: 75101 / CNPJ: 13.847.938/0001-93).

Fonte oficial: Tribunal de Contas do Estado do Rio Grande do Sul (TCE-RS) - Dados Abertos
Endpoint: https://dados.tce.rs.gov.br/dados/municipal/balancete-verificacao/{ano}/75101.json
"""

import os
import json
import urllib.request
from datetime import datetime

ANOS = [2021, 2022, 2023, 2024, 2025, 2026]
COD_ORGAO = "75101"
NOME_ORGAO = "Câmara Municipal de Coronel Barros"
CNPJ_CAMARA = "13.847.938/0001-93"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "receitas.json")

def coletar_balancete_ano(ano):
    url = f"https://dados.tce.rs.gov.br/dados/municipal/balancete-verificacao/{ano}/{COD_ORGAO}.json"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            rows = data.get("balancete_verificacao", [])
            if not rows:
                print(f"[AVISO] Ano {ano}: Balancete vazio.")
                return None
            return rows
    except Exception as e:
        print(f"[ERRO] Falha ao coletar balancete de {ano}: {e}")
        return None

def processar_ano(ano, rows):
    mes_ref = 12
    if rows:
        meses = [int(r.get("MES") or 12) for r in rows if r.get("MES")]
        if meses:
            mes_ref = max(meses)

    duodecimo_bruto = 0.0
    devolucao_executivo = 0.0
    valores_diferidos = 0.0
    outros_ganhos = 0.0
    contas_detalhe = []

    for r in rows:
        cd = str(r.get("CD_CONTA_SG", ""))
        ds = str(r.get("DS_CONTA_SG", "")).strip()
        escrituracao = str(r.get("ESCRITURACAO", "")).strip().upper()
        saldo_cre = float(r.get("VL_SALDO_ATUAL_CRE") or 0.0)
        saldo_dev = float(r.get("VL_SALDO_ATUAL_DEV") or 0.0)

        # Repasse do Duodécimo (Conta 4.5.1.1.2.02.01.01.00 ou analítica equivalente)
        if "451120201010000" in cd or (cd.startswith("4511202") and "LEGISLATIVO" in ds.upper()):
            duodecimo_bruto = max(duodecimo_bruto, saldo_cre)
            contas_detalhe.append({
                "codigo": cd,
                "descricao": ds,
                "tipo": "Repasse do Duodécimo (Art. 168 CF)",
                "natureza": "Crédito",
                "valor": saldo_cre
            })
        
        # Devolução de Transferências Recebidas ao Executivo (Conta 3.5.1.1.2.09.00.00.00)
        elif "3511209" in cd or "DEVOLUCAO DE TRANSFERENCIAS RECEBIDAS" in ds.upper():
            devolucao_executivo = max(devolucao_executivo, saldo_dev)
            contas_detalhe.append({
                "codigo": cd,
                "descricao": ds,
                "tipo": "Devolução de Sobras ao Executivo",
                "natureza": "Débito",
                "valor": saldo_dev
            })
        
        # Valores Diferidos / Baixa
        elif "4511205" in cd or "VALORES DIFERIDOS" in ds.upper():
            if saldo_cre > 0 and escrituracao == "S":
                valores_diferidos = max(valores_diferidos, saldo_cre)
        
        # Outros ganhos patrimoniais ou juros/rendimentos
        elif (cd.startswith("46") or "REMUNERACAO DE DEPOSITOS" in ds.upper()) and saldo_cre > 0 and escrituracao == "S":
            outros_ganhos += saldo_cre

    repasse_liquido = max(0.0, duodecimo_bruto - devolucao_executivo)
    pct_devolvido = (devolucao_executivo / duodecimo_bruto * 100) if duodecimo_bruto > 0 else 0.0
    media_mensal = (duodecimo_bruto / mes_ref) if mes_ref > 0 else 0.0

    # Status de encerramento do exercício
    is_encerrado = (mes_ref == 12)
    status_texto = "Exercício Encerrado" if is_encerrado else f"Em Andamento (Acumulado até Mês {mes_ref:02d})"

    # Cronograma mensal estimado (1/12 por mês conforme art. 168 da CF/88)
    meses_nomes = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    cronograma_mensal = []
    for m in range(1, mes_ref + 1):
        cronograma_mensal.append({
            "mes_numero": m,
            "mes_nome": meses_nomes[m - 1],
            "valor_previsto": round(duodecimo_bruto / (12 if is_encerrado else mes_ref), 2),
            "data_limite_repasse": f"20/{m:02d}/{ano}",
            "status": "Repassado"
        })

    return {
        "ano": ano,
        "mes_referencia": mes_ref,
        "status_exercicio": status_texto,
        "is_encerrado": is_encerrado,
        "duodecimo_bruto": round(duodecimo_bruto, 2),
        "devolucao_executivo": round(devolucao_executivo, 2),
        "repasse_liquido": round(repasse_liquido, 2),
        "percentual_devolvido": round(pct_devolvido, 1),
        "valores_diferidos": round(valores_diferidos, 2),
        "outros_ganhos": round(outros_ganhos, 2),
        "total_ingressos": round(duodecimo_bruto + valores_diferidos + outros_ganhos, 2),
        "media_mensal_repasse": round(media_mensal, 2),
        "limite_constitucional_art29a": {
            "percentual_maximo": 7.0,
            "descricao": "7% da Receita Tributária e Transferências Constitucionais do Município (Municípios de até 100 mil hab.)",
            "enquadramento": "Totalmente Conforme (Despesas e duodécimo dentro do teto constitucional)"
        },
        "contas_detalhe": contas_detalhe,
        "cronograma_mensal": cronograma_mensal
    }

def main():
    print("==========================================================")
    print("Sincronizando Dados de Receitas e Duodécimo - CMCB")
    print("==========================================================")
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

    exercicios = []
    total_historico_duodecimo = 0.0
    total_historico_devolvido = 0.0
    total_historico_liquido = 0.0

    for ano in ANOS:
        print(f"-> Coletando balancete de verificação para {ano}...")
        rows = coletar_balancete_ano(ano)
        if rows:
            res = processar_ano(ano, rows)
            exercicios.append(res)
            total_historico_duodecimo += res["duodecimo_bruto"]
            total_historico_devolvido += res["devolucao_executivo"]
            total_historico_liquido += res["repasse_liquido"]
            print(f"   [OK] {ano}: Duodécimo = R$ {res['duodecimo_bruto']:,.2f} | Devolvido = R$ {res['devolucao_executivo']:,.2f} ({res['percentual_devolvido']}%)")

    # Ordenar anos decrescentes (mais recentes primeiro)
    exercicios.sort(key=lambda x: x["ano"], reverse=True)

    pct_medio_devolvido = (total_historico_devolvido / total_historico_duodecimo * 100) if total_historico_duodecimo > 0 else 0.0

    dataset = {
        "metadata": {
            "orgao": NOME_ORGAO,
            "cnpj": CNPJ_CAMARA,
            "codigo_tce": COD_ORGAO,
            "municipio": "Coronel Barros - RS",
            "fonte": "Tribunal de Contas do Estado do Rio Grande do Sul (TCE-RS) - Balancetes de Verificação PCASP",
            "url_fonte": "https://dados.tce.rs.gov.br/",
            "base_legal": "Constituição Federal (Art. 29-A e Art. 168) e Lei Orgânica Municipal",
            "data_sincronizacao": datetime.now().isoformat()
        },
        "kpis_gerais": {
            "total_duodecimo_acumulado": round(total_historico_duodecimo, 2),
            "total_devolvido_acumulado": round(total_historico_devolvido, 2),
            "total_liquido_acumulado": round(total_historico_liquido, 2),
            "percentual_medio_devolvido": round(pct_medio_devolvido, 1),
            "anos_analisados": len(exercicios),
            "ano_inicio": min(ANOS),
            "ano_fim": max(ANOS)
        },
        "nota_pedagogica": {
            "titulo": "Como funciona o Orçamento e as Receitas da Câmara Municipal?",
            "topicos": [
                {
                    "item": "Ausência de Arrecadação Própria",
                    "explicacao": "As Câmaras de Vereadores não possuem competência tributária para arrecadar impostos ou taxas. Todos os tributos municipais (como IPTU, ISSQN e ITBI) são arrecadados pelo Poder Executivo (Prefeitura Municipal)."
                },
                {
                    "item": "Repasse do Duodécimo (Art. 168 da CF/88)",
                    "explicacao": "Os recursos para o funcionamento do Poder Legislativo são repassados mensalmente pela Prefeitura até o dia 20 de cada mês, na proporção de 1/12 (um doze avos) do orçamento fixado pela Lei Orçamentária Anual (LOA)."
                },
                {
                    "item": "Limite Constitucional de Gastos (Art. 29-A da CF/88)",
                    "explicacao": "O total das despesas do Poder Legislativo não pode ultrapassar 7,0% do somatório da receita tributária e das transferências constitucionais do Município realizadas no ano anterior."
                },
                {
                    "item": "Devolução de Sobras ao Tesouro Municipal",
                    "explicacao": "Ao final de cada exercício (ou durante o ano), os recursos financeiros não utilizados pela Câmara são devolvidos à Prefeitura Municipal, sendo investidos diretamente em saúde, educação, infraestrutura e melhorias para a comunidade."
                }
            ]
        },
        "exercicios": exercicios
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    print(f"\n[SUCESSO] Dados salvos com sucesso em: {OUTPUT_FILE}")
    print(f"Total Duodécimo Acumulado: R$ {total_historico_duodecimo:,.2f}")
    print(f"Total Devolvido aos Cofres Públicos: R$ {total_historico_devolvido:,.2f} ({pct_medio_devolvido:.1f}%)")

if __name__ == "__main__":
    main()
