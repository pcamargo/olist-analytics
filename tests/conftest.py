import sys
from unittest.mock import MagicMock

# 1. Cria submódulos fantasmas para o pacote awsglue
awsglue_mock = MagicMock()
awsglue_utils_mock = MagicMock()
awsglue_context_mock = MagicMock()
awsglue_job_mock = MagicMock()

# 2. Injeta os mocks no dicionário de módulos globais do Python
sys.modules['awsglue'] = awsglue_mock
sys.modules['awsglue.utils'] = awsglue_utils_mock
sys.modules['awsglue.context'] = awsglue_context_mock
sys.modules['awsglue.job'] = awsglue_job_mock

# 3. Define o comportamento esperado para a função getResolvedOptions
# Isso evita que o script quebre ao tentar ler argumentos que não existem no teste
awsglue_utils_mock.getResolvedOptions = MagicMock(return_value={'JOB_NAME': 'test_job', 'DATA_LAKE_BUCKET': 'test_bucket'})
