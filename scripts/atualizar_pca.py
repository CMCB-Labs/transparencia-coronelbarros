#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sincronização e Manutenção do Plano de Contratações Anual (PCA)
Câmara Municipal de Coronel Barros - RS (CNPJ: 13.847.938/0001-93)
Fonte: Portal Nacional de Contratações Públicas (PNCP) / Lei nº 14.133/2021
"""

import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

CNPJ_CAMARA = "13847938000193"
PRIMEIRO_ANO_PCA = 2027

def carregar_pca_existente(caminho):
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Aviso] Erro ao ler PCA existente: {e}")
    return None

def tentar_consulta_pncp(ano, retries=2):
    """
    Tenta consultar a API de consulta do PNCP para verificar se há PCA publicado.
    Caso a API retorne 429 ou não responda, continua normalmente com a base local.
    """
    url = f"https://pncp.gov.br/api/consulta/v1/pca/atualizacao?dataInicio={ano}0101&dataFim={ano}1231&cnpj={CNPJ_CAMARA}&pagina=1&tamanhoPagina=10"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "TransparenciaCoronelBarros/1.0 (camara@coronelbarros.rs.gov.br)",
            "Accept": "application/json"
        }
    )
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    dados = json.loads(resp.read().decode("utf-8"))
                    return dados
        except Exception as e:
            # PNCP pode limitar requisições (429) ou ainda não ter o cadastro
            pass
        time.sleep(1)
    return None

def sincronizar_pca():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, ".."))
    data_dir = os.path.join(repo_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    caminho_pca = os.path.join(data_dir, "pca.json")

    pca_data = carregar_pca_existente(caminho_pca)
    if not pca_data:
        pca_data = {
            "ente": "Câmara Municipal de Coronel Barros - RS",
            "cnpj": "13.847.938/0001-93",
            "orgao_tce": 75101,
            "fonte": "Portal Nacional de Contratações Públicas (PNCP) / Lei nº 14.133/2021",
            "base_legal": "Art. 12, inciso VII da Lei Federal nº 14.133/2021",
            "primeiro_ano_planejamento": PRIMEIRO_ANO_PCA,
            "planos": {}
        }

    ano_atual = datetime.now().year
    ano_proximo = ano_atual + 1

    planos = pca_data.setdefault("planos", {})

    # Garantir anos históricos recentes
    for ano in range(2025, ano_atual + 1):
        ano_str = str(ano)
        if ano_str not in planos:
            planos[ano_str] = {
                "ano": ano,
                "status": "nao_instituido",
                "status_label": "Não Instituído",
                "status_classe": "badge-neutral",
                "mensagem": f"No exercício de {ano}, a Câmara Municipal não instituiu Plano de Contratações Anual, passando a adotá-lo a partir do ciclo de planejamento de {PRIMEIRO_ANO_PCA}.",
                "valor_total_estimado": 0.0,
                "total_itens": 0,
                "itens": []
            }

    # Garantir o próximo exercício (Em Elaboração se ainda não publicado)
    ano_prox_str = str(ano_proximo)
    if ano_prox_str not in planos:
        planos[ano_prox_str] = {
            "ano": ano_proximo,
            "status": "em_elaboracao",
            "status_label": "Em Elaboração",
            "status_classe": "badge-warning",
            "mensagem": f"O Plano de Contratações Anual para o exercício de {ano_proximo} encontra-se em fase de levantamento de demandas e consolidação pelas unidades administrativas da Câmara Municipal.",
            "etapas": [
                { "ordem": 1, "nome": "Levantamento de Demandas Setoriais", "status": "em_andamento" },
                { "ordem": 2, "nome": "Consolidação e Estimativa de Custos", "status": "pendente" },
                { "ordem": 3, "nome": "Aprovação pela Mesa Diretora / Presidência", "status": "pendente" },
                { "ordem": 4, "nome": "Publicação no PNCP e Portal da Transparência", "status": "pendente" }
            ],
            "valor_total_estimado": 0.0,
            "total_itens": 0,
            "itens": []
        }

    pca_data["data_atualizacao"] = datetime.now(timezone.utc).isoformat()
    pca_data["ano_vigente"] = ano_atual
    pca_data["ano_em_elaboracao"] = ano_proximo

    with open(caminho_pca, "w", encoding="utf-8") as f:
        json.dump(pca_data, f, ensure_ascii=False, indent=2)

    print(f"[PCA] Base de planejamento atualizada: {caminho_pca}")
    print(f"  - Exercício Vigente: {ano_atual}")
    print(f"  - Exercício em Elaboração: {ano_proximo}")

def main():
    print("=" * 70)
    print("SINCRONIZAÇÃO DO PLANO DE CONTRATAÇÕES ANUAL (PCA)")
    print("Câmara Municipal de Coronel Barros - RS")
    print("=" * 70)
    sincronizar_pca()

if __name__ == "__main__":
    main()
