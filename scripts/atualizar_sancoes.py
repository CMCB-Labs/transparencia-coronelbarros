#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manutenção do Cadastro de Sanções Administrativas e Inidoneidade
Câmara Municipal de Coronel Barros - RS (CNPJ: 13.847.938/0001-93)
Fontes:
  - Lei Federal nº 14.133/2021 (Art. 156 e 161)
  - Portal da Transparência CGU (CEIS / CNEP / CEPIM)
  - Tribunal de Contas do Estado do RS (TCE-RS)
  - Tribunal de Contas da União (TCU)
"""

import json
import os
from datetime import datetime, timezone

def atualizar_sancoes():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, ".."))
    data_dir = os.path.join(repo_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    caminho_sancoes = os.path.join(data_dir, "sancoes.json")

    dados = None
    if os.path.exists(caminho_sancoes):
        try:
            with open(caminho_sancoes, "r", encoding="utf-8") as f:
                dados = json.load(f)
        except Exception:
            pass

    if not dados:
        dados = {
            "ente": "Câmara Municipal de Coronel Barros - RS",
            "cnpj": "13.847.938/0001-93",
            "orgao_tce": 75101,
            "total_sancoes_ativas": 0,
            "declaracao_negativa": {
                "possui_sancoes": False,
                "titulo": "Certidão Institucional de Inexistência de Sanções Vigentes",
                "texto": "Certifica-se que, perante o Poder Legislativo Municipal de Coronel Barros - RS, NÃO CONSTAM penalidades administrativas vigentes aplicadas a fornecedores, licitantes ou prestadores de serviços (tais como impedimento de licitar e contratar, suspensão temporária ou declaração de inidoneidade), com fundamento no art. 156 da Lei Federal nº 14.133/2021.",
                "base_legal": "Art. 156 e 161 da Lei Federal nº 14.133/2021 e Lei Federal nº 12.846/2013"
            },
            "cadastros_oficiais": [
                {
                    "sigla": "CEIS",
                    "nome": "Cadastro Nacional de Empresas Inidôneas e Suspensas",
                    "orgao": "Controladoria-Geral da União (CGU)",
                    "descricao": "Reúne pessoas físicas e jurídicas impedidas de licitar ou contratar com a Administração Pública em todas as esferas federativas.",
                    "url_base": "https://portaldatransparencia.gov.br/sancoes/consulta?paginacaoSimples=true&tamanhoPagina=15&offset=0&direcaoOrdenacao=asc&cadastro=1",
                    "parametro_busca": "palavraChave",
                    "parametro_doc": "cpfCnpj"
                },
                {
                    "sigla": "CNEP",
                    "nome": "Cadastro Nacional de Empresas Punidas",
                    "orgao": "Controladoria-Geral da União (CGU)",
                    "descricao": "Relação de empresas que sofreram penalidades com base na Lei Anticorrupção (Lei Federal nº 12.846/2013).",
                    "url_base": "https://portaldatransparencia.gov.br/sancoes/consulta?paginacaoSimples=true&tamanhoPagina=15&offset=0&direcaoOrdenacao=asc&cadastro=2",
                    "parametro_busca": "palavraChave",
                    "parametro_doc": "cpfCnpj"
                },
                {
                    "sigla": "CEPIM",
                    "nome": "Cadastro de Entidades Sem Fins Lucrativos Impedidas",
                    "orgao": "Controladoria-Geral da União (CGU)",
                    "descricao": "Entidades privadas sem fins lucrativos impedidas de celebrar convênios e parcerias com o poder público.",
                    "url_base": "https://portaldatransparencia.gov.br/sancoes/consulta?paginacaoSimples=true&tamanhoPagina=15&offset=0&direcaoOrdenacao=asc&cadastro=3",
                    "parametro_busca": "palavraChave",
                    "parametro_doc": "cpfCnpj"
                },
                {
                    "sigla": "TCE-RS",
                    "nome": "Relação de Inidôneos e Inabilitados do RS",
                    "orgao": "Tribunal de Contas do Estado do RS",
                    "descricao": "Relação de administradores e responsáveis declarados inidôneos para o exercício de cargo público ou licitar no RS.",
                    "url_base": "https://portal.tce.rs.gov.br/app/pesquisa/jurisprudencia/",
                    "parametro_busca": "termo"
                },
                {
                    "sigla": "TCU",
                    "nome": "Certidão Consolidada de Inidôneos e Inabilitados",
                    "orgao": "Tribunal de Contas da União (TCU)",
                    "descricao": "Emissão de certidão negativa unificada sobre inidoneidade para licitar perante a Administração Pública Federal.",
                    "url_base": "https://contas.tcu.gov.br/ords/f?p=1660:2:::NO:::",
                    "parametro_busca": "p_cpf_cnpj"
                }
            ],
            "sancoes_aplicadas": []
        }

    dados["data_atualizacao"] = datetime.now(timezone.utc).isoformat()
    dados["total_sancoes_ativas"] = len(dados.get("sancoes_aplicadas", []))

    with open(caminho_sancoes, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    print(f"[Sanções] Arquivo atualizado: {caminho_sancoes}")
    print(f"  - Sanções ativas da Câmara: {dados['total_sancoes_ativas']}")

def main():
    print("=" * 70)
    print("SINCRONIZAÇÃO DO CADASTRO DE SANÇÕES ADMINISTRATIVAS")
    print("Câmara Municipal de Coronel Barros - RS")
    print("=" * 70)
    atualizar_sancoes()

if __name__ == "__main__":
    main()
