import os
import subprocess
import logging
import yaml
from netmiko import ConnectHandler
from concurrent.futures import ThreadPoolExecutor

# Configuração de logging
class Logger:
    def __init__(self, log_dir="log", log_file="ssh_executions.log"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)  # Cria a pasta se não existir
        self.log_file = os.path.join(self.log_dir, log_file)

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(file_format)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger

# Classe para gerenciamento de dispositivos
class Dispositivo:
    def __init__(self, host, port, username, password, device_type):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.device_type = device_type

    def executar_comandos_ssh(self, comandos, arquivo_saida):
        comando_ssh = [
            "sshpass", "-p", self.password,
            "ssh", "-o", "StrictHostKeyChecking=no",
            "-p", str(self.port), "-T", f"{self.username}@{self.host}"
        ]
        with open(arquivo_saida, 'w') as f:
            process = subprocess.Popen(comando_ssh, stdin=subprocess.PIPE, stdout=f, stderr=subprocess.STDOUT)
            process.communicate(input=comandos.encode())
            process.wait()

    def executar_comandos_netmiko(self, comandos, arquivo_saida):
        dispositivo_netmiko = {
            "device_type": self.device_type,
            "host": self.host,
            "username": self.username,
            "password": self.password,
            "port": self.port,
        }
        try:
            with ConnectHandler(**dispositivo_netmiko) as conn:
                output = conn.send_config_set(comandos.splitlines())
                with open(arquivo_saida, 'w') as f:
                    f.write(output)
        except Exception as e:
            logger.error(f"Erro ao executar comandos no dispositivo {self.host}: {str(e)}")

# Classe para manipulação de arquivos YAML
class GerenciadorYAML:
    @staticmethod
    def carregar_dispositivos(arquivo_yaml):
        try:
            with open(arquivo_yaml, 'r') as f:
                data = yaml.safe_load(f)
            return [
                Dispositivo(
                    host=d.get('host'),
                    port=d.get('port', 22),
                    username=d.get('username'),
                    password=d.get('password'),
                    device_type=d.get('device_type', 'cisco_ios')
                ) for d in data.get('devices', [])
            ]
        except Exception as e:
            logger.error(f"Erro ao carregar o arquivo YAML {arquivo_yaml}: {str(e)}")
            return []

# Classe para gerenciamento de comandos
class GerenciadorComandos:
    @staticmethod
    def listar_arquivos(diretorio):
        return [os.path.join(diretorio, f) for f in os.listdir(diretorio) if f.endswith('.txt')]

    @staticmethod
    def escolher_arquivo(arquivos_comandos):
        if not arquivos_comandos:
            logger.error("Nenhum arquivo de comando encontrado.")
            print("Nenhum arquivo de comando encontrado.")
            return None

        print("Escolha o arquivo de comando:")
        for i, arquivo in enumerate(arquivos_comandos, 1):
            print(f"{i}. {os.path.basename(arquivo)}")

        while True:
            try:
                escolha = int(input("Digite o número do arquivo que você deseja usar: "))
                if 1 <= escolha <= len(arquivos_comandos):
                    return arquivos_comandos[escolha - 1]
                else:
                    print("Escolha inválida. Tente novamente.")
            except ValueError:
                print("Entrada inválida. Por favor, insira um número.")

# Funções auxiliares para gerar comandos
class GeradorComandos:
    @staticmethod
    def gerar_comandos_vlan_uplink(vlan_id, interface):
        return f"""
conf t
vlan {vlan_id}
!
interface {interface}
switchport trunk allowed vlan add {vlan_id}
end
copy r s
exit
"""

    @staticmethod
    def gerar_comandos_flow(nome_do_flow, vlan_internet, vlan_gerencia):
        return f"""
conf t
gpon profile flow {nome_do_flow}
add flow
{nome_do_flow}-1 encryption disable
{nome_do_flow}-1 flow-type pbmp 1
{nome_do_flow}-1 vlan {vlan_internet} service Internet
add flow
{nome_do_flow}-2 encryption disable
{nome_do_flow}-2 flow-type iphost 1
{nome_do_flow}-2 vlan {vlan_gerencia} service Gerencia
!
gpon profile vlan-translation {nome_do_flow}
add translation-type access {vlan_internet}
end
show gpon profile flow {nome_do_flow}
show gpon profile vlan-translation {nome_do_flow}
copy r s
exit
"""

    @staticmethod
    def remover_flow(nome_do_flow):
        return f"""
conf t
no gpon profile flow {nome_do_flow}
show gpon profile flow {nome_do_flow}
end
copy r s
exit
"""

