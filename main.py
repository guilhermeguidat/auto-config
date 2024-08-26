import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import shutil
import winreg as reg
import time

import bitlocker
import instalarProgramas
import criarUsuarios
import tempo
import gpedit
import favoritos
import prints

# Caminhos
current_dir = os.path.dirname(os.path.abspath(__file__))
powershell_script_path = os.path.join(current_dir, 'script', 'EnableBitLocker.ps1')
bitlocker_info_path = r'C:\BitLockerRecoveryInfo.txt'

# Senhas de administrador disponíveis
admin_passwords = {
    "AR Própria": "ARcm@2050",
    "Outras": "ARcert1127"
}

def execute_tasks(nome_agr, nome_ar, senha_pc_admin, run_bitlocker, run_install, run_users, run_gpedit, run_time, run_capture):

    if run_install:
        instalarProgramas.install_programs()

    if run_users:
        usuario_agr = f"AGR-{nome_agr}"
        senha_agr = "AGR12345"
        senha_admin = senha_pc_admin
        criarUsuarios.criar_usuario(usuario_agr, senha_agr, "Usuarios")
        criarUsuarios.criar_usuario("PC_Admin", senha_admin, "Administradores")
        
    favoritos.copiar_favoritos(nome_ar)

    if run_gpedit:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        backup_folder = os.path.join(script_dir, 'GroupPolicyBackup')
        source_folder = r'C:\Windows\System32\GroupPolicy'

        if os.path.exists(backup_folder):
            print("Restaurando o backup de políticas de grupo...")
            if os.path.exists(source_folder):
                shutil.rmtree(source_folder)
            shutil.copytree(backup_folder, source_folder)
            print("Restauro completo.")
            subprocess.run(['gpupdate', '/force'], shell=True)
        else:
            print("Backup não encontrado. Não é possível restaurar.")

        chave = reg.HKEY_LOCAL_MACHINE
        subchave = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System'
        gpedit.alterar_registro(chave, subchave, 'DisableCAD', 1)

        secedit_config = """
        [Unicode]
        Unicode=yes
        [System Access]
        MinimumPasswordAge = 1
        MaximumPasswordAge = 30
        MinimumPasswordLength = 8
        PasswordComplexity = 1
        PasswordHistorySize = 0
        LockoutBadCount = 3
        ResetLockoutCount = 30
        LockoutDuration = 30
        [Event Audit]
        AuditSystemEvents = 3
        AuditLogonEvents = 3
        AuditObjectAccess = 3
        AuditPrivilegeUse = 3
        AuditPolicyChange = 3
        AuditAccountManage = 3
        AuditProcessTracking = 3
        AuditDSAccess = 3
        AuditAccountLogon = 3
        [Registry Values]
        MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\EnableLUA=4,0
        [Version]
        signature="$CHICAGO$"
        Revision=1
        """
        gpedit.aplicar_secedit(secedit_config)

    if run_bitlocker:
        bitlocker.execute_powershell_script(powershell_script_path)

        time.sleep(5)

        if not os.path.exists(bitlocker_info_path):
            print(f"Arquivo de recuperação do BitLocker não encontrado: {bitlocker_info_path}")
            return

        pdf_name = f"CHAVE_BITLOCKER_{nome_agr}_AR_{nome_ar}.pdf"
        pdf_path = os.path.join('C:', pdf_name)

        bitlocker.convert_txt_to_pdf(bitlocker_info_path, pdf_path)

        print(f"Arquivo PDF salvo em: {pdf_path}")

    if run_time:
        tempo.executar_configuracao_data_hora()
        time_server = "tic.syngularid.com.br"
        tempo.open_control_panel()
        tempo.configure_time_server(time_server)
    
    if run_capture:
        folder_name = f"PRINTS {nome_agr} {nome_ar}"
        messagebox.showinfo("Aviso", "O script irá tirar capturas de tela. Por favor, prepare-se.")
        prints.start_capture(
            folder_name,
            True,  # Capturar MAC Address
            True,  # Capturar Informações do Sistema
            True,  # Capturar Serial da Máquina
            True,  # Capturar Programas Instalados
            True   # Capturar Ativação do Windows
        )
    
    # Exibir mensagem de conclusão
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Concluído", "Todas as tarefas foram concluídas com sucesso!")
    root.destroy()
    
def main():
    def on_submit():
        nome_agr = nome_agr_entry.get()
        nome_ar = nome_ar_entry.get()
        senha_pc_admin = senha_pc_admin_var.get()
        run_bitlocker = bitlocker_var.get()
        run_install = install_var.get()
        run_users = users_var.get()
        run_gpedit = gpedit_var.get()
        run_time = time_var.get()
        run_capture = capture_var.get()
        window.destroy()
        execute_tasks(nome_agr, nome_ar, senha_pc_admin, run_bitlocker, run_install, run_users, run_gpedit, run_time, run_capture)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(current_dir, 'gear_icon.ico')

    window = tk.Tk()
    window.title("Configuração")
    window.geometry("490x330")  
    
    window.iconbitmap(icon_path)

    # Labels
    tk.Label(window, text="Nome do AGR:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
    tk.Label(window, text="Nome da AR:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
    tk.Label(window, text="Senha Administrador:").grid(row=2, column=0, padx=10, pady=10, sticky="e")

    # Entries
    nome_agr_entry = tk.Entry(window)
    nome_agr_entry.grid(row=0, column=1, padx=10, pady=10)

    nome_ar_entry = tk.Entry(window)
    nome_ar_entry.grid(row=1, column=1, padx=10, pady=10)

    # Radiobuttons
    senha_pc_admin_var = tk.StringVar(value="ARcm@2050")
    tk.Radiobutton(window, text="AR Própria", variable=senha_pc_admin_var, value="ARcm@2050").grid(row=2, column=1, padx=10, pady=5, sticky="w")
    tk.Radiobutton(window, text="Outras", variable=senha_pc_admin_var, value="ARcert1127").grid(row=2, column=1, padx=10, pady=5, sticky="e")

    # Checkbuttons
    bitlocker_var = tk.BooleanVar(value=True)
    install_var = tk.BooleanVar(value=True)
    users_var = tk.BooleanVar(value=True)
    gpedit_var = tk.BooleanVar(value=True)
    time_var = tk.BooleanVar(value=True)
    capture_var = tk.BooleanVar(value=True)

    tk.Checkbutton(window, text="BitLocker", variable=bitlocker_var).grid(row=3, column=0, padx=10, pady=5, sticky="w")
    tk.Checkbutton(window, text="Instalação de Drivers", variable=install_var).grid(row=3, column=1, padx=10, pady=5, sticky="w")
    tk.Checkbutton(window, text="Usuários", variable=users_var).grid(row=3, column=2, padx=10, pady=5, sticky="w")
    tk.Checkbutton(window, text="Gpedit", variable=gpedit_var).grid(row=4, column=0, padx=10, pady=5, sticky="w")
    tk.Checkbutton(window, text="Configurar Data e Hora", variable=time_var).grid(row=4, column=1, padx=10, pady=5, sticky="w")
    tk.Checkbutton(window, text="Capturas de Tela", variable=capture_var).grid(row=5, column=0, padx=10, pady=5, sticky="w")

    # Button
    execute_button = tk.Button(window, text="Executar", command=on_submit)
    execute_button.grid(row=6, column=0, columnspan=3, padx=10, pady=20)

    window.mainloop()

if __name__ == "__main__":
    main()
