import subprocess
import winreg as reg

def alterar_registro(chave, subchave, valor_nome, valor, tipo=reg.REG_DWORD):
    try:
        chave_reg = reg.OpenKey(chave, subchave, 0, reg.KEY_SET_VALUE)
    except FileNotFoundError:
        chave_reg = reg.CreateKey(chave, subchave)
    try:
        reg.SetValueEx(chave_reg, valor_nome, 0, tipo, valor)
        reg.CloseKey(chave_reg)
        print(f"{valor_nome} configurado para {valor} em {subchave}.")
    except WindowsError as e:
        print(f"Erro ao alterar o registro:\n{e}")

def aplicar_secedit(config):
    try:
        with open('secedit.inf', 'w') as file:
            file.write(config)
        subprocess.run(['secedit', '/configure', '/db', 'secedit.sdb', '/cfg', 'secedit.inf'], check=True)
        print("Configurações de segurança aplicadas com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao aplicar configurações de segurança:\n{e}")
