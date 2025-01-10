# manager_ssh
Conexão via ssh com Netmiko e  ssh-pass


Estrutura do diretorio do projeto:

projeto/
│

├── comandos/                    # Pasta onde estarão os arquivos de comandos
│    ├── comando1.txt             # Exemplo de comando de configuração de dispositivos
│    ├── comando2.txt             # Outro arquivo de comandos, se necessário
│    └── ...                      # Outros arquivos de comandos conforme necessário
│
├─ log/                         # Pasta onde serão gerados os logs de execução
│    ├── sshpass/                 # Pasta específica para logs do sshpass
│    │   ├── ssh_executions.log  # Log principal para sshpass
│        │   └── ...                  # Outros logs relacionados ao sshpass
│        └── ...                      # Outros tipos de logs, se necessário
│
├── dispositivos.yaml            # Arquivo YAML com as configurações dos dispositivos (hosts, usernames, etc.)
│
└── connect_ssh.py                # O script Python com o código fornecido.
