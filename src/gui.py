"""(De)cipher GUI application.

Tkinter wrapper for the cipher modules in `scripts` (AES, DES, Vigenère,
Playfair). The layout and flow are preserved; the code is refactored to
reduce duplication and improve readability without changing behavior.

This module provides helpers to ensure required packages are available,
build the tabbed interface for each cipher, and run encrypt/decrypt
operations via the underlying `scripts` modules.
"""

import sys
import importlib
import subprocess
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, filedialog, messagebox
from style_dark import apply_dark_theme


def _ensure_packages(pack_map):
    """Ensure external packages are available.

    For each mapping (import_name -> pip_name) attempt to import the
    package. If import fails, ask the user for permission to install
    the corresponding `pip_name` using the current Python executable.

    The function prefers Tkinter dialogs for prompts; if a Tk root cannot
    be created it falls back to console input. If the user declines to
    install a required package an ImportError is raised.
    """
    missing = []
    for import_name, pip_name in pack_map.items():
        try:
            importlib.import_module(import_name)
        except Exception:
            missing.append((import_name, pip_name))

    if not missing:
        return

    tmp_root = None
    try:
        tmp_root = tk.Tk()
        tmp_root.withdraw()
    except Exception:
        tmp_root = None

    try:
        for import_name, pip_name in missing:
            msg = (
                f"A biblioteca necessaria '{import_name}' não está instalada.\n\n"
                f"Deseja permitir que a aplicação instale '{pip_name}' agora?"
            )
            allow = False
            try:
                allow = messagebox.askyesno("Instalar dependência", msg, parent=tmp_root)
            except Exception:
                try:
                    resp = input(msg + " [y/N]: ")
                    allow = resp.strip().lower().startswith("y")
                except Exception:
                    allow = False

            if not allow:
                raise ImportError(f"Dependência ausente: {import_name}")

            try:
                if tmp_root:
                    messagebox.showinfo("Instalação", f"Instalando {pip_name}...", parent=tmp_root)
            except Exception:
                pass

            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
            except Exception as e:
                try:
                    if tmp_root:
                        messagebox.showerror("Erro", f"Falha na instalação de {pip_name}: {e}", parent=tmp_root)
                except Exception:
                    pass
                raise
    finally:
        if tmp_root:
            try:
                tmp_root.destroy()
            except Exception:
                pass


_REQUIRED_PACKAGES = {
    "Crypto": "pycryptodome",
}

try:
    _ensure_packages(_REQUIRED_PACKAGES)
except ImportError as e:
    print(f"Erro: {e}")
    sys.exit(1)

from scripts import aes, des, vigenere, playfair

if sys.platform.startswith("win"):
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            from ctypes import windll as _windll
            _windll.user32.SetProcessDPIAware()
        except Exception:
            pass


