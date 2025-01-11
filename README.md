# Automação de Configuração de Dispositivos de Rede

## Descrição

Este script em Python é uma ferramenta automatizada para gerenciar dispositivos de rede, executar comandos de configuração e registrar as saídas de execução. A aplicação pode ser configurada para trabalhar com dispositivos via SSH ou utilizando o Netmiko, um módulo para automação de rede. O sistema também suporta a execução de comandos a partir de arquivos YAML ou arquivos de texto. Ele oferece uma interface de menu interativo para facilitar a escolha de comandos e dispositivos.

## Funcionalidades

- **Execução de comandos via SSH**: Conecte-se aos dispositivos e execute comandos através do `sshpass` e `ssh`.
- **Execução de comandos via Netmiko**: Utiliza o Netmiko para configurar dispositivos de rede de forma programática.
- **Gerenciamento de dispositivos**: Carregue os dispositivos a partir de um arquivo YAML.
- **Registro de log**: As saídas das execuções são registradas em arquivos de log.
- **Menu interativo**: Oferece um menu para escolher as configurações de VLAN, Flow, ou executar comandos via arquivo.
- **Execução em múltiplos dispositivos simultaneamente**: Utiliza `ThreadPoolExecutor` para executar comandos em vários dispositivos ao mesmo tempo.

## Estrutura do Projeto

```text
├── comandos
│   └── arquivo_comandos.txt         # Arquivos de comandos em texto
├── dispositivos.yaml               # Arquivo YAML com a configuração dos dispositivos
├── log                             # Diretório de logs
│   └── ssh_executions.log          # Arquivo de log das execuções SSH
└── script.py                       # O script principal
          # O script principal

Requisitos
Python 3.6 ou superior
Pacotes necessários:
netmiko
pyyaml
sshpass
Você pode instalar as dependências necessárias usando o seguinte comando:

bash
Copiar código
pip install netmiko pyyaml
Como Usar
Configuração dos Dispositivos: Crie um arquivo dispositivos.yaml com a configuração dos dispositivos que você deseja gerenciar. Exemplo de formato:

yaml
Copiar código
devices:
  - host: 192.168.1.1
    port: 22
    username: admin
    password: senha
    device_type: cisco_ios
  - host: 192.168.1.2
    port: 22
    username: admin
    password: senha
    device_type: cisco_ios
Executando o Script: Após configurar o arquivo YAML, execute o script com o seguinte comando:

bash
Copiar código
python script.py
Menu Interativo: O script oferece um menu interativo que permite realizar as seguintes ações:

Configurar Flow (Criar ou Remover Flow)
Configurar VLAN
Executar comandos a partir de arquivos de texto
Arquivos de Comandos: Você pode criar arquivos de texto com os comandos que deseja executar e colocá-los no diretório comandos. O menu permitirá selecionar e executar esses arquivos nos dispositivos configurados.

Visualizando Logs: Todos os comandos executados são registrados no diretório log. A saída de cada execução pode ser visualizada nos arquivos de log gerados.

Contribuições
Sinta-se à vontade para fazer contribuições ao projeto, incluindo melhorias e correções de bugs.
