# Central de Transparência Fiscal — Câmara Municipal de Coronel Barros - RS

Módulo automatizado de geração de dados e relatórios de transparência fiscal para incorporação (**embed**) no portal oficial da **Câmara Municipal de Coronel Barros - RS** (Portal Modelo / Interlegis / Plone).

---

## 🎯 Arquitetura da Solução

```
+-------------------------------------------------------------+
|              API SICONFI (Tesouro Nacional / STN)           |
|        Endpoint RGF Simplificado • Código IBGE: 4305871      |
+------------------------------+------------------------------+
                               | (1. Execução mensal agendada)
                               v
+-------------------------------------------------------------+
|               GITHUB ACTIONS (.github/workflows)             |
|   - Roda no dia 1º de cada mês às 06:00 UTC (ou sob demanda)|
|   - Executa: scripts/atualizar_siconfi.py                   |
|   - Consolida anos/semestres em data/rgf.json               |
|   - Faz commit e publica no GitHub Pages                    |
+------------------------------+------------------------------+
                               | (2. Deploy estático CDN)
                               v
+-------------------------------------------------------------+
|                    GITHUB PAGES (HTTPS / CDN)               |
|   - rgf.html / index.html (Layout responsivo com embed)     |
|   - data/rgf.json (Acesso ultra rápido e CORS liberado)     |
+------------------------------+------------------------------+
                               | (3. Incorporação via iframe)
                               v
+-------------------------------------------------------------+
|       PORTAL DA CÂMARA (Portal Modelo / Interlegis)         |
|   - Incorporado na página de Transparência / Gestão Fiscal  |
|   - Fundo 100% transparente, sem cabeçalhos repetidos       |
+-------------------------------------------------------------+
```

---

## 📦 Estrutura de Arquivos

```text
transparencia-coronelbarros/
├── .github/
│   └── workflows/
│       └── atualizar_dados.yml    # Workflow agendado (mensal)
├── data/
│   ├── rgf.json                   # Base de dados estruturada do RGF (Gestão Fiscal)
│   └── balancos.json              # Base de dados estruturada dos Balanços (DCA)
├── scripts/
│   └── atualizar_siconfi.py       # Robô coletor em Python (RGF + DCA)
├── rgf.html                       # Página do RGF para EMBED (fundo transparente)
├── balancos.html                  # Página dos Balanços Anuais para EMBED
├── index.html                     # Entrada padrão no GitHub Pages
├── .gitignore
└── README.md                      # Manual técnico de incorporação
```

---

## 💻 Como Incorporar no Portal da Câmara (Plone / Portal Modelo)

Como a página foi desenhada com **fundo transparente** e **sem menus ou cabeçalhos externos**, ela se integra naturalmente como se fosse parte nativa do portal.

### Código para colar no TinyMCE (Visualização de Código HTML) ou Tile de Conteúdo:

```html
<div style="width: 100%; max-width: 1180px; margin: 0 auto; overflow: hidden; background: transparent;">
  <iframe 
    id="cb-iframe-rgf"
    src="https://cmcb-labs.github.io/transparencia-coronelbarros/rgf.html" 
    style="width: 100%; border: none; min-height: 800px; background: transparent; overflow: hidden; display: block;" 
    title="Relatório de Gestão Fiscal - Câmara Municipal de Coronel Barros"
    scrolling="no"
    loading="lazy">
  </iframe>
</div>

<script>
  // Ajuste automático de altura seguro contra loops infinitos
  (function() {
    var lastReceivedHeight = 0;
    window.addEventListener('message', function(e) {
      if (e.data && e.data.type === 'cb-resize' && typeof e.data.height === 'number') {
        var iframe = document.getElementById('cb-iframe-rgf');
        var newH = Math.ceil(e.data.height);
        if (iframe && Math.abs(newH - lastReceivedHeight) > 4) {
          lastReceivedHeight = newH;
          iframe.style.height = newH + 'px';
        }
      }
    });
  })();
</script>
```

---

## ⚙️ Execução e Testes Manuais

Para rodar a extração localmente em sua máquina:

```bash
python scripts/atualizar_siconfi.py
```

Para acionar a sincronização pelo GitHub:
1. Acesse a aba **Actions** no repositório do GitHub.
2. Selecione o fluxo **Sincronização Mensal SICONFI (RGF Coronel Barros)**.
3. Clique em **Run workflow**.
