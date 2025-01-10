import os
import subprocess
import logging
import yaml
from netmiko import ConnectHandler

# Configuração de logging
log_dir = "log/sshpass"
os.makedirs(log_dir, exist_ok=True)  # Cria a pasta se não existir
log_file = os.path.join(log_dir, "ssh_executions.log")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)
file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_format)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(file_format)
logger.addHandler(console_handler)

# Função para executar comandos via sshpass
def executar_comandos_ssh(ip, porta, usuario, senha, comandos, arquivo_saida):
    """Executa comandos em um dispositivo remoto via SSH usando sshpass."""
    comando_ssh = f"sshpass -p '{senha}' ssh -o StrictHostKeyChecking=no -p {porta} -T {usuario}@{ip}"
    with open(arquivo_saida, 'w') as f:
        process = subprocess.Popen(comando_ssh, shell=True, stdin=subprocess.PIPE, stdout=f, stderr=subprocess.STDOUT)
        process.communicate(input=comandos.encode())
        process.wait()

# Função para executar comandos via Netmiko
def executar_comandos_netmiko(dispositivo, comandos, arquivo_saida):
    """Executa comandos em um dispositivo remoto via Netmiko."""
    try:
        with ConnectHandler(**dispositivo) as conn:
            output = conn.send_config_set(comandos.splitlines())
            with open(arquivo_saida, 'w') as f:
                f.write(output)
    except Exception as e:
        logger.error(f"Erro ao executar comandos no dispositivo {dispositivo['host']}: {str(e)}")
        print(f"Erro ao executar comandos no dispositivo {dispositivo['host']}: {str(e)}")

# Função para carregar dispositivos do arquivo YAML
def carregar_dispositivos_yaml(arquivo_yaml):
    try:
        with open(arquivo_yaml, 'r') as f:
            data = yaml.safe_load(f)
        return data.get('devices', [])
    except Exception as e:
        logger.error(f"Erro ao carregar o arquivo YAML {arquivo_yaml}: {str(e)}")
        return []

# Função para listar arquivos de comandos
def listar_arquivos_comandos(diretorio):
    return [os.path.join(diretorio, f) for f in os.listdir(diretorio) if f.endswith('.txt')]

# Função para gerar comandos de VLAN para o uplink
def gerar_comandos_vlan_uplink(vlan_id, interface):
    """Gera comandos para configurar a VLAN no uplink da OLT."""
    comandos = f"""
conf t
vlan database
vlan {vlan_id}
!
interface {interface}
switchport trunk allowed vlan add {vlan_id}
end
copy r s
exit
"""
    return comandos

# Função para gerar comandos predefinidos para o perfil de flow
def gerar_comandos_flow(nome_do_flow, vlan_internet, vlan_gerencia):
    """Gera comandos para configurar o perfil de flow na OLT."""
    comandos = f"""
conf t
gpon profile flow {nome_do_flow}
add flow
{nome_do_flow}-1 encription disable
{nome_do_flow}-1 flow-type pbmp 1
{nome_do_flow}-1 vlan {vlan_internet} service Internet
add flow
{nome_do_flow}-2 encription disable
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
    return comandos

# Função para escolher um arquivo de comandos
def escolher_arquivo_comando(arquivos_comandos):
    """Permite ao usuário escolher um arquivo de comandos disponível."""
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

# Configurações principais
arquivo_yaml = "dispositivos.yaml"
diretorio_comandos = "comandos"  # Diretório onde os arquivos de comandos estão localizados

# Carregar dispositivos do arquivo YAML
dispositivos = carregar_dispositivos_yaml(arquivo_yaml)

if not dispositivos:
    logger.error(f"Nenhum dispositivo encontrado no arquivo YAML {arquivo_yaml}.")
    print(f"Nenhum dispositivo encontrado no arquivo YAML.")
else:
    arquivos_comandos = listar_arquivos_comandos(diretorio_comandos)
    comando_pronto = input("Deseja usar comandos predefinidos no script? (s/n): ").lower() == 's'
    
    if comando_pronto:
        # Gerar comandos predefinidos
        escolha_comando = input("Escolha o comando a ser gerado: \n1. Configurar Flow na OLT\n2. Configurar VLAN no uplink\nDigite o número: ")
        
        if escolha_comando == '1':
            nome_do_flow = input("Digite o nome do flow: ")
            vlan_internet = input("Digite a VLAN de Internet: ")
            vlan_gerencia = input("Digite a VLAN de Gerência: ")
            comandos = gerar_comandos_flow(nome_do_flow, vlan_internet, vlan_gerencia)
        elif escolha_comando == '2':
            vlan_id = input("Digite o ID da VLAN: ")
            interface = input("Digite a interface (ex: 10giga-ethernet0/1): ")
            comandos = gerar_comandos_vlan_uplink(vlan_id, interface)
        else:
            print("Opção inválida.")
            comandos = ""
    else:
        # Selecionar arquivo de comandos
        arquivo_comandos_escolhido = escolher_arquivo_comando(arquivos_comandos)
        if arquivo_comandos_escolhido:
            with open(arquivo_comandos_escolhido, 'r') as f:
                comandos = f.read()

    # Executar comandos nos dispositivos
    for dispositivo in dispositivos:
        ip = dispositivo.get('host')
        porta = dispositivo.get('port', 22)
        tipo = dispositivo.get('device_type')
        usuario = dispositivo.get('username')
        senha = dispositivo.get('password')

        arquivo_saida = os.path.join(log_dir, f"saida_{ip}_{porta}.log")

        if tipo == "ssh":
            logger.info(f"Executando comandos via sshpass em {ip}.")
            executar_comandos_ssh(ip, porta, usuario, senha, comandos, arquivo_saida)
        else:
            logger.info(f"Executando comandos via Netmiko em {ip}.")
            dispositivo_netmiko = {
                "device_type": tipo,
                "host": ip,
                "username": usuario,
                "password": senha,
                "port": porta,
            }
            executar_comandos_netmiko(dispositivo_netmiko, comandos, arquivo_saida)
