import csv
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

from classes_04 import (
    DatabaseManager, Tecnico, Equipamento, Medicao,
    TecnicoDAO, EquipamentoDAO, MedicaoDAO
)

def importar_planilha_csv(caminho_csv, db):
    """Lê o CSV bruto da Schulz, aplica regras de higienização e grava no SQLite."""
    tecnico_dao = TecnicoDAO(db)
    equipamento_dao = EquipamentoDAO(db)
    medicao_dao = MedicaoDAO(db)
    
    tags_processadas = set()
    linhas_importadas = 0
    erros = []

    if not os.path.exists(caminho_csv):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_csv}")

    with open(caminho_csv, mode="r", encoding="utf-8-sig") as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=";")
        
        for num_linha, row in enumerate(leitor, start=2):
            try:
                # 1. Validações e higienização na criação dos objetos
                tec = Tecnico(nome=row["nome_tecnico"], matricula=row["matricula"])
                tec_salvo = tecnico_dao.inserir(tec)

                eq = Equipamento(codigo_tag=row["codigo_tag"], denominacao=row["denominacao"])
                eq_salvo = equipamento_dao.inserir(eq)

                med = Medicao(
                    id_tecnico=tec_salvo.id_tecnico,
                    id_equipamento=eq_salvo.id_equipamento,
                    measurement_plan=row["measurement_plan"],
                    part_number=row["part_number"],
                    nome_caracteristica=row["nome_caracteristica"],
                    data_medicao=row["data_medicao"],
                    hora_medicao=row["hora_medicao"],
                    valor_nominal=row["valor_nominal"],
                    tolerancia_superior=row["tolerancia_superior"],
                    tolerancia_inferior=row["tolerancia_inferior"],
                    medicao_1=row["medicao_1"],
                    medicao_2=row["medicao_2"]
                )
                medicao_dao.inserir(med)
                
                tags_processadas.add(eq_salvo.codigo_tag)
                linhas_importadas += 1

            except Exception as e:
                erros.append(f"Linha {num_linha}: {e}")

    return linhas_importadas, sorted(list(tags_processadas)), erros
def gerar_texto_certificado(codigo_tag, db):
    """Consulta o banco com JOIN e monta o certificado consolidado do equipamento."""
    medicao_dao = MedicaoDAO(db)
    registros = medicao_dao.relatorio_por_tag(codigo_tag)

    if not registros:
        return f"Nenhum ensaio encontrado para a TAG: {codigo_tag}"

    primeiro = registros[0]
    linhas = []
    linhas.append("=" * 75)
    linhas.append("          SCHULZ S.A. - CERTIFICADO DE CALIBRAÇÃO METROLÓGICA          ")
    linhas.append("=" * 75)
    linhas.append(f"Equipamento : {primeiro['denominacao']} (TAG: {primeiro['codigo_tag']})")
    linhas.append(f"Metrologista: {primeiro['nome_metrologista']} (Matrícula: {primeiro['matricula']})")
    linhas.append(f"Data Emissão: {primeiro['data_medicao']}")
    linhas.append("-" * 75)
    linhas.append("RESULTADOS DOS ENSAIOS:")

    todos_aprovados = True

    for reg in registros:
        status = reg["status_aprovacao"]
        if status == "REPROVADO":
            todos_aprovados = False

        linhas.append(
            f" • [{reg['part_number']}] {reg['nome_caracteristica']}: "
            f"Média {reg['media_calculada']} mm | "
            f"Faixa [{reg['tolerancia_inferior']} a {reg['tolerancia_superior']}] -> {status}"
        )

    linhas.append("-" * 75)
    parecer_final = "APROVADO PARA USO" if todos_aprovados else "REPROVADO (BLOQUEADO PARA CALIBRAÇÃO)"
    linhas.append(f"PARECER TÉCNICO FINAL: {parecer_final}")
    linhas.append("=" * 75)

    return "\n".join(linhas)
