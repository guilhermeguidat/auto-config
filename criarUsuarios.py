import subprocess

def criar_usuario(usuario, senha, grupo):
    try:
        subprocess.run(['net', 'user', usuario, senha, '/add'], check=True)
        subprocess.run(['net', 'localgroup', grupo, usuario, '/add'], check=True)
        print(f"Usuário {usuario} criado e adicionado ao grupo {grupo}.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao criar o usuário {usuario}:\n{e}")