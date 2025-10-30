#!/usr/bin/env python3
"""
Elegant GUI for file encryption/decryption.
Place this file at: src/gui.py
It expects your cipher implementations to live in the `scripts` package:
  scripts/aes.py, scripts/des.py, scripts/vigenere.py, scripts/playfair.py
Each module should expose at least these functions (examples):
  encrypt_file(input_path, output_path, **kwargs)
  decrypt_file(input_path, output_path, **kwargs)

If a cipher module is missing the GUI will show an informative error message but the GUI will still run.

Dependencies: PyQt6
  pip install PyQt6

This GUI is written to be self-contained and easy to adapt.
"""

import sys
import traceback
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QTabWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QComboBox,
    QRadioButton,
    QButtonGroup,
    QProgressBar,
    QGroupBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def safe_import(module_name: str):
    """Try to import a cipher module from `scripts`. Returns module or None and error."""
    try:
        full = f"scripts.{module_name}"
        mod = __import__(full, fromlist=["*"])  # dynamic import
        return mod, None
    except Exception as e:
        return None, e


class WorkerThread(QThread):
    """Run encryption/decryption in background to keep UI responsive."""

    finished = pyqtSignal(bool, str)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self.func(*self.args, **self.kwargs)
            self.finished.emit(True, "Completed successfully")
        except Exception as e:
            self.finished.emit(False, str(e) + "\n" + traceback.format_exc())


