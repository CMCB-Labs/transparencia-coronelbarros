# Central de Transparência da Câmara Municipal de Coronel Barros - RS

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Deploy-006838?style=flat-square&logo=github)](https://cmcb-labs.github.io/transparencia-coronelbarros/)
[![TCE-RS](https://img.shields.io/badge/TCE--RS-Dados%20Abertos%20(75101)-009739?style=flat-square)](https://dados.tce.rs.gov.br/)
[![SICONFI](https://img.shields.io/badge/STN-SICONFI-0369A1?style=flat-square)](https://siconfi.tesouro.gov.br/)
[![PNTP Atricon](https://img.shields.io/badge/PNTP%20Atricon-100%25%20Conforme-FFCC00?style=flat-square&logoColor=black)](https://transparencia.atricon.org.br/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://www.python.org/)

Repositório central de módulos e componentes interativos de transparência pública, controle fiscal e prestação de contas da **Câmara Municipal de Coronel Barros - RS** (CNPJ: `13.847.938/0001-93`, Código TCE-RS: `75101`, IBGE: `4305871`).

Desenvolvido para incorporação transparente (**embed via iframe**) no **Portal Modelo / Interlegis (Plone)**, com integração direta aos dados abertos oficiais do **TCE-RS**, **Siconfi/STN**, **LicitaCon Cidadão** e **PNCP**.

---

## 🌐 Páginas Publicadas e Módulos Disponíveis

Todos os módulos possuem **fundo 100% transparente**, tipografia oficial **Montserrat**, design responsivo, suporte a modo escuro/claro e **sincronização automática de rolagem (roda do mouse `cb-wheel`)** e redimensionamento de altura (`cb-resize`).

| Módulo / Tema | Descrição e Recursos | Link Direto (GitHub Pages) | Destino no Portal Interlegis |
| :--- | :--- | :--- | :--- |
| **Painel Geral (Hub)** | Central unificada com acesso a todos os módulos e indicadores fiscais. | [Acessar Hub](https://cmcb-labs.github.io/transparencia-coronelbarros/index.html) | `/transparencia` |
| **Relatório de Gestão Fiscal (RGF)** | Demonstrativo da despesa com pessoal e limites prudenciais da LRF (LC 101/2000). | [Acessar RGF](https://cmcb-labs.github.io/transparencia-coronelbarros/rgf.html) | `/transparencia/orcamento-e-financas/rgf` |
| **Balanços Anuais (DCA)** | Balanço Patrimonial, Balanço Orçamentário, DVP e despesas por função (STN). | [Acessar Balanços](https://cmcb-labs.github.io/transparencia-coronelbarros/balancos.html) | `/transparencia/contas-publicas/balancos-anuais` |
| **Execução Orçamentária (RREO)** | Acompanhamento da execução de receitas e despesas por bimestre municipal. | [Acessar RREO](https://cmcb-labs.github.io/transparencia-coronelbarros/rreo.html) | `/transparencia/orcamento-e-financas/rreo` |
| **Receitas e Duodécimo** | Repasses mensais do duodécimo (art. 168 CF), teto de 7% (art. 29-A CF) e histórico de devoluções à Prefeitura. | [Acessar Receitas](https://cmcb-labs.github.io/transparencia-coronelbarros/receitas.html) | `/transparencia/orcamento-e-financas/receitas` |
| **Julgamento de Contas (Geral)** | Julgamentos e pareceres prévios emitidos pelo TCE-RS (Legislativo e Executivo). | [Acessar Julgamentos](https://cmcb-labs.github.io/transparencia-coronelbarros/julgamentos.html) | `/transparencia/contas-publicas/julgamentos-tce` |
| **Contas da Câmara** | Julgamentos específicos das contas anuais dos Presidentes da Câmara (TCE-RS). | [Acessar Contas Câmara](https://cmcb-labs.github.io/transparencia-coronelbarros/julgamentos_camara.html) | `/transparencia/contas-publicas/julgamentos-camara` |
| **Contas do Executivo** | Pareceres prévios e julgamento das contas de governo dos Prefeitos Municipais. | [Acessar Contas Executivo](https://cmcb-labs.github.io/transparencia-coronelbarros/julgamentos_executivo.html) | `/transparencia/contas-publicas/julgamentos-executivo` |
| **Licitações e Editais** | Processos licitatórios, dispensas e inexigibilidades com links diretos aos PDFs e LicitaCon. | [Acessar Licitações](https://cmcb-labs.github.io/transparencia-coronelbarros/licitacoes.html) | `/transparencia/licitacoes-e-contratos/licitacoes` |
| **Contratos e Aditivos** | Contratos administrativos, termos aditivos, vigência calculada e links aos editais. | [Acessar Contratos](https://cmcb-labs.github.io/transparencia-coronelbarros/contratos.html) | `/transparencia/licitacoes-e-contratos/contratos` |
| **Plano de Contratações (PCA)** | Planejamento anual de compras públicas com virada automática de exercício (PNCP / Lei 14.133/2021). | [Acessar PCA](https://cmcb-labs.github.io/transparencia-coronelbarros/plano_contratacoes.html) | `/transparencia/licitacoes-e-contratos/plano-anual` |
| **Sanções Administrativas** | Certidão Negativa de Inidoneidade da Câmara e central de consulta aos 5 cadastros nacionais (CEIS, CNEP, CEPIM, TCE-RS, TCU). | [Acessar Sanções](https://cmcb-labs.github.io/transparencia-coronelbarros/sancoes.html) | `/transparencia/licitacoes-e-contratos/sancoes` |
| **Bens Imóveis e Sede** | Relação do prédio da Sede Legislativa (cessão de uso gratuito, R$ 0,00 de aluguel) e série histórica (2021-2026). | [Acessar Imóveis](https://cmcb-labs.github.io/transparencia-coronelbarros/imoveis.html) | `/transparencia/patrimonio/imoveis` |
| **Frota Oficial de Veículos** | Declaração de Frota Zero (sem custos com veículos, combustível ou seguro) e série histórica (2021-2026). | [Acessar Veículos](https://cmcb-labs.github.io/transparencia-coronelbarros/veiculos.html) | `/transparencia/patrimonio/veiculos` |
| **Obras Públicas** | Declaração Negativa de Obras da Câmara, divisão de competências e canal de fiscalização das obras da Prefeitura. | [Acessar Obras](https://cmcb-labs.github.io/transparencia-coronelbarros/obras.html) | `/transparencia/patrimonio/obras` |

---

## 🏛️ Fontes de Dados e Integrações Oficiais

```
                                 FONTES OFICIAIS DE DADOS
  ┌───────────────────────┬────────────────────────┬──────────────────────┬──────────────────────┐
  │     SICONFI / STN     │    TCE-RS BALANCETES   │   LICITACON CIDADÃO  │  PORTAL PNCP / CGU   │
  │   - RGF Simplificado  │  - Balancete Verif.    │  - Licitações        │  - Plano de Compras  │
  │   - Balanços (DCA)    │  - Balancete Despesa   │  - Contratos         │  - Cadastros CEIS /  │
  │   - RREO Bimestral    │  - Repasses Duodécimo  │  - Termos Aditivos   │    CNEP / CEPIM      │
  └───────────┬───────────┴───────────┬────────────┴──────────┬───────────┴──────────┬───────────┘
              │                       │                       │                      │
              ▼                       ▼                       ▼                      ▼
  ┌──────────────────────────────────────────────────────────────────────────────────────────────┐
  │                           ROBÔS DE EXTRAÇÃO E SINCRONIZAÇÃO (PYTHON)                         │
  │       scripts/sincronizar_tudo.py  ──>  Atualiza todas as bases de dados em data/*.json     │
  └──────────────────────────────────────────────┬───────────────────────────────────────────────┘
                                                 │
                                                 ▼
  ┌──────────────────────────────────────────────────────────────────────────────────────────────┐
  │                            GITHUB PAGES (DEPLOY CONTÍNUO / HTTPS)                            │
  │         Páginas autônomas, leves, com fundo transparente e responsividade total              │
  └──────────────────────────────────────────────┬───────────────────────────────────────────────┘
                                                 │ (Incorporação via Iframe sem scrollbar dupla)
                                                 ▼
  ┌──────────────────────────────────────────────────────────────────────────────────────────────┐
  │                       PORTAL DA CÂMARA MUNICIPAL DE CORONEL BARROS - RS                      │
  │                       (Portal Modelo / Interlegis / Plone - Layout Oficial)                  │
  └──────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Estrutura do Repositório

```text
transparencia-coronelbarros/
├── data/                               # Bases de dados JSON consolidadas
│   ├── balancos.json                   # Balanços e Contas Anuais DCA / Siconfi
│   ├── contratos.json                  # Contratos administrativos e termos aditivos
│   ├── julgamentos.json                # Julgamentos e pareceres prévios TCE-RS
│   ├── licitacoes.json                 # Processos licitatórios do LicitaCon
│   ├── patrimonio.json                 # Imóveis, veículos, obras e série histórica
│   ├── pca.json                        # Plano de Contratações Anual
│   ├── receitas.json                   # Repasses do duodécimo e devoluções
│   ├── rgf.json                        # Relatório de Gestão Fiscal (LRF)
│   ├── rreo.json                       # Relatório Resumido de Execução Orçamentária
│   └── sancoes.json                    # Certidões e cadastros de sanções
├── scripts/                            # Robôs de coleta e automação
│   ├── atualizar_licitacon.py          # Coleta licitações e contratos via LicitaCon
│   ├── atualizar_patrimonio.py         # Coleta patrimônio e série histórica no TCE-RS
│   ├── atualizar_pca.py                # Atualiza planejamento de contratações
│   ├── atualizar_receitas.py           # Coleta repasses e duodécimos no TCE-RS
│   ├── atualizar_sancoes.py            # Atualiza certidões de idoneidade
│   ├── atualizar_siconfi.py            # Coleta RGF, DCA e RREO no Siconfi
│   ├── atualizar_tce.py                # Coleta jurisprudência e julgamentos TCE-RS
│   └── sincronizar_tudo.py             # Orquestrador geral de atualização
├── balancos.html                       # Módulo de Balanços Anuais
├── contratos.html                      # Módulo de Contratos e Aditivos
├── imoveis.html                        # Módulo de Bens Imóveis e Sede
├── index.html                          # Hub Principal de Navegação
├── julgamentos.html                    # Módulo Geral de Julgamentos TCE-RS
├── julgamentos_camara.html             # Módulo Julgamentos da Câmara
├── julgamentos_executivo.html          # Módulo Pareceres Prévios do Prefeito
├── licitacoes.html                     # Módulo de Licitações e Editais
├── obras.html                          # Módulo de Obras Públicas
├── plano_contratacoes.html             # Módulo de Plano de Contratações Anual
├── receitas.html                       # Módulo de Receitas e Duodécimo
├── rgf.html                            # Módulo de Relatório de Gestão Fiscal
├── rreo.html                           # Módulo de Execução Orçamentária
├── sancoes.html                        # Módulo de Sanções e Inidoneidade
├── veiculos.html                       # Módulo de Frota Oficial de Veículos
├── .gitignore
└── README.md                           # Documentação técnica e guia de links
```

---

## 💻 Como Incorporar no Portal da Câmara (Portal Modelo / Plone)

Cada módulo conta com um arquivo de incorporação pronto em `paginas/transparencia/*_embed.html`.

Para incorporar qualquer uma das páginas no portal da Câmara:
1. Abra a página desejada no Portal Modelo / Plone.
2. No editor **TinyMCE**, clique no botão **Visualizar Código-Fonte** (`<>`) ou utilize um **Tile de Conteúdo Incorporado**.
3. Cole o modelo padrão abaixo (ajustando o `id`, `src` e `title` da página desejada):

```html
<div class="cb-container cb-embed-container" style="width: 100%; max-width: 1180px; margin: 0 auto; background: transparent;">
  <iframe 
    id="cb-iframe-modulo"
    src="https://cmcb-labs.github.io/transparencia-coronelbarros/NOME_DA_PAGINA.html" 
    style="width: 100%; border: none; min-height: 400px; background: transparent; display: block;" 
    title="Transparência - Câmara Municipal de Coronel Barros"
    loading="lazy">
  </iframe>
</div>

<script>
  // Script de redimensionamento e sincronização de scroll da roda do mouse
  (function() {
    var lastReceivedHeight = 0;
    window.addEventListener('message', function(e) {
      if (!e.data) return;

      // 1. Redimensionamento automático estritamente protegido contra loops infinitos
      if (e.data.type === 'cb-resize' && typeof e.data.height === 'number') {
        var el = document.getElementById('cb-iframe-modulo');
        var newHeight = Math.ceil(e.data.height);
        if (el && Math.abs(newHeight - lastReceivedHeight) > 4) {
          lastReceivedHeight = newHeight;
          el.style.height = newHeight + 'px';
        }
      }

      // 2. Encaminhamento de scroll da roda do mouse quando o cursor está sobre o iframe
      if (e.data.type === 'cb-wheel' && typeof e.data.deltaY === 'number') {
        window.scrollBy({
          top: e.data.deltaY,
          behavior: 'auto'
        });
      }
    });
  })();
</script>
```

---

## 🚀 Como Executar a Atualização dos Dados

Para sincronizar todas as bases de dados locais com os servidores do TCE-RS, Siconfi e PNCP:

```bash
# Executar a sincronização completa de todos os módulos
python scripts/sincronizar_tudo.py
```

Para rodar apenas um módulo específico:

```bash
python scripts/atualizar_siconfi.py     # RGF, Balanços e RREO
python scripts/atualizar_licitacon.py   # Licitações e Contratos
python scripts/atualizar_receitas.py    # Repasses do Duodécimo
python scripts/atualizar_patrimonio.py  # Imóveis, Veículos e Obras
python scripts/atualizar_tce.py         # Julgamento de Contas
python scripts/atualizar_pca.py         # Plano de Contratações
python scripts/atualizar_sancoes.py     # Sanções e Inidoneidade
```

---

## ⚖️ Conformidade Legal e Controle Externo

Os módulos foram concebidos em estrita conformidade com:
* **Constituição da República Federativa do Brasil** (Arts. 29-A, 37, 165 e 168);
* **Lei Complementar nº 101/2000** (Lei de Responsabilidade Fiscal - LRF);
* **Lei Federal nº 12.527/2011** (Lei de Acesso à Informação - LAI);
* **Lei Federal nº 14.133/2021** (Nova Lei de Licitações e Contratos Administrativos);
* **Resoluções e Instruções Normativas do TCE-RS** (Tribunal de Contas do Estado do Rio Grande do Sul);
* **Critérios do Programa Nacional de Transparência Pública (PNTP / Atricon)**.
