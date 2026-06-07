## O Padrão Ouro: Olist E-Commerce Dataset

Este é um dataset real de mais de 100 mil pedidos de marketplaces brasileiros (de 2016 a 2018), mas totalmente anonimizado.

Por que é excelente? Ele não é um arquivo único; ele é composto por várias tabelas relacionais (clientes, pedidos, itens, produtos, pagamentos, avaliações e geolocalização).

O Desafio de Engenharia: Ideal para simular um cenário de negócio real. Você precisará criar um pipeline que ingira essas diferentes tabelas no S3, faça o particionamento correto e use o AWS Glue/Athena para criar JOINS complexos na camada Silver/Gold para responder a perguntas como: "Qual o tempo médio de entrega por estado?" ou "Quais categorias de produtos geram mais receita?".

## 🛠️ Como estruturar isso no GitHub?
Independentemente do dataset que escolher, documente o fluxo dos dados no seu repositório. O design ideal da sua arquitetura deve seguir este fluxo visual de dados:

Camada Bronze (Raw): Os arquivos originais do dataset (em CSV ou JSON) dropados diretamente via script de ingestão no primeiro bucket S3.

Camada Silver (Trusted): Seu job do AWS Glue limpa os dados, remove duplicatas, trata valores nulos e converte os arquivos para Parquet (comprimido e colunar).

Camada Gold (Refined): Onde os dados são agregados e modelados para o negócio (tabelas de fatos e dimensões), prontos para serem consumidos pelo Amazon Athena.