# Classe de menu interativo
class MenuInterativo:
    def __init__(self, dispositivos):
        self.dispositivos = dispositivos

    def exibir_menu_principal(self):
        print("\nMenu Principal:")
        print("1. Configuração de Flow")
        print("2. Configuração de VLAN")
        print("3. Executar comandos via arquivo")
        print("4. Sair")

    def exibir_menu_flow(self):
        print("\nMenu de Configuração de Flow:")
        print("1. Criar Flow")
        print("2. Remover Flow")
        print("3. Voltar ao menu principal")

    def executar(self):
        while True:
            self.exibir_menu_principal()
            escolha_principal = input("Escolha uma opção: ")

            if escolha_principal == '1':
                # Submenu Configuração de Flow
                while True:
                    self.exibir_menu_flow()
                    escolha_flow = input("Escolha uma opção: ")
                    if escolha_flow == '1':
                        nome_do_flow = input("Digite o nome do flow: ")
                        vlan_internet = input("Digite a VLAN de Internet: ")
                        vlan_gerencia = input("Digite a VLAN de Gerência: ")
                        comandos = GeradorComandos.gerar_comandos_flow(nome_do_flow, vlan_internet, vlan_gerencia)
                        self.executar_comandos_dispositivos(comandos)
                    elif escolha_flow == '2':
                        nome_do_flow = input("Digite o nome do flow a ser removido: ")
                        comandos = GeradorComandos.remover_flow(nome_do_flow)
                        self.executar_comandos_dispositivos(comandos)
                    elif escolha_flow == '3':
                        break
                    else:
                        print("Opção inválida. Tente novamente.")

            elif escolha_principal == '2':
                vlan_id = input("Digite o ID da VLAN: ")
                interface = input("Digite a interface: ")
                comandos = GeradorComandos.gerar_comandos_vlan_uplink(vlan_id, interface)
                self.executar_comandos_dispositivos(comandos)

            elif escolha_principal == '3':
                arquivos_comandos = GerenciadorComandos.listar_arquivos("comandos")
                arquivo_comandos_escolhido = GerenciadorComandos.escolher_arquivo(arquivos_comandos)
                if arquivo_comandos_escolhido:
                    with open(arquivo_comandos_escolhido, 'r') as f:
                        comandos = f.read()
                    self.executar_comandos_dispositivos(comandos)

            elif escolha_principal == '4':
                print("Saindo...")
                break

            else:
                print("Opção inválida. Tente novamente.")

    def executar_comandos_dispositivos(self, comandos):
        def processar_dispositivo(dispositivo):
            arquivo_saida = os.path.join("log", f"saida_{dispositivo.host}_{dispositivo.port}.log")
            if dispositivo.device_type == 'ssh':
                logger.info(f"Executando comandos via sshpass em {dispositivo.host}.")
                dispositivo.executar_comandos_ssh(comandos, arquivo_saida)
            else:
                logger.info(f"Executando comandos via Netmiko em {dispositivo.host}.")
                dispositivo.executar_comandos_netmiko(comandos, arquivo_saida)

        with ThreadPoolExecutor() as executor:
            executor.map(processar_dispositivo, self.dispositivos)

# Inicialização
logger = Logger().get_logger()
arquivo_yaml = "dispositivos.yaml"
dispositivos = GerenciadorYAML.carregar_dispositivos(arquivo_yaml)

if dispositivos:
    menu = MenuInterativo(dispositivos)
    menu.executar()
else:
    logger.error("Nenhum dispositivo encontrado.")
    print("Nenhum dispositivo encontrado.")
