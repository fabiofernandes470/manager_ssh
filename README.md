# manager_ssh
Conexão via ssh com Netmiko e  ssh-pass


Estrutura do diretorio do projeto:

projeto/

│
├ comandos/                     # Pasta onde estarão os arquivos de comandos

│    ├── comando1.txt             # Exemplo de comando de configuração de dispositivos

│    ├── comando2.txt             # Outro arquivo de comandos, se necessário

│    └── ...                      # Outros arquivos de comandos conforme necessário
│
├ log/                           # Pasta onde serão gerados os logs de execução

│    ├── sshpass/                 # Pasta específica para logs do sshpass

│    │   ├── ssh_executions.log   # Log principal para sshpass

│        │   └── ...              # Outros logs relacionados ao sshpass

│        └── ...                  # Outros tipos de logs, se necessário

│
├ dispositivos.yaml             # Arquivo YAML com as configurações dos dispositivos (hosts, usernames, etc.)

│
└ connect_ssh.py                # O script Python com o código fornecido.


Explicação da Estrutura:

comandos/:

Esta pasta contém arquivos de texto (.txt) com os comandos que você deseja executar. O código irá ler esses arquivos para usar os comandos de configuração conforme selecionado.
Exemplo de comandos em arquivos .txt: comando1.txt, comando2.txt, etc.
Você pode adicionar quantos arquivos de comando precisar.
log/sshpass/:

A pasta log/ será usada para armazenar os logs de execução. Dentro dessa pasta, a subpasta sshpass/ é onde os logs específicos de execução com sshpass serão gravados.
O arquivo de log ssh_executions.log armazenará as informações sobre as execuções feitas via sshpass, como erros, informações de execução, etc.
dispositivos.yaml:

Este arquivo YAML contém a lista de dispositivos para os quais o script se conectará. Ele deve ter uma estrutura como a seguinte (exemplo básico):

devices:
  - host: "192.168.1.1"
    port: 22
    device_type: "ssh"
    username: "admin"
    password: "senha123"
  - host: "192.168.1.2"
    port: 22
    device_type: "cisco_ios"
    username: "admin"
    password: "senha123

