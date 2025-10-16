import os
import sys
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

APP_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
PRINCIPAL_CSV = os.path.join(APP_DIR, "alunos.csv")
RELATORIO_CSV = os.path.join(APP_DIR, "relatorio_filtrado.csv")
COLUMNS = ["Nome", "Idade", "Curso", "Nota Final"]

class SistemaAlunos:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Cadastro e Relatórios de Alunos")
        self.root.configure(bg='#f0f0f0')
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._configurar_estilos()
        
        self.df = pd.DataFrame(columns=COLUMNS)
        self.indice_editando = None
        self._criar_widgets()
        self.carregar_csv(auto=True)

    def _configurar_estilos(self):
        """Configura estilos simples para os widgets"""
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', foreground='#333333', font=('Segoe UI', 9))
        self.style.configure('TButton', font=('Segoe UI', 9), padding=6)
        self.style.configure('Header.TLabel', font=('Segoe UI', 11, 'bold'), foreground='#2c3e50')
        self.style.configure('TEntry', padding=5)
        self.style.configure('Treeview', font=('Segoe UI', 9), rowheight=25)
        self.style.configure('Treeview.Heading', font=('Segoe UI', 9, 'bold'), background='#e0e0e0', foreground='black')
        
        self.style.configure('Success.TButton', background='#27ae60', foreground='white')
        self.style.map('Success.TButton', 
                      background=[('active', '#219653')])
        
        self.style.configure('Danger.TButton', background='#e74c3c', foreground='white')
        self.style.map('Danger.TButton', 
                      background=[('active', '#c0392b')])

    def _criar_widgets(self):
        # Container principal
        main_container = ttk.Frame(self.root, padding=20)
        main_container.pack(fill="both", expand=True)

        # Header
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(header_frame, text="Sistema de Gestão de Alunos", 
                 style='Header.TLabel').pack(side="left")
        
        # Frame de cadastro
        frm_cadastro = ttk.Frame(main_container, padding=15)
        frm_cadastro.pack(fill="x", pady=(0, 15))

        # Grid de campos
        ttk.Label(frm_cadastro, text="Nome:").grid(row=0, column=0, sticky="w", padx=(0, 5), pady=5)
        self.entry_nome = ttk.Entry(frm_cadastro, width=25, font=('Segoe UI', 9))
        self.entry_nome.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(frm_cadastro, text="Idade:").grid(row=0, column=2, sticky="w", padx=(20, 5), pady=5)
        self.entry_idade = ttk.Entry(frm_cadastro, width=8, font=('Segoe UI', 9))
        self.entry_idade.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frm_cadastro, text="Curso:").grid(row=1, column=0, sticky="w", padx=(0, 5), pady=5)
        self.entry_curso = ttk.Entry(frm_cadastro, width=25, font=('Segoe UI', 9))
        self.entry_curso.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(frm_cadastro, text="Nota Final:").grid(row=1, column=2, sticky="w", padx=(20, 5), pady=5)
        self.entry_nota = ttk.Entry(frm_cadastro, width=8, font=('Segoe UI', 9))
        self.entry_nota.grid(row=1, column=3, padx=5, pady=5)

        btn_cadastrar = ttk.Button(frm_cadastro, text="Cadastrar Aluno", 
                                 command=self.cadastrar_aluno, style='Success.TButton')
        btn_cadastrar.grid(row=0, column=4, rowspan=2, padx=(20, 0), pady=5, sticky="ns")

        frm_cadastro.columnconfigure(1, weight=1)

        frm_acoes = ttk.Frame(main_container, padding=15)
        frm_acoes.pack(fill="x", pady=(0, 15))

        # Filtros
        ttk.Label(frm_acoes, text="Filtrar por nota >").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.entry_filtro = ttk.Entry(frm_acoes, width=10, font=('Segoe UI', 9))
        self.entry_filtro.grid(row=0, column=1, padx=5)
        
        btn_filtrar = ttk.Button(frm_acoes, text="Aplicar Filtro", command=self.filtrar_alunos)
        btn_filtrar.grid(row=0, column=2, padx=5)
        
        btn_mostrar_todos = ttk.Button(frm_acoes, text="Mostrar Todos", command=self.atualizar_tabela)
        btn_mostrar_todos.grid(row=0, column=3, padx=5)

        btn_exportar = ttk.Button(frm_acoes, text="Exportar Relatório", command=self.exportar_relatorio_filtrado)
        btn_exportar.grid(row=0, column=4, padx=5)

        # Segunda linha de botões
        btn_salvar = ttk.Button(frm_acoes, text="Salvar CSV", command=self.salvar_csv)
        btn_salvar.grid(row=1, column=0, padx=5, pady=(10, 0))
        
        btn_carregar = ttk.Button(frm_acoes, text="Carregar CSV", command=self.carregar_csv_dialog)
        btn_carregar.grid(row=1, column=1, padx=5, pady=(10, 0))

        btn_editar = ttk.Button(frm_acoes, text="Editar Selecionado", command=self.editar_aluno)
        btn_editar.grid(row=1, column=2, padx=5, pady=(10, 0))

        btn_excluir = ttk.Button(frm_acoes, text="Excluir Selecionado", 
                               command=self.excluir_aluno, style='Danger.TButton')
        btn_excluir.grid(row=1, column=3, padx=5, pady=(10, 0))

        frm_tabela = ttk.Frame(main_container)
        frm_tabela.pack(fill="both", expand=True)

        table_frame = ttk.Frame(frm_tabela)
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Treeview com cabeçalho cinza
        self.tree = ttk.Treeview(table_frame, columns=COLUMNS, show="headings")
        
        # Configurar colunas
        for col in COLUMNS:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        
        # Layout da tabela e scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Status bar
        self.status_bar = ttk.Label(main_container, text="Pronto", relief="sunken", style='TLabel')
        self.status_bar.pack(fill="x", pady=(10, 0))

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
            if idade <= 0:
                raise ValueError("Idade deve ser positiva")
            nota = float(nota_str)
            if nota < 0 or nota > 10:
                raise ValueError("Nota deve estar entre 0 e 10")
        except ValueError as e:
            messagebox.showerror("Erro", f"Verifique os campos numéricos:\n{e}")
            return

        novo = {"Nome": nome, "Idade": idade, "Curso": curso, "Nota Final": nota}

        # Se estiver editando, atualiza o registro existente
        if self.indice_editando is not None:
            self.df.loc[self.indice_editando] = novo
            self.indice_editando = None
            messagebox.showinfo("Sucesso", "Aluno atualizado com sucesso.")
            self.status_bar.config(text="Aluno atualizado com sucesso")
        else:
            self.df = pd.concat([self.df, pd.DataFrame([novo])], ignore_index=True)
            messagebox.showinfo("Sucesso", "Aluno cadastrado com sucesso.")
            self.status_bar.config(text="Aluno cadastrado com sucesso")

        self.atualizar_tabela()
        self.salvar_csv(auto=True)
        self.limpar_campos()

    def limpar_campos(self):
        self.entry_nome.delete(0, tk.END)
        self.entry_idade.delete(0, tk.END)
        self.entry_curso.delete(0, tk.END)
        self.entry_nota.delete(0, tk.END)
        self.indice_editando = None

    def atualizar_tabela(self, df_view=None):
        df_show = self.df if df_view is None else df_view
        for row in self.tree.get_children():
            self.tree.delete(row)
        for i, row in df_show.iterrows():
            self.tree.insert("", tk.END, iid=i, values=(row["Nome"], int(row["Idade"]), row["Curso"], f"{float(row['Nota Final']):.1f}"))
        
        # Atualizar status
        total = len(self.df)
        filtrado = len(df_show) if df_view is not None else None
        if filtrado is not None and filtrado != total:
            self.status_bar.config(text=f"Mostrando {filtrado} de {total} alunos (filtrado)")
        else:
            self.status_bar.config(text=f"Total de {total} alunos cadastrados")

    def editar_aluno(self):
        selecionado = self.tree.focus()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um aluno para editar.")
            return
        self.indice_editando = int(selecionado)
        aluno = self.df.loc[self.indice_editando]
        
        self.limpar_campos()
        self.entry_nome.insert(0, aluno["Nome"])
        self.entry_idade.insert(0, str(aluno["Idade"]))
        self.entry_curso.insert(0, aluno["Curso"])
        self.entry_nota.insert(0, str(aluno["Nota Final"]))
        
        self.status_bar.config(text=f"Editando aluno: {aluno['Nome']}")

    def excluir_aluno(self):
        selecionado = self.tree.focus()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um aluno para excluir.")
            return
        idx = int(selecionado)
        nome = self.df.loc[idx, "Nome"]
        if messagebox.askyesno("Confirmação", f"Tem certeza que deseja excluir {nome}?"):
            self.df = self.df.drop(idx).reset_index(drop=True)
            self.atualizar_tabela()
            self.salvar_csv(auto=True)
            messagebox.showinfo("Sucesso", "Aluno excluído com sucesso.")
            self.status_bar.config(text=f"Aluno {nome} excluído com sucesso")

    def filtrar_alunos(self):
        val = self.entry_filtro.get().strip()
        try:
            limite = float(val)
        except ValueError:
            messagebox.showerror("Erro", "Informe uma média válida.")
            return
        
        df_filtrado = self.df[self.df["Nota Final"] > limite]
        if df_filtrado.empty:
            messagebox.showinfo("Resultado", f"Nenhum aluno com nota acima de {limite:.2f}.")
            self.status_bar.config(text=f"Nenhum aluno encontrado com nota acima de {limite:.1f}")
        else:
            self.status_bar.config(text=f"Encontrados {len(df_filtrado)} alunos com nota acima de {limite:.1f}")
        
        self.atualizar_tabela(df_filtrado)
        self._ultimo_filtrado = df_filtrado

    def salvar_csv(self, auto=False):
        try:
            self.df.to_csv(PRINCIPAL_CSV, index=False)
            if not auto:
                messagebox.showinfo("Sucesso", f"Arquivo salvo em:\n{PRINCIPAL_CSV}")
                self.status_bar.config(text="Dados salvos com sucesso")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar CSV:\n{e}")

    def carregar_csv(self, auto=False):
        if os.path.exists(PRINCIPAL_CSV):
            try:
                df = pd.read_csv(PRINCIPAL_CSV)
                for col in COLUMNS:
                    if col not in df.columns:
                        df[col] = ""
                df = df[COLUMNS]
                df["Idade"] = pd.to_numeric(df["Idade"], errors="coerce").fillna(0).astype(int)
                df["Nota Final"] = pd.to_numeric(df["Nota Final"], errors="coerce").fillna(0.0).astype(float)
                self.df = df
                self.atualizar_tabela()
                if not auto:
                    self.status_bar.config(text="Dados carregados automaticamente")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao carregar CSV:\n{e}")
        else:
            self.df = pd.DataFrame(columns=COLUMNS)

    def carregar_csv_dialog(self):
        path = filedialog.askopenfilename(
            title="Abrir CSV", 
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=APP_DIR
        )
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
                self.status_bar.config(text=f"Dados carregados de: {os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao carregar CSV:\n{e}")

    def exportar_relatorio_filtrado(self):
        df_filtrado = getattr(self, "_ultimo_filtrado", None)
        if df_filtrado is None or df_filtrado.empty:
            messagebox.showerror("Erro", "Nenhum filtro aplicado para exportar.")
            return
        try:
            df_filtrado.to_csv(RELATORIO_CSV, index=False)
            messagebox.showinfo("Sucesso", f"Relatório exportado:\n{RELATORIO_CSV}")
            self.status_bar.config(text=f"Relatório exportado: {os.path.basename(RELATORIO_CSV)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar relatório:\n{e}")

def main():
    root = tk.Tk()
    root.geometry("900x600")
    root.minsize(800, 500)
    
    # Centralizar na tela
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (900 // 2)
    y = (root.winfo_screenheight() // 2) - (600 // 2)
    root.geometry(f"900x600+{x}+{y}")
    
    app = SistemaAlunos(root)
    root.mainloop()

if __name__ == "__main__":
    main()