class CipherGUI:
    """Main application GUI for (De)cipher."""

    def __init__(self, root):
        self.root = root
        self.root.title("(De)cipher™")
        self.root.geometry("960x540")
        self.root.resizable(True, True)

        apply_dark_theme(self.root)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabs = {}
        for tab_name in ["Início", "AES", "DES", "Vigenère", "Playfair"]:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=tab_name)
            self.tabs[tab_name] = frame

        for i in range(len(self.notebook.tabs())):
            try:
                self.notebook.tab(i, padding=[30, 10])
            except Exception:
                pass

        self.setup_start_tab()
        self.setup_cipher_tab("AES")
        self.setup_cipher_tab("DES")
        self.setup_cipher_tab("Vigenère")
        self.setup_cipher_tab("Playfair")

        try:
            self.center_window()
        except Exception:
            pass

    def setup_start_tab(self):
        frame = self.tabs["Início"]
        try:
            scale = float(self.root.tk.call('tk', 'scaling'))
        except Exception:
            scale = 1.0
        welcome_size = max(8, int(round(11 * scale)))
        label = ttk.Label(
            frame,
            text=(
                "🔐 Bem-vindo à aplicação (De)cipher™\n\n"
                "Aqui pode fazer a Cifra e Decifra de Ficheiros.\n\n"
                "Selecione uma aba acima para escolher o método de cifra.\n\n"
            ),
            justify="center",
            font=("Segoe UI", welcome_size)
        )
        label.pack(expand=True, pady=100)
        label.pack(expand=True, pady=100)

    def _set_entry_path(self, entry, path):
        """Set `path` into an Entry widget while preserving readonly state.

        The helper attempts several strategies in order:
        - If the Entry uses a `textvariable`, set it via `setvar`.
        - If the widget supports the ttk `state()` API, temporarily remove
          `readonly`, update the value and restore previous states.
        - Fall back to using `config(state=...)` on a tk.Entry.
        """
        if not path:
            return

        try:
            tv_name = entry.cget('textvariable')
            if tv_name:
                try:
                    entry.setvar(tv_name, path)
                    return
                except Exception:
                    pass
        except Exception:
            pass

        try:
            state_fn = getattr(entry, 'state', None)
            if callable(state_fn):
                try:
                    prev_states = list(entry.state())
                except Exception:
                    prev_states = []
                try:
                    entry.state(['!readonly'])
                except Exception:
                    pass
                try:
                    entry.delete(0, tk.END)
                    entry.insert(0, path)
                finally:
                    try:
                        if 'readonly' in prev_states:
                            entry.state(['readonly'])
                    except Exception:
                        pass
                return
        except Exception:
            pass

        try:
            prev_state = entry.cget('state')
        except Exception:
            prev_state = None
        try:
            if prev_state == 'readonly':
                entry.config(state='normal')
            entry.delete(0, tk.END)
            entry.insert(0, path)
        finally:
            if prev_state == 'readonly':
                try:
                    entry.config(state='readonly')
                except Exception:
                    pass

    def _open_path_dialog(self, entry, save=False):
        """Open a file dialog (open or save) and write the selected path.

        If `save` is True opens a save-as dialog, otherwise opens an
        open-file dialog. The selected path (if any) is written into the
        provided `entry` via `_set_entry_path`.
        """
        if save:
            path = filedialog.asksaveasfilename(defaultextension=".txt")
        else:
            path = filedialog.askopenfilename()
        if path:
            self._set_entry_path(entry, path)

    def _make_radio_group(self, parent, var):
        """Create and return a frame containing 'Encrypt'/'Decrypt' radios.

        The function returns a frame containing two radio buttons bound
        to `var`. The visual styling uses custom tk.Radiobuttons when
        possible and falls back to ttk.Radiobuttons on error.
        """
        rb_frame = ttk.Frame(parent)
        try:
            dark_bg = "#1e1e1e"
            dark_active = "#3a3a3a"
            fg = "#ffffff"
            tk.Radiobutton(rb_frame, text="Cifrar", variable=var, value="encrypt",
                           bg=dark_bg, fg=fg, selectcolor=dark_active,
                           activebackground=dark_active, activeforeground=fg,
                           bd=0, highlightthickness=0, anchor="w").pack(side="left", padx=(0, 10))
            tk.Radiobutton(rb_frame, text="Decifrar", variable=var, value="decrypt",
                           bg=dark_bg, fg=fg, selectcolor=dark_active,
                           activebackground=dark_active, activeforeground=fg,
                           bd=0, highlightthickness=0, anchor="w").pack(side="left")
        except Exception:
            ttk.Radiobutton(rb_frame, text="Cifrar", variable=var, value="encrypt").pack(side="left", padx=(0, 10))
            ttk.Radiobutton(rb_frame, text="Decifrar", variable=var, value="decrypt").pack(side="left")
        return rb_frame

    def _make_log_box(self, parent):
        """Create and return a read-only log Text widget configured for dark theme."""
        log_box = tk.Text(parent, height=10, width=90, bg="#2d2d2d", fg="#ffffff", insertbackground="white")
        try:
            log_box.config(state="disabled")
        except Exception:
            pass
        return log_box

    def setup_cipher_tab(self, cipher_type):
        frame = self.tabs[cipher_type]

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=0)
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=0)
        frame.grid_columnconfigure(2, weight=1)

        content = ttk.Frame(frame)
        content.grid(row=1, column=1)

        if cipher_type == "Playfair":
            ttk.Label(content, text="Ficheiro da Tabela:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
            key_entry = ttk.Entry(content, width=55, state="readonly")
            key_entry.grid(row=0, column=1, padx=10, pady=5)
            ttk.Button(content, text="Procurar", command=lambda e=key_entry: self._open_path_dialog(e)).grid(row=0, column=2, padx=5)
            key_row = 1

        elif cipher_type == "Vigenère":
            ttk.Label(content, text="Ficheiro da Tabela:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
            self.vig_table_entry = ttk.Entry(content, width=55, state="readonly")
            self.vig_table_entry.grid(row=0, column=1, padx=10, pady=5)
            ttk.Button(content, text="Procurar", command=lambda: self._open_path_dialog(self.vig_table_entry)).grid(row=0, column=2, padx=5)

            ttk.Label(content, text="Ficheiro da Chave:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
            self.vig_key_entry = ttk.Entry(content, width=55, state="readonly")
            self.vig_key_entry.grid(row=1, column=1, padx=10, pady=5)
            ttk.Button(content, text="Procurar", command=lambda: self._open_path_dialog(self.vig_key_entry)).grid(row=1, column=2, padx=5)
            key_entry = self.vig_key_entry
            key_row = 1

        else:
            ttk.Label(content, text="Ficheiro da Chave:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
            key_entry = ttk.Entry(content, width=55, state="readonly")
            key_entry.grid(row=0, column=1, padx=10, pady=5)
            ttk.Button(content, text="Procurar", command=lambda e=key_entry: self._open_path_dialog(e)).grid(row=0, column=2, padx=5)
            key_row = 0

        ttk.Label(content, text="Ficheiro de Entrada:").grid(row=key_row+1, column=0, padx=10, pady=5, sticky="e")
        input_entry = ttk.Entry(content, width=55, state="readonly")
        input_entry.grid(row=key_row+1, column=1, padx=10, pady=5)
        ttk.Button(content, text="Procurar", command=lambda e=input_entry: self._open_path_dialog(e)).grid(row=key_row+1, column=2, padx=5)

        ttk.Label(content, text="Ficheiro de Saída:").grid(row=key_row+2, column=0, padx=10, pady=5, sticky="e")
        output_entry = ttk.Entry(content, width=55, state="readonly")
        output_entry.grid(row=key_row+2, column=1, padx=10, pady=5)
        ttk.Button(content, text="Guardar como", command=lambda e=output_entry: self._open_path_dialog(e, save=True)).grid(row=key_row+2, column=2, padx=5)

        action_var = tk.StringVar(value="encrypt")
        rb_frame = self._make_radio_group(content, action_var)
        rb_frame.grid(row=key_row+3, column=1)

        if cipher_type == "Vigenère":
            cmd = self.run_vigenere
        else:
            cmd = lambda ct=cipher_type, ke=key_entry, ie=input_entry, oe=output_entry, av=action_var: self.run_cipher(ct, ke, ie, oe, av)

        ttk.Button(content, text="Executar", command=cmd).grid(row=key_row+4, column=1, pady=10)

        log_box = self._make_log_box(content)
        log_box.grid(row=key_row+5, column=0, columnspan=3, padx=10, pady=10)

        frame.key_entry = key_entry
        frame.input_entry = input_entry
        frame.output_entry = output_entry
        frame.action_var = action_var
        frame.log_box = log_box

        if cipher_type == "Vigenère":
            self.vig_input_entry = input_entry
            self.vig_output_entry = output_entry
            self.vig_action = action_var
            self.vig_log = log_box

    def log_message(self, box, message):
        """Append a line to the log box, toggling read-only state briefly."""
        try:
            box.config(state="normal")
            box.insert(tk.END, message + "\n")
            box.config(state="disabled")
            box.see(tk.END)
        except Exception:
            pass

    def center_window(self):
        """Center the main application window on the screen."""
        self.root.update_idletasks()

        width = self.root.winfo_width()
        height = self.root.winfo_height()
        if width <= 1 or height <= 1:
            try:
                geom = self.root.geometry()
                size = geom.split('+')[0]
                width, height = map(int, size.split('x'))
            except Exception:
                width, height = 960, 540

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = max(0, (screen_width - width) // 2)
        y = max(0, (screen_height - height) // 2)

        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def run_cipher(self, cipher_type, key_entry, input_entry, output_entry, action_var):
        """Run the selected cipher module to encrypt or decrypt a file.

        Parameters:
            cipher_type (str): one of 'AES', 'DES', 'Playfair'.
            key_entry (tk.Entry): Entry widget holding the key or key path.
            input_entry (tk.Entry): Entry widget holding input file path.
            output_entry (tk.Entry): Entry widget holding output file path.
            action_var (tk.StringVar): 'encrypt' or 'decrypt'.
        """
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
        """Run Vigenère-specific encrypt/decrypt using the GUI-provided paths."""
        if not hasattr(self, 'vig_table_entry') or not hasattr(self, 'vig_key_entry'):
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
    try:
        dpi = root.winfo_fpixels('1i')
        scaling = dpi / 96.0
        root.tk.call('tk', 'scaling', scaling)
        try:
            names = [
                "TkDefaultFont",
                "TkMenuFont",
                "TkTextFont",
                "TkHeadingFont",
                "TkCaptionFont",
                "TkSmallCaptionFont",
                "TkIconFont",
            ]
            for name in names:
                try:
                    f = tkfont.nametofont(name)
                    orig = f.cget("size")
                    try:
                        orig_val = float(orig)
                    except Exception:
                        orig_val = 10.0
                    new_size = max(6, int(round(orig_val * scaling)))
                    f.configure(size=new_size)
                except Exception:
                    pass
        except Exception:
            pass
    except Exception:
        pass

    app = CipherGUI(root)
    root.mainloop()