class AppMetrologiaSchulz:
    def __init__(self, root):
        self.root = root
        self.root.title("Schulz S.A. - Sistema de Calibração Metrológica (MVP)")
        self.root.geometry("760x540")
        self.root.configure(bg="#f0f4f8")

        # Garante que o banco seja criado na mesma pasta do programa/executável
        # Garante que o banco seja criado na mesma pasta do .exe (ou do .py no VS Code)
        if getattr(sys, 'frozen', False):
            pasta_base = os.path.dirname(sys.executable)
        else:
            pasta_base = os.path.dirname(os.path.abspath(__file__))
            
        self.caminho_db = os.path.join(pasta_base, "metrologia_schulz.db")
        self.db = DatabaseManager(db_name=self.caminho_db)
        self.db.inicializar_banco()

        self.montar_interface()

    def montar_interface(self):
        # Cabeçalho
        frame_topo = tk.Frame(self.root, bg="#003366", pady=12)
        frame_topo.pack(fill="x")
        
        lbl_titulo = tk.Label(
            frame_topo, text="SCHULZ S.A. - LABORATÓRIO DE METROLOGIA",
            font=("Arial", 14, "bold"), fg="white", bg="#003366"
        )
        lbl_titulo.pack()

        lbl_sub = tk.Label(
            frame_topo, text="Importação Automatizada de Medições e Emissão de Certificados",
            font=("Arial", 10), fg="#d0e1f9", bg="#003366"
        )
        lbl_sub.pack()

        # Área de Botões
        frame_botoes = tk.Frame(self.root, bg="#f0f4f8", pady=15)
        frame_botoes.pack()

        btn_importar = tk.Button(
            frame_botoes, text="📂 1. Importar Planilha (.CSV)",
            font=("Arial", 10, "bold"), bg="#0066cc", fg="white",
            padx=15, pady=8, cursor="hand2", command=self.acao_importar
        )
        btn_importar.grid(row=0, column=0, padx=10)

        btn_salvar = tk.Button(
            frame_botoes, text="💾 2. Exportar Certificados (.TXT)",
            font=("Arial", 10, "bold"), bg="#2e7d32", fg="white",
            padx=15, pady=8, cursor="hand2", command=self.acao_exportar_txt
        )
        btn_salvar.grid(row=0, column=1, padx=10)

        # Área de Exibição dos Certificados
        self.area_texto = scrolledtext.ScrolledText(
            self.root, width=88, height=22, font=("Consolas", 10), bg="white", fg="#111111"
        )
        self.area_texto.pack(padx=15, pady=5)
        self.area_texto.insert("1.0", "Aguardando importação da planilha CSV da máquina de medição...\n")

    def acao_importar(self):
        caminho_csv = filedialog.askopenfilename(
            title="Selecione a planilha de medições da Schulz",
            filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
        )
        if not caminho_csv:
            return

        try:
            qtd, tags, erros = importar_planilha_csv(caminho_csv, self.db)
            self.area_texto.delete("1.0", tk.END)

            if erros:
                self.area_texto.insert(tk.END, "⚠️ AVISOS DURANTE A IMPORTAÇÃO:\n" + "\n".join(erros) + "\n\n")

            if not tags:
                self.area_texto.insert(tk.END, "Nenhum dado válido foi importado.")
                return

            for tag in tags:
                certificado = gerar_texto_certificado(tag, self.db)
                self.area_texto.insert(tk.END, certificado + "\n\n")

            messagebox.showinfo("Sucesso", f"Importação concluída!\n{qtd} medições processadas.")

        except Exception as e:
            messagebox.showerror("Erro na Importação", f"Falha ao ler arquivo:\n{e}")

    def acao_exportar_txt(self):
        conteudo = self.area_texto.get("1.0", tk.END).strip()
        if not conteudo or "Aguardando importação" in conteudo:
            messagebox.showwarning("Aviso", "Importe uma planilha primeiro para gerar os certificados.")
            return

        caminho_saida = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile="Certificados_Calibracao_Schulz.txt",
            filetypes=[("Arquivo de Texto", "*.txt")]
        )
        if caminho_saida:
            with open(caminho_saida, "w", encoding="utf-8") as f:
                f.write(conteudo)
            messagebox.showinfo("Exportado", "Certificados salvos com sucesso!")


if __name__ == "__main__":
    janela = tk.Tk()
    app = AppMetrologiaSchulz(janela)
    janela.mainloop()




