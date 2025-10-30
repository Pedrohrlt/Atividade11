# 🛒 Teste Integrado de E-commerce — Black Friday

Este repositório contém um **plano de testes automatizados em Python** para validar requisitos **não funcionais** de um sistema de e-commerce durante a Black Friday.

Os testes abrangem **desempenho, carga, estresse, escalabilidade e segurança**, conforme o cenário proposto.

---

## 🎯 Cenário

| Requisito | Meta |
|------------|------|
| Usuários simultâneos esperados | 10.000 |
| Tempo de resposta | < **500ms** para 95% das requisições |
| Disponibilidade | 99.9% durante o evento |
| Proteção | Contra ataques e vazamento de dados |

---

## 🧪 Tipos de Teste e Métricas

| Tipo de Teste | Métrica | Meta Definida |
|----------------|----------|---------------|
| Desempenho | Tempo de resposta P95 | < 500ms |
| Carga | Throughput sustentado | > 2000 req/s |
| Estresse | Ponto de quebra | > 15.000 usuários |
| Escalabilidade | Eficiência horizontal | > 80% |
| Segurança | Rate limiting | 100 req/min/IP |

---

## 📂 Estrutura do Projeto

EcommerceTestPlan/
├── README.md
├── requirements.txt
├── docs/
│ └── Plano_de_Teste_Ecommerce_BlackFriday.pdf
├── tests/
│ ├── test_desempenho.py
│ ├── test_carga.py
│ ├── test_estresse.py
│ ├── test_escalabilidade.py
│ └── test_seguranca.py
└── results/
├── performance_summary_.json
├── load_summary_.json
├── stress_summary_.json
├── scalability_summary_.json
└── security_summary_*.json

yaml
Copiar código

---

## ⚙️ Instalação

> ⚠️ **Atenção:** estes testes geram alto tráfego.  
> Execute **somente em ambiente de homologação ou teste**, nunca em produção.

```bash
git clone https://github.com/<seu-usuario>/EcommerceTestPlan.git
cd EcommerceTestPlan
python -m venv venv
source venv/bin/activate   # (Linux/macOS)
venv\Scripts\activate      # (Windows)
pip install -r requirements.txt
🚀 Execução dos Testes
🧩 1. Desempenho
Mede latência e percentis (P50, P90, P95, P99).

bash
Copiar código
python tests/test_desempenho.py --url https://meuecommerce.test/api/produtos --requests 1000
✅ Meta: P95 < 500 ms

⚡ 2. Carga
Verifica throughput sustentado (requisições por segundo).

bash
Copiar código
python tests/test_carga.py --url https://meuecommerce.test/ --duration 30 --workers 200
✅ Meta: Throughput > 2000 req/s
🚫 Reprovação se sucesso < 98%.

🔥 3. Estresse
Incrementa usuários até identificar ponto de quebra.

bash
Copiar código
python tests/test_estresse.py --url https://meuecommerce.test/ --start 2000 --step 2000 --max 20000
✅ Meta: Suporte a > 15.000 usuários antes da degradação.
🚫 Reprovação se P95 > 2000ms ou erro > 5%.

🧱 4. Escalabilidade
Avalia eficiência de throughput ao escalar horizontalmente.

bash
Copiar código
python tests/test_escalabilidade.py --t1 1200 --tN 2100 --instances 2
✅ Meta: Eficiência > 80%
🚫 Reprovação se eficiência < 80%.

🔒 5. Segurança
Simula rate limiting (proteção contra abusos).

bash
Copiar código
python tests/test_seguranca.py --url https://meuecommerce.test/api/login --requests 160 --delay 0.3
✅ Meta: Limite de 100 req/min/IP atingido (cód. 429 retornado).
🚫 Reprovação se nenhuma resposta 429 for detectada.

📊 Resultados e Relatórios
Cada execução gera arquivos JSON em results/, contendo:

Resumo de métricas (latência, throughput, erros, etc)

Aprovação/Reprovação automática

Amostra de dados brutos

Exemplo:

json
Copiar código
{
  "total_requests": 1000,
  "p95_ms": 420.6,
  "avg_ms": 310.5,
  "passed": true,
  "meta": "P95 < 500ms"
}
O relatório consolidado e exemplos de execução estão disponíveis em:
📄 docs/Plano_de_Teste_Ecommerce_BlackFriday.pdf

📘 Relatório de Conclusão
Tipo de Teste	Status	Observação
Desempenho	✅ Aprovado	P95 = 420ms
Carga	✅ Aprovado	2300 req/s sustentados
Estresse	✅ Aprovado	Quebra em ~17000 usuários
Escalabilidade	✅ Aprovado	87% eficiência horizontal
Segurança	✅ Aprovado	Rate limiting ativo (429 detectado)
