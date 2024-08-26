import os
import shutil

def obter_diretorio_executavel():
    return os.path.dirname(os.path.abspath(__file__))

def copiar_favoritos(nome_ar):
    pasta_fav = "favoritos"  # Diretório onde os arquivos HTML estão localizados
    arquivo_padrao = "PADRÃO.html"
    
    # Obtém o diretório onde o script está sendo executado
    diretorio_script = obter_diretorio_executavel()
    caminho_pasta_fav = os.path.join(diretorio_script, pasta_fav)
    
    # Verifica se a pasta FAV existe
    if not os.path.exists(caminho_pasta_fav):
        print(f"Pasta {caminho_pasta_fav} não encontrada.")
        return

    # Procura pelo arquivo correspondente ao nome da AR
    arquivo_favoritos = None
    for arquivo in os.listdir(caminho_pasta_fav):
        if arquivo.lower() == f"{nome_ar.lower()}.html":
            arquivo_favoritos = arquivo
            break

    # Define o arquivo a ser copiado (correspondente ou padrão)
    if arquivo_favoritos:
        arquivo_origem = os.path.join(caminho_pasta_fav, arquivo_favoritos)
    else:
        arquivo_origem = os.path.join(caminho_pasta_fav, arquivo_padrao)

    # Define o caminho da pasta do script
    pasta_script = diretorio_script
    arquivo_favoritos_script = os.path.join(pasta_script, "favoritos.html")

    # Verifica se o arquivo de origem existe antes de tentar copiar
    if not os.path.isfile(arquivo_origem):
        print(f"Arquivo de origem '{arquivo_origem}' não encontrado.")
        return

    try:
        # Copia o arquivo para a pasta do script
        shutil.copy(arquivo_origem, arquivo_favoritos_script)
        print(f"Arquivo '{arquivo_origem}' copiado para '{arquivo_favoritos_script}' com sucesso.")
        
        # Define o caminho da pasta de destino no disco C:
        pasta_destino = os.path.join('C:\\')
        os.makedirs(pasta_destino, exist_ok=True)
        arquivo_destino = os.path.join(pasta_destino, "favoritos.html")
        
        # Copia o arquivo da pasta do script para o disco C:
        shutil.copy(arquivo_favoritos_script, arquivo_destino)
        print(f"Arquivo '{arquivo_favoritos_script}' copiado para '{arquivo_destino}' com sucesso.")
        
    except PermissionError as e:
        print(f"Erro de permissão ao copiar o arquivo: {e}. Tente executar o programa como administrador.")
    except Exception as e:
        print(f"Erro ao copiar o arquivo: {e}")