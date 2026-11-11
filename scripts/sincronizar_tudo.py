#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orquestrador Geral de Sincronização da Transparência
Câmara Municipal de Coronel Barros - RS

Executa em sequência:
1. Siconfi / STN: RGF, DCA (Balanços) e RREO
2. TCE-RS: Jurisprudência, Pareceres Prévios e Julgamentos de Contas
3. TCE-RS / LicitaCon: Licitações e Contratos
4. PNCP / Planejamento: Plano de Contratações Anual (PCA)
5. CGU / TCE-RS: Sanções Administrativas e Inidoneidade
"""

import subprocess
import sys
import os

def run_script(script_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir, script_name)
    print(f"\n>>> Executando {script_name}...")
    res = subprocess.run([sys.executable, path])
    if res.returncode != 0:
        print(f"[Aviso] Script {script_name} finalizou com código {res.returncode}")
    else:
        print(f"[Sucesso] {script_name} concluído com sucesso!")

def main():
    print("=" * 70)
    print("INICIANDO SINCRONIZAÇÃO COMPLETA DA TRANSPARÊNCIA")
    print("Câmara Municipal de Coronel Barros - RS")
    print("=" * 70)

    # 1. Siconfi (RGF, DCA Balanços, RREO)
    run_script("atualizar_siconfi.py")

    # 2. TCE-RS (Julgamentos e Pareceres Prévios)
    run_script("atualizar_tce.py")

    # 3. TCE-RS / LicitaCon (Licitações e Contratos)
    run_script("atualizar_licitacon.py")

    # 4. PNCP / Planejamento (Plano de Contratações Anual)
    run_script("atualizar_pca.py")

    # 5. Sanções e Inidoneidade (CEIS / CNEP / Câmara)
    run_script("atualizar_sancoes.py")

    # 6. Receitas e Repasses do Duodécimo (TCE-RS)
    run_script("atualizar_receitas.py")

    # 7. Patrimônio: Imóveis, Veículos e Obras (TCE-RS & Inventário)
    run_script("atualizar_patrimonio.py")

    print("\n" + "=" * 70)
    print("TODOS OS DADOS FORAM ATUALIZADOS!")
    print("=" * 70)

if __name__ == "__main__":
    main()
