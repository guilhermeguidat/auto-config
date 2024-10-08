import os  
import subprocess  

def install_program(executable, silent_args):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        drivers_dir = os.path.join(script_dir, 'drivers')
        executable_path = os.path.join(drivers_dir, executable)
        if not os.path.isfile(executable_path):
            print(f"Erro: {executable_path} não encontrado.")
            return
        print(f"Iniciando a instalação de {executable}...")
        subprocess.run([executable_path] + silent_args, check=True)
        print(f"{executable} instalado com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Falha na instalação de {executable}:\n{e}")
        
def install_programs():
    programs = {
        "AWP.exe": ["/silent"],
        "ePass2003-Setup_170623.exe": ["/silent"],
        "ExtensionModule.exe": ["/S"],
        "ftrDriverSetup_win8_whql_3471.exe": ["/quiet", "/norestart"],
        "GDsetupStarsignCUTx64.exe": ["/s"],
        "sac_iti.exe": ["/silent"],
        "SafeSignIC30124-x64-win-tu-user64.exe": ["/quiet"]
    }
    for executable, args in programs.items():
        install_program(executable, args)