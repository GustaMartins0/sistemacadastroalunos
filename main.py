import os
import sys
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ...configurações iniciais...
APP_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
PRINCIPAL_CSV = os.path.join(APP_DIR, "alunos.csv")
RELATORIO_CSV = os.path.join(APP_DIR, "relatorio_filtrado.csv")

COLUMNS = ["Nome", "Idade", "Curso", "Nota Final"]

class SistemaAlunos:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Cadastro e Relatórios de Alunos")
        self.df = pd.DataFrame(columns=COLUMNS)
        self._criar_widgets()
        self.carregar_csv(auto=True)

    def _criar_widgets(self):
        # Frame de cadastro
        frm_top = ttk.Frame(self.root, padding=10)
        frm_top.pack(fill="x")

        ttk.Label(frm_top, text="Nome:").grid(row=0, column=0, sticky="w")
        self.entry_nome = ttk.Entry(frm_top, width=30)
        self.entry_nome.grid(row=0, column=1, padx=5)

        ttk.Label(frm_top, text="Idade:").grid(row=0, column=2, sticky="w")
        self.entry_idade = ttk.Entry(frm_top, width=8)
        self.entry_idade.grid(row=0, column=3, padx=5)

        ttk.Label(frm_top, text="Curso:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_curso = ttk.Entry(frm_top, width=30)
        self.entry_curso.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frm_top, text="Nota Final:").grid(row=1, column=2, sticky="w", pady=5)
        self.entry_nota = ttk.Entry(frm_top, width=8)
        self.entry_nota.grid(row=1, column=3, padx=5, pady=5)

        btn_cadastrar = ttk.Button(frm_top, text="Cadastrar", command=self.cadastrar_aluno)
        btn_cadastrar.grid(row=0, column=4, rowspan=2, padx=10)

        # Frame de filtros e ações
        frm_mid = ttk.Frame(self.root, padding=10)
        frm_mid.pack(fill="x")

        ttk.Label(frm_mid, text="Filtrar nota >").grid(row=0, column=0, sticky="w")
        self.entry_filtro = ttk.Entry(frm_mid, width=10)
        self.entry_filtro.grid(row=0, column=1, padx=5)
        btn_filtrar = ttk.Button(frm_mid, text="Filtrar", command=self.filtrar_alunos)
        btn_filtrar.grid(row=0, column=2, padx=5)
        btn_mostrar_todos = ttk.Button(frm_mid, text="Mostrar Todos", command=self.atualizar_tabela)
        btn_mostrar_todos.grid(row=0, column=3, padx=5)

        btn_exportar = ttk.Button(frm_mid, text="Exportar relatório filtrado", command=self.exportar_relatorio_filtrado)
        btn_exportar.grid(row=0, column=4, padx=10)

        btn_salvar = ttk.Button(frm_mid, text="Salvar CSV", command=self.salvar_csv)
        btn_salvar.grid(row=0, column=5, padx=5)
        btn_carregar = ttk.Button(frm_mid, text="Carregar CSV", command=self.carregar_csv_dialog)
        btn_carregar.grid(row=0, column=6, padx=5)

        # Frame tabela
        frm_table = ttk.Frame(self.root, padding=10)
        frm_table.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(frm_table, columns=COLUMNS, show="headings")
        for col in COLUMNS:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        vsb = ttk.Scrollbar(frm_table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

    # Função para cadastrar novo aluno
    def cadastrar_aluno(self):
        nome = self.entry_nome.get().strip()
        idade_str = self.entry_idade.get().strip()
        curso = self.entry_curso.get().strip()
        nota_str = self.entry_nota.get().strip()

        if not nome:
            messagebox.showerror("Erro", "Nome é obrigatório.")
            return

        try:
            idade = int(idade_str)
        except ValueError:
            messagebox.showerror("Erro", "Idade deve ser um número inteiro.")
            return

        try:
            nota = float(nota_str)
        except ValueError:
            messagebox.showerror("Erro", "Nota Final deve ser um número (ex: 8.5).")
            return

        novo = {"Nome": nome, "Idade": idade, "Curso": curso, "Nota Final": nota}
        self.df = pd.concat([self.df, pd.DataFrame([novo])], ignore_index=True)
        self.atualizar_tabela()
        self.salvar_csv(auto=True)
        messagebox.showinfo("Sucesso", "Aluno cadastrado com sucesso.")
        # limpa campos
        self.entry_nome.delete(0, tk.END)
        self.entry_idade.delete(0, tk.END)
        self.entry_curso.delete(0, tk.END)
        self.entry_nota.delete(0, tk.END)

    # Atualiza a Treeview com os dados do DataFrame (ou DataFrame passado)
    def atualizar_tabela(self, df_view=None):
        df_show = self.df if df_view is None else df_view
        # limpa tree
        for row in self.tree.get_children():
            self.tree.delete(row)
        # insere linhas
        for _, row in df_show.iterrows():
            self.tree.insert("", tk.END, values=(row["Nome"], int(row["Idade"]), row["Curso"], float(row["Nota Final"])))

    # Filtra alunos com nota acima do valor informado pelo usuário
    def filtrar_alunos(self):
        val = self.entry_filtro.get().strip()
        try:
            limite = float(val)
        except ValueError:
            messagebox.showerror("Erro", "Informe uma média válida (número).")
            return
        df_filtrado = self.df[self.df["Nota Final"] > limite]
        if df_filtrado.empty:
            messagebox.showinfo("Resultado", "Nenhum aluno com nota acima de {:.2f}.".format(limite))
        self.atualizar_tabela(df_filtrado)
        # guarda filtro atual para exportação
        self._ultimo_filtrado = df_filtrado

    # Salva o DataFrame principal em CSV
    def salvar_csv(self, auto=False):
        try:
            self.df.to_csv(PRINCIPAL_CSV, index=False)
            if not auto:
                messagebox.showinfo("Sucesso", f"Arquivo salvo em:\n{PRINCIPAL_CSV}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar CSV:\n{e}")

    # Carrega CSV do caminho padrão (usado no start) ou via diálogo
    def carregar_csv(self, auto=False):
        if os.path.exists(PRINCIPAL_CSV):
            try:
                df = pd.read_csv(PRINCIPAL_CSV)
                # garantir colunas e tipos
                for col in COLUMNS:
                    if col not in df.columns:
                        df[col] = ""
                df = df[COLUMNS]
                # tentar converter tipos
                df["Idade"] = pd.to_numeric(df["Idade"], errors="coerce").fillna(0).astype(int)
                df["Nota Final"] = pd.to_numeric(df["Nota Final"], errors="coerce").fillna(0.0).astype(float)
                self.df = df
                self.atualizar_tabela()
                if not auto:
                    messagebox.showinfo("Sucesso", f"Arquivo carregado:\n{PRINCIPAL_CSV}")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao carregar CSV:\n{e}")
        else:
            # arquivo não existe: inicia DataFrame vazio
            self.df = pd.DataFrame(columns=COLUMNS)
            if not auto:
                messagebox.showinfo("Aviso", "Nenhum arquivo encontrado. Um novo registro será criado ao salvar.")

    # Carregar CSV via diálogo (escolher arquivo)
    def carregar_csv_dialog(self):
        path = filedialog.askopenfilename(title="Abrir CSV", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if path:
            try:
                df = pd.read_csv(path)
                for col in COLUMNS:
                    if col not in df.columns:
                        df[col] = ""
                df = df[COLUMNS]
                df["Idade"] = pd.to_numeric(df["Idade"], errors="coerce").fillna(0).astype(int)
                df["Nota Final"] = pd.to_numeric(df["Nota Final"], errors="coerce").fillna(0.0).astype(float)
                self.df = df
                self.atualizar_tabela()
                messagebox.showinfo("Sucesso", f"Arquivo carregado:\n{path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao carregar CSV:\n{e}")

    # Exporta o relatório filtrado para CSV
    def exportar_relatorio_filtrado(self):
        df_filtrado = getattr(self, "_ultimo_filtrado", None)
        if df_filtrado is None:
            # sem filtro anterior, perguntar valor agora
            val = self.entry_filtro.get().strip()
            try:
                limite = float(val)
            except ValueError:
                messagebox.showerror("Erro", "Informe uma média válida para filtrar antes de exportar.")
                return
            df_filtrado = self.df[self.df["Nota Final"] > limite]

        try:
            df_filtrado.to_csv(RELATORIO_CSV, index=False)
            messagebox.showinfo("Sucesso", f"Relatório exportado:\n{RELATORIO_CSV}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar relatório:\n{e}")

def main():
    root = tk.Tk()
    app = SistemaAlunos(root)
    root.geometry("800x500")
    root.mainloop()

if __name__ == "__main__":
    main()
