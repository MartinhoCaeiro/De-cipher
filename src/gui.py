"""(De)cipher GUI application.

This module provides a small Tkinter-based GUI wrapper around the
encryption/decryption modules in `scripts` (AES, DES, Vigenère, Playfair).

Run the file directly to start the GUI (creates a `tk.Tk()` root and
instantiates `CipherGUI`). The GUI expects the cipher modules to expose
`encrypt_file(input_path, output_path, key)` and
`decrypt_file(input_path, output_path, key)` (Vigenère accepts a list of
paths for table and key as shown in the implementation).

The UI focuses on file selection and simple logging; cryptographic
operations are delegated to the modules in `scripts`.
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

    pack_map: mapping of import_name -> pip_package_name

    For each mapping, try to import the module. If import fails, prompt
    the user (via a temporarily created hidden Tk root) asking whether
    the program may install the required pip package. If the user
    agrees, run `python -m pip install <package>` using the current
    interpreter. If installation fails or the user declines, the
    function will raise ImportError.
    """
    missing = []
    for import_name in pack_map:
        try:
            importlib.import_module(import_name)
        except Exception:
            missing.append((import_name, pack_map[import_name]))

    if not missing:
        return

    # Create a temporary hidden Tk root for dialogs
    _tmp_root = None
    try:
        _tmp_root = tk.Tk()
        _tmp_root.withdraw()
    except Exception:
        _tmp_root = None

    for import_name, pip_name in missing:
        msg = (
            f"A biblioteca requerida '{import_name}' não está instalada.\n\n"
            f"Deseja permitir que a aplicação instale '{pip_name}' agora?"
        )
        allow = False
        try:
            allow = messagebox.askyesno("Instalar dependência", msg, parent=_tmp_root)
        except Exception:
            # fallback to console prompt if messagebox not available
            try:
                resp = input(msg + " [y/N]: ")
                allow = resp.strip().lower().startswith("y")
            except Exception:
                allow = False

        if not allow:
            if _tmp_root:
                try:
                    _tmp_root.destroy()
                except Exception:
                    pass
            raise ImportError(f"Dependência ausente: {import_name}")

        # Run pip install using the current Python executable
        try:
            messagebox.showinfo("Instalação", f"Instalando {pip_name}...", parent=_tmp_root)
        except Exception:
            pass
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
        except Exception as e:
            try:
                messagebox.showerror("Erro", f"Falha na instalação de {pip_name}: {e}", parent=_tmp_root)
            except Exception:
                pass
            if _tmp_root:
                try:
                    _tmp_root.destroy()
                except Exception:
                    pass
            raise

    if _tmp_root:
        try:
            _tmp_root.destroy()
        except Exception:
            pass


# Map import names to pip package names when they differ. Add more
# entries if future scripts require other third-party libraries.
_REQUIRED_PACKAGES = {
    "Crypto": "pycryptodome",
}

# Ensure dependencies are present before importing modules that need them.
try:
    _ensure_packages(_REQUIRED_PACKAGES)
except ImportError as e:
    # If dependencies are missing and user declined install, exit.
    print(f"Erro: {e}")
    sys.exit(1)

