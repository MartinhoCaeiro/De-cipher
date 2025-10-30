import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from scripts import aes, des, vigenere, playfair
from style_dark import apply_dark_theme

class CipherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("(De)cipher™")
        self.root.geometry("960x540")
        self.root.resizable(True, True)

        # Aplica tema escuro
        apply_dark_theme(self.root)

        # Notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabs = {}
        for tab_name in ["Início", "AES", "DES", "Vigenère", "Playfair"]:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=tab_name)
            self.tabs[tab_name] = frame

            # Centraliza o texto das abas
        for i in range(len(self.notebook.tabs())):
            # Notebook.tab supports padding; ignore other options if not supported on a platform
            try:
                self.notebook.tab(i, padding=[30, 10])
            except Exception:
                pass

        self.setup_start_tab()
        # Create cipher tabs' controls
        self.setup_cipher_tab("AES")
        self.setup_cipher_tab("DES")
        self.setup_cipher_tab("Vigenère")
        self.setup_cipher_tab("Playfair")

        # Center the main window on the screen
        try:
            self.center_window()
        except Exception:
            # If centering fails for any reason, don't crash the app
            pass

    def setup_start_tab(self):
        frame = self.tabs["Início"]
        label = ttk.Label(
            frame,
            text=(
                "🔐 Bem-vindo à aplicação de Cifra e Decifra de Ficheiros\n\n"
                "Selecione uma aba acima para escolher o método de cifra.\n\n"
                "• AES e DES utilizam ficheiros de chave binários ou texto.\n"
                "• Vigenère e Playfair utilizam ficheiros de tabela e texto ASCII."
            ),
            justify="center",
            font=("Segoe UI", 11)
        )
        label.pack(expand=True, pady=100)
    def setup_cipher_tab(self, cipher_type):
        frame = self.tabs[cipher_type]

        # Create a centered content frame inside the tab frame.
        # Configure outer frame to have three rows and three columns so the middle cell stays centered.
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=0)
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=0)
        frame.grid_columnconfigure(2, weight=1)

        content = ttk.Frame(frame)
        # place content in the middle cell
        content.grid(row=1, column=1)

        # Determinar rótulo do arquivo de chave/tabela e construir widgets inside content
        if cipher_type == "Playfair":
            ttk.Label(content, text="Ficheiro da Tabela:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
            key_entry = ttk.Entry(content, width=55)
            key_entry.grid(row=0, column=1, padx=10, pady=5)
            ttk.Button(content, text="Procurar", command=lambda e=key_entry: self.browse_file(e)).grid(row=0, column=2, padx=5)
            key_row = 1

        elif cipher_type == "Vigenère":
            ttk.Label(content, text="Ficheiro da Tabela:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
            self.vig_table_entry = ttk.Entry(content, width=55)
            self.vig_table_entry.grid(row=0, column=1, padx=10, pady=5)
            ttk.Button(content, text="Procurar", command=lambda: self.browse_file(self.vig_table_entry)).grid(row=0, column=2, padx=5)

            ttk.Label(content, text="Ficheiro da Chave:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
            self.vig_key_entry = ttk.Entry(content, width=55)
            self.vig_key_entry.grid(row=1, column=1, padx=10, pady=5)
            ttk.Button(content, text="Procurar", command=lambda: self.browse_file(self.vig_key_entry)).grid(row=1, column=2, padx=5)
            key_entry = self.vig_key_entry
            key_row = 1

        else:
            ttk.Label(content, text="Ficheiro da Chave:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
            key_entry = ttk.Entry(content, width=55)
            key_entry.grid(row=0, column=1, padx=10, pady=5)
            ttk.Button(content, text="Procurar", command=lambda e=key_entry: self.browse_file(e)).grid(row=0, column=2, padx=5)
            key_row = 0

        # Entradas de input e output
        ttk.Label(content, text="Ficheiro de Entrada:").grid(row=key_row+1, column=0, padx=10, pady=5, sticky="e")
        input_entry = ttk.Entry(content, width=55)
        input_entry.grid(row=key_row+1, column=1, padx=10, pady=5)
        ttk.Button(content, text="Procurar", command=lambda e=input_entry: self.browse_file(e)).grid(row=key_row+1, column=2, padx=5)

        ttk.Label(content, text="Ficheiro de Saída:").grid(row=key_row+2, column=0, padx=10, pady=5, sticky="e")
        output_entry = ttk.Entry(content, width=55)
        output_entry.grid(row=key_row+2, column=1, padx=10, pady=5)
        ttk.Button(content, text="Guardar como", command=lambda e=output_entry: self.save_file(e)).grid(row=key_row+2, column=2, padx=5)

        # Ação (cifrar/decifrar)
        action_var = tk.StringVar(value="encrypt")
        ttk.Radiobutton(content, text="Cifrar", variable=action_var, value="encrypt").grid(row=key_row+3, column=1, sticky="w", padx=10)
        ttk.Radiobutton(content, text="Decifrar", variable=action_var, value="decrypt").grid(row=key_row+3, column=1, sticky="e", padx=10)

        # Botão executar
        if cipher_type == "Vigenère":
            cmd = self.run_vigenere
        else:
            cmd = lambda ct=cipher_type, ke=key_entry, ie=input_entry, oe=output_entry, av=action_var: self.run_cipher(ct, ke, ie, oe, av)

        ttk.Button(content, text="Executar", command=cmd).grid(row=key_row+4, column=1, pady=10)

        # Caixa de log
        log_box = tk.Text(content, height=10, width=90, bg="#2d2d2d", fg="#ffffff", insertbackground="white")
        log_box.grid(row=key_row+5, column=0, columnspan=3, padx=10, pady=10)

        # Armazenar referências
        frame.key_entry = key_entry
        frame.input_entry = input_entry
        frame.output_entry = output_entry
        frame.action_var = action_var
        frame.log_box = log_box

        # Se for Vigenère, manter referências de forma que run_vigenere as encontre
        if cipher_type == "Vigenère":
            self.vig_input_entry = input_entry
            self.vig_output_entry = output_entry
            self.vig_action = action_var
            self.vig_log = log_box

    def browse_file(self, entry):
        path = filedialog.askopenfilename()
        if path:
            entry.delete(0, tk.END)
            entry.insert(0, path)

    def save_file(self, entry):
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path:
            entry.delete(0, tk.END)
            entry.insert(0, path)

    def log_message(self, box, message):
        try:
            box.config(state="normal")
            box.insert(tk.END, message + "\n")
            box.config(state="disabled")
            box.see(tk.END)
        except Exception:
            # If the log box is not available, silently ignore to avoid crashes
            pass

    def center_window(self):
        """Center the main window on the screen.

        This computes the desired geometry and updates the window position.
        Works even if the window manager hasn't fully realized the window yet.
        """
        # Ensure geometry info is up to date
        self.root.update_idletasks()

        # Try to get the current size; fall back to parsing geometry string if needed
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        if width <= 1 or height <= 1:
            geom = self.root.geometry()  # format: 'WxH+X+Y'
            try:
                size = geom.split('+')[0]
                width, height = map(int, size.split('x'))
            except Exception:
                # fallback to a reasonable default
                width, height = 960, 540

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = max(0, (screen_width - width) // 2)
        y = max(0, (screen_height - height) // 2)

        self.root.geometry(f"{width}x{height}+{x}+{y}")


    def run_cipher(self, cipher_type, key_entry, input_entry, output_entry, action_var):
        key = key_entry.get().strip() if key_entry is not None else ""
        input_path = input_entry.get().strip()
        output_path = output_entry.get().strip()
        action = action_var.get()

        if not all([key, input_path, output_path]):
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
            return

        module_map = {"AES": aes, "DES": des, "Playfair": playfair}
        module = module_map.get(cipher_type)
        if module is None:
            messagebox.showerror("Erro", f"Módulo para '{cipher_type}' não encontrado.")
            return

        log_box = self.tabs[cipher_type].log_box

        try:
            if action == "encrypt":
                module.encrypt_file(input_path, output_path, key)
                self.log_message(log_box, f"[{cipher_type}] Ficheiro cifrado com sucesso.")
            else:
                module.decrypt_file(input_path, output_path, key)
                self.log_message(log_box, f"[{cipher_type}] Ficheiro decifrado com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))
            self.log_message(log_box, f"Erro: {e}")

    def run_vigenere(self):
        tabela_path = getattr(self, 'vig_table_entry', None)
        chave_entry = getattr(self, 'vig_key_entry', None)
        if tabela_path is None or chave_entry is None:
            messagebox.showerror("Erro", "Widgets do Vigenère não estão inicializados corretamente.")
            return

        tabela_path = self.vig_table_entry.get().strip()
        chave_path = self.vig_key_entry.get().strip()
        input_path = self.vig_input_entry.get().strip()
        output_path = self.vig_output_entry.get().strip()
        action = self.vig_action.get()

        if not all([tabela_path, chave_path, input_path, output_path]):
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
            return

        try:
            if action == "encrypt":
                vigenere.encrypt_file(input_path, output_path, [tabela_path, chave_path])
                self.log_message(self.vig_log, "[Vigenère] Ficheiro cifrado com sucesso.")
            else:
                vigenere.decrypt_file(input_path, output_path, [tabela_path, chave_path])
                self.log_message(self.vig_log, "[Vigenère] Ficheiro decifrado com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))
            self.log_message(self.vig_log, f"Erro: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CipherGUI(root)
    root.mainloop()
