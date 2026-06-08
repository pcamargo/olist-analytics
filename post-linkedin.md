🎓 Grateful, certified, and always learning!

I am thrilled to share that I have officially completed my postgraduate studies in Data Science & Analytics! 🚀

To bridge academic theory with real-world cloud scale, I decided to build a modern, end-to-end Data Lakehouse Platform on AWS using the Olist E-Commerce dataset. No manual clicks—everything is fully automated.

Here is a breakdown of the production-ready architecture I designed:

🛠️ Infrastructure as Code (IaC): 100% provisioned via Terraform, implementing strict IAM least-privilege security.
📦 Medallion Architecture (S3): Structured into Bronze (Raw CSVs), Silver (Cleaned Parquet), and Gold (Business Dimensions & Facts) layers.
🔥 Serverless Compute: Developed PySpark ETL jobs running on AWS Glue for schema enforcement, joins, and optimization.
📊 Cost Optimization & Analytics: Leveraged AWS Glue Crawlers and partition strategies (partitionBy Year/Month) to ensure lightning-fast, cost-effective queries via Amazon Athena.
🔄 GitOps & CI/CD: Built an automated GitHub Actions pipeline that validates Terraform syntax on every PR and syncs PySpark scripts directly to S3 upon merging to main.

This journey has been an incredible opportunity to deep dive into cloud architecture, scalable data engineering, and DevOps practices.

📂 Check out the full repository, documentation, and architecture diagrams here: [COLE_O_LINK_DO_SEU_GITHUB_AQUI]

A huge thank you to my professors, colleagues, and everyone who supported me throughout this academic milestone. On to the next challenge! 🎯

#DataEngineering #CloudArchitecture #AWS #Terraform #PySpark #GitHubActions #Postgraduate #ContinuousLearning #DevOps