# Now safe to import local cipher modules that may depend on third-party libs
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
    """Main application GUI for (De)cipher.

    Responsibilities:
    - Build and manage the Tkinter widgets (tabs, file selectors, actions).
    - Validate user input and call the appropriate cipher module functions.
    - Provide lightweight logging to the UI.

    The class keeps references to the important widgets so action handlers
    (e.g., `run_cipher`) can read user selections and report results.
    """
    def __init__(self, root):
        """Initialize the GUI and build all tabs and widgets.

        Args:
            root: The Tkinter root window (tk.Tk instance).
        """
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
        """Populate the 'Início' (start) tab with a brief welcome message.

        This method keeps the widget creation focused and separate from the
        rest of the layout code so the welcome content is easy to locate.
        """
    def setup_cipher_tab(self, cipher_type):
        frame = self.tabs[cipher_type]

        """Create controls for a given cipher tab.

        Args:
            cipher_type: One of "AES", "DES", "Vigenère", or "Playfair".

        The controls include key/table selection, input/output file selectors,
        action (encrypt/decrypt) radio buttons, an Execute button and a
        read-only log text box.
        """

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
            ttk.Button(content, text="Procurar", command=lambda e=key_entry: self.browse_file(e)).grid(row=0, column=2, padx=5)
            key_row = 1

        elif cipher_type == "Vigenère":
            ttk.Label(content, text="Ficheiro da Tabela:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
            self.vig_table_entry = ttk.Entry(content, width=55, state="readonly")
            self.vig_table_entry.grid(row=0, column=1, padx=10, pady=5)
            ttk.Button(content, text="Procurar", command=lambda: self.browse_file(self.vig_table_entry)).grid(row=0, column=2, padx=5)

            ttk.Label(content, text="Ficheiro da Chave:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
            self.vig_key_entry = ttk.Entry(content, width=55, state="readonly")
            self.vig_key_entry.grid(row=1, column=1, padx=10, pady=5)
            ttk.Button(content, text="Procurar", command=lambda: self.browse_file(self.vig_key_entry)).grid(row=1, column=2, padx=5)
            key_entry = self.vig_key_entry
            key_row = 1

        else:
            ttk.Label(content, text="Ficheiro da Chave:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
            key_entry = ttk.Entry(content, width=55, state="readonly")
            key_entry.grid(row=0, column=1, padx=10, pady=5)
            ttk.Button(content, text="Procurar", command=lambda e=key_entry: self.browse_file(e)).grid(row=0, column=2, padx=5)
            key_row = 0

        ttk.Label(content, text="Ficheiro de Entrada:").grid(row=key_row+1, column=0, padx=10, pady=5, sticky="e")
        input_entry = ttk.Entry(content, width=55, state="readonly")
        input_entry.grid(row=key_row+1, column=1, padx=10, pady=5)
        ttk.Button(content, text="Procurar", command=lambda e=input_entry: self.browse_file(e)).grid(row=key_row+1, column=2, padx=5)

        ttk.Label(content, text="Ficheiro de Saída:").grid(row=key_row+2, column=0, padx=10, pady=5, sticky="e")
        output_entry = ttk.Entry(content, width=55, state="readonly")
        output_entry.grid(row=key_row+2, column=1, padx=10, pady=5)
        ttk.Button(content, text="Guardar como", command=lambda e=output_entry: self.save_file(e)).grid(row=key_row+2, column=2, padx=5)

        action_var = tk.StringVar(value="encrypt")
        rb_frame = ttk.Frame(content)
        rb_frame.grid(row=key_row+3, column=1)
        try:
            dark_bg = "#1e1e1e"
            dark_active = "#3a3a3a"
            fg = "#ffffff"
            tk.Radiobutton(rb_frame, text="Cifrar", variable=action_var, value="encrypt",
                           bg=dark_bg, fg=fg, selectcolor=dark_active,
                           activebackground=dark_active, activeforeground=fg,
                           bd=0, highlightthickness=0, anchor="w").pack(side="left", padx=(0, 10))
            tk.Radiobutton(rb_frame, text="Decifrar", variable=action_var, value="decrypt",
                           bg=dark_bg, fg=fg, selectcolor=dark_active,
                           activebackground=dark_active, activeforeground=fg,
                           bd=0, highlightthickness=0, anchor="w").pack(side="left")
        except Exception:
            ttk.Radiobutton(rb_frame, text="Cifrar", variable=action_var, value="encrypt").pack(side="left", padx=(0, 10))
            ttk.Radiobutton(rb_frame, text="Decifrar", variable=action_var, value="decrypt").pack(side="left")

        if cipher_type == "Vigenère":
            cmd = self.run_vigenere
        else:
            cmd = lambda ct=cipher_type, ke=key_entry, ie=input_entry, oe=output_entry, av=action_var: self.run_cipher(ct, ke, ie, oe, av)

        ttk.Button(content, text="Executar", command=cmd).grid(row=key_row+4, column=1, pady=10)

        log_box = tk.Text(content, height=10, width=90, bg="#2d2d2d", fg="#ffffff", insertbackground="white")
        log_box.grid(row=key_row+5, column=0, columnspan=3, padx=10, pady=10)
        try:
            log_box.config(state="disabled")
        except Exception:
            pass

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

    def browse_file(self, entry):
        """Show an open-file dialog and put the chosen path into `entry`.

        The function preserves the Entry widget's previous state (for
        example `readonly`) by temporarily enabling it if needed.

        Args:
            entry: A ttk.Entry (or similar) where the selected path will be
                   inserted.
        """

        path = filedialog.askopenfilename()
        if not path:
            return

        # First try to set a bound textvariable (works even when readonly)
        try:
            tv_name = entry.cget('textvariable')
            if tv_name:
                try:
                    entry.setvar(tv_name, path)
                    print(f"browse_file: set textvariable {tv_name} -> {path}")
                    return
                except Exception:
                    pass
        except Exception:
            pass

        # If this is a ttk widget, prefer using the state() API to toggle
        # readonly state instead of entry.config which may not work on all
        # ttk implementations.
        try:
            state_fn = getattr(entry, 'state', None)
            if callable(state_fn):
                try:
                    prev_states = list(entry.state())
                except Exception:
                    prev_states = []
                # temporarily remove readonly if present
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

        # Fallback for plain tk.Entry or other widgets
        prev_state = None
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

    def save_file(self, entry):
        """Show a save-as dialog and put the chosen path into `entry`.

        Mirrors `browse_file` behavior but uses a save dialog and defaults to
        a `.txt` extension. Preserves the Entry's prior widget state.

        Args:
            entry: A ttk.Entry (or similar) where the selected save path will be
                   inserted.
        """

        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if not path:
            return

        # Prefer setting the bound variable directly when available
        try:
            tv_name = entry.cget('textvariable')
            if tv_name:
                try:
                    entry.setvar(tv_name, path)
                    print(f"save_file: set textvariable {tv_name} -> {path}")
                    return
                except Exception:
                    pass
        except Exception:
            pass

        # Use ttk Entry state API when possible
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

        # Fallback for plain tk.Entry
        prev_state = None
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

    def log_message(self, box, message):
        """Append a single-line message to the GUI log `box`.

        The method makes the text widget temporarily writable, inserts the
        message followed by a newline, then restores the widget to
        read-only. Errors are ignored to keep the UI robust.

        Args:
            box: A tk.Text widget used for logging.
            message: The message string to append.
        """

        try:
            box.config(state="normal")
            box.insert(tk.END, message + "\n")
            box.config(state="disabled")
            box.see(tk.END)
        except Exception:
            pass

    def center_window(self):
        """Center the main window on the screen.

        This computes the desired geometry and updates the window position.
        Works even if the window manager hasn't fully realized the window yet.
        """
        self.root.update_idletasks()

        width = self.root.winfo_width()
        height = self.root.winfo_height()
        if width <= 1 or height <= 1:
            geom = self.root.geometry()
            try:
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
