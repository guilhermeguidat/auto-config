import subprocess 
from fpdf import FPDF  

def execute_powershell_script(script_path):
    activate_ps_script = 'Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force'
    command = ['powershell.exe', '-Command', f"{activate_ps_script}; . '{script_path}'"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print("Script PowerShell executado com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o script PowerShell:\n{e.stderr}")

def convert_txt_to_pdf(txt_path, pdf_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    with open(txt_path, 'r') as file:
        for line in file:
            pdf.cell(200, 10, txt=line.strip(), ln=True)
    pdf.output(pdf_path)