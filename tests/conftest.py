import sys
from unittest.mock import MagicMock

# 1. Cria uma classe customizada para simular um pacote com sub-atributos
class MockPackage(MagicMock):
    def __repr__(self):
        return f"<MockPackage {self._mock_name}>"

# 2. Instancia os mocks para o pacote principal e os sub-módulos
awsglue_mock = MockPackage(name='awsglue')
transforms_mock = MockPackage(name='awsglue.transforms')
utils_mock = MockPackage(name='awsglue.utils')
context_mock = MockPackage(name='awsglue.context')
job_mock = MockPackage(name='awsglue.job')

# Mapeia os sub-módulos dentro do mock principal para o Python não reclamar de pacotes
awsglue_mock.transforms = transforms_mock
awsglue_mock.utils = utils_mock
awsglue_mock.context = context_mock
awsglue_mock.job = job_mock

# 3. Injeta tudo no cache de módulos do sistema do Python (sys.modules)
sys.modules['awsglue'] = awsglue_mock
sys.modules['awsglue.transforms'] = transforms_mock
sys.modules['awsglue.utils'] = utils_mock
sys.modules['awsglue.context'] = context_mock
sys.modules['awsglue.job'] = job_mock

# 4. Define o retorno padrão para a função getResolvedOptions da AWS
utils_mock.getResolvedOptions = MagicMock(
    return_value={'JOB_NAME': 'test_job', 'DATA_LAKE_BUCKET': 'test_bucket'}
)