class CipherTab(QWidget):
    def __init__(self, cipher_name: str, options: dict = None):
        super().__init__()
        self.cipher_name = cipher_name
        self.options = options or {}
        self.module, self.err = safe_import(cipher_name.lower())
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()

        # File selectors
        file_layout = QHBoxLayout()
        self.input_path = QLineEdit()
        self.input_btn = QPushButton("Selecionar ficheiro")
        self.input_btn.clicked.connect(self.select_input)
        file_layout.addWidget(QLabel("Ficheiro input:"))
        file_layout.addWidget(self.input_path)
        file_layout.addWidget(self.input_btn)
        layout.addLayout(file_layout)

        out_layout = QHBoxLayout()
        self.output_path = QLineEdit()
        self.output_btn = QPushButton("Salvar como...")
        self.output_btn.clicked.connect(self.select_output)
        out_layout.addWidget(QLabel("Ficheiro output:"))
        out_layout.addWidget(self.output_path)
        out_layout.addWidget(self.output_btn)
        layout.addLayout(out_layout)

        # Key / params
        params_box = QGroupBox("Parâmetros")
        params_layout = QVBoxLayout()

        # Add specific option widgets based on options map
        self.param_widgets = {}
        for k, cfg in self.options.items():
            row = QHBoxLayout()
            row.addWidget(QLabel(cfg.get("label", k) + ":"))
            if cfg["type"] == "text":
                w = QLineEdit()
            elif cfg["type"] == "combo":
                w = QComboBox()
                w.addItems(cfg.get("values", []))
            else:
                w = QLineEdit()
            w.setToolTip(cfg.get("tooltip", ""))
            row.addWidget(w)
            params_layout.addLayout(row)
            self.param_widgets[k] = w

        params_box.setLayout(params_layout)
        layout.addWidget(params_box)

        # Encrypt/Decrypt radio buttons
        ops_layout = QHBoxLayout()
        self.encrypt_radio = QRadioButton("Encriptar")
        self.decrypt_radio = QRadioButton("Desencriptar")
        self.encrypt_radio.setChecked(True)
        group = QButtonGroup(self)
        group.addButton(self.encrypt_radio)
        group.addButton(self.decrypt_radio)
        ops_layout.addWidget(self.encrypt_radio)
        ops_layout.addWidget(self.decrypt_radio)
        layout.addLayout(ops_layout)

        # Run button + progress
        run_layout = QHBoxLayout()
        self.run_btn = QPushButton("Executar")
        self.run_btn.clicked.connect(self.execute)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # busy indicator when running
        self.progress.setVisible(False)
        run_layout.addWidget(self.run_btn)
        run_layout.addWidget(self.progress)
        layout.addLayout(run_layout)

        # Log
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setFixedHeight(140)
        layout.addWidget(self.log)

        # If module missing, show top warning
        if self.module is None:
            note = QLabel(
                f"Módulo de cifra '{self.cipher_name}' não encontrado em scripts/.\n"
                "Por favor coloque um ficheiro scripts/{name}.py com funções encrypt_file/decrypt_file"
            )
            note.setStyleSheet("color: darkred; font-weight: bold;")
            layout.insertWidget(0, note)

        self.setLayout(layout)

    def select_input(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar ficheiro")
        if path:
            self.input_path.setText(path)
            # If output empty set default
            if not self.output_path.text():
                self.output_path.setText(path + (".enc" if self.encrypt_radio.isChecked() else ".dec"))

    def select_output(self):
        path, _ = QFileDialog.getSaveFileName(self, "Salvar como")
        if path:
            self.output_path.setText(path)

    def _gather_kwargs(self):
        kw = {}
        for k, widget in self.param_widgets.items():
            if isinstance(widget, QLineEdit):
                kw[k] = widget.text()
            elif isinstance(widget, QComboBox):
                kw[k] = widget.currentText()
            else:
                kw[k] = widget.text()
        return kw

    def execute(self):
        inp = self.input_path.text().strip()
        out = self.output_path.text().strip()
        if not inp or not out:
            QMessageBox.warning(self, "Faltam ficheiros", "Por favor selecione ficheiro input e output.")
            return

        if self.module is None:
            QMessageBox.critical(
                self,
                "Módulo em falta",
                f"O módulo para {self.cipher_name} não está disponível: {self.err}",
            )
            return

        kwargs = self._gather_kwargs()
        op = "encrypt_file" if self.encrypt_radio.isChecked() else "decrypt_file"
        if not hasattr(self.module, op):
            QMessageBox.critical(
                self,
                "Função em falta",
                f"O módulo {self.cipher_name} não implementa {op}()",
            )
            return

        func = getattr(self.module, op)

        # Start worker thread
        self.run_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.log.append(f"A iniciar {op} com {self.cipher_name}...\nInput: {inp}\nOutput: {out}\nParams: {kwargs}")

        self.worker = WorkerThread(func, inp, out, **kwargs)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_finished(self, ok: bool, message: str):
        self.run_btn.setEnabled(True)
        self.progress.setVisible(False)
        if ok:
            self.log.append("OK: " + message)
            QMessageBox.information(self, "Concluído", "Operação concluída com sucesso.")
        else:
            self.log.append("ERRO: " + message)
            QMessageBox.critical(self, "Erro", "Ocorreu um erro: " + message)


class HomeTab(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        h = QLabel(
            "<h2>Bem-vindo à aplicação de cifra</h2>"
            "<p>Use as abas para escolher a cifra. Se os módulos estiverem na pasta <code>scripts/</code>,"
            "o botão Executar irá chamar as funções <code>encrypt_file</code> / <code>decrypt_file</code> do módulo correspondente.</p>"
        )
        h.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(h)

        tips = QLabel(
            "<ul>"
            "<li>Arraste um ficheiro para a caixa de input para preencher o caminho (não implementado por arrastar — por favor usar selecionar).</li>"
            "<li>Parâmetros específicos de cada cifra aparecem na respetiva aba.</li>"
            "<li>Esta GUI usa PyQt6. Instale com <code>pip install PyQt6</code>.</li>"
            "</ul>"
        )
        tips.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(tips)

        self.recent = QTextEdit()
        self.recent.setReadOnly(True)
        self.recent.setPlainText("Histórico de operações aparecerá aqui.")
        layout.addWidget(self.recent)

        self.setLayout(layout)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cifrador — GUI elegante")
        self.resize(900, 640)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        tabs = QTabWidget()

        home = HomeTab()
        tabs.addTab(home, "Início")

        # AES tab options
        aes_opts = {
            "key": {"label": "Chave (hex/str)", "type": "text", "tooltip": "Chave ou passphrase"},
            "mode": {"label": "Modo", "type": "combo", "values": ["ECB", "CBC", "CFB", "OFB", "GCM"]},
        }
        tabs.addTab(CipherTab("AES", aes_opts), "AES")

        # DES tab options
        des_opts = {
            "key": {"label": "Chave (56-bit)", "type": "text", "tooltip": "Chave para DES"},
            "mode": {"label": "Modo", "type": "combo", "values": ["ECB", "CBC", "CFB", "OFB"]},
        }
        tabs.addTab(CipherTab("DES", des_opts), "DES")

        # Viginère
        vig_opts = {
            "key": {"label": "Chave (texto)", "type": "text", "tooltip": "Chave alfabética para Viginère"},
        }
        tabs.addTab(CipherTab("Viginere", vig_opts), "Viginère")

        # Playfair
        pf_opts = {
            "key": {"label": "Chave (texto)", "type": "text", "tooltip": "Chave para Playfair"},
        }
        tabs.addTab(CipherTab("Playfair", pf_opts), "Playfair")

        layout.addWidget(tabs)
        self.setLayout(layout)


def main():
    app = QApplication(sys.argv)
    # Optional: nicer default font/size
    app.setStyleSheet(
        "QWidget { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11pt; }"
        "QGroupBox { margin-top: 12px; }"
        "QTabWidget::pane { border: 1px solid #ddd; }")

    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
