"""
Estilos y configuración visual para la GUI.
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path

class Colors:
    """Paleta de colores estilo terminal CLI."""
    # Fondo y texto
    BG = '#0a0a0a'  # Negro profundo
    BG_ALT = '#111111'  # Negro alternativo
    TEXT = '#00ff41'  # Verde matrix
    TEXT_DIM = '#008f11'  # Verde oscuro
    TEXT_BRIGHT = '#66ff99'  # Verde brillante
    TEXT_RED = '#ff0033'  # Rojo para errores
    TEXT_YELLOW = '#ffff00'  # Amarillo para advertencias
    TEXT_CYAN = '#00ffff'  # Cian para destacar
    
    # Bordes y widgets
    BORDER = '#00ff41'
    BORDER_DIM = '#006600'
    SELECT_BG = '#003300'
    SELECT_FG = '#00ff41'
    
    # Progreso
    PROGRESS_BG = '#001a00'
    PROGRESS_FG = '#00ff41'

class Fonts:
    """Configuración de fuentes estilo terminal."""
    # Tamaños
    SIZE_SMALL = 10
    SIZE_NORMAL = 12
    SIZE_LARGE = 14
    SIZE_TITLE = 18
    
    # Familias - Usar nombres válidos para tkinter
    FAMILY = "Courier"  # Cambiado de "Courier New" a "Courier"
    # Alternativas: "Consolas", "Lucida Console", "Monospace"
    
    # Estilos combinados
    TITLE = (FAMILY, SIZE_TITLE, "bold")
    HEADER = (FAMILY, SIZE_LARGE, "bold")
    NORMAL = (FAMILY, SIZE_NORMAL)
    SMALL = (FAMILY, SIZE_SMALL)
    BOLD = (FAMILY, SIZE_NORMAL, "bold")

def configure_styles():
    """Configura los estilos de ttk para toda la aplicación."""
    style = ttk.Style()
    
    # Tema oscuro
    style.theme_use('clam')
    
    # Colores base
    style.configure('.',
        background=Colors.BG,
        foreground=Colors.TEXT,
        fieldbackground=Colors.BG_ALT,
        borderwidth=1,
        relief='flat'
    )
    
    # TFrame
    style.configure('Terminal.TFrame',
        background=Colors.BG,
        relief='flat',
        borderwidth=0
    )
    
    # TLabel
    style.configure('Terminal.TLabel',
        background=Colors.BG,
        foreground=Colors.TEXT,
        font=Fonts.NORMAL
    )
    
    style.configure('Terminal.Title.TLabel',
        background=Colors.BG,
        foreground=Colors.TEXT_BRIGHT,
        font=Fonts.TITLE
    )
    
    style.configure('Terminal.Header.TLabel',
        background=Colors.BG,
        foreground=Colors.TEXT_CYAN,
        font=Fonts.HEADER
    )
    
    style.configure('Terminal.Subtitle.TLabel',
        background=Colors.BG,
        foreground=Colors.TEXT_DIM,
        font=Fonts.BOLD
    )
    
    # TButton
    style.configure('Terminal.TButton',
        background=Colors.BG_ALT,
        foreground=Colors.TEXT,
        borderwidth=1,
        relief='raised',
        focusthickness=0,
        padding=8,
        font=Fonts.NORMAL
    )
    style.map('Terminal.TButton',
        background=[('active', Colors.BG)],
        foreground=[('active', Colors.TEXT_BRIGHT)],
        relief=[('pressed', 'sunken')]
    )
    
    # TCheckbutton
    style.configure('Terminal.TCheckbutton',
        background=Colors.BG,
        foreground=Colors.TEXT,
        font=Fonts.NORMAL,
        borderwidth=0,
        focusthickness=0,
        padding=4
    )
    style.map('Terminal.TCheckbutton',
        background=[('active', Colors.BG_ALT)],
        foreground=[('active', Colors.TEXT_BRIGHT)]
    )

    # TSpinbox
    style.configure('Terminal.TSpinbox',
        fieldbackground=Colors.BG_ALT,
        foreground=Colors.TEXT,
        background=Colors.BG_ALT,
        borderwidth=1,
        relief='solid',
        font=Fonts.NORMAL,
        arrowcolor=Colors.TEXT
    )

    # TRadiobutton
    style.configure('Terminal.TRadiobutton',
        background=Colors.BG,
        foreground=Colors.TEXT,
        font=Fonts.NORMAL,
        borderwidth=0,
        focusthickness=0,
        padding=4
    )
    style.map('Terminal.TRadiobutton',
        background=[('active', Colors.BG_ALT)],
        foreground=[('active', Colors.TEXT_BRIGHT)]
    )

    # TEntry
    style.configure('Terminal.TEntry',
        fieldbackground=Colors.BG_ALT,
        foreground=Colors.TEXT,
        insertcolor=Colors.TEXT,
        borderwidth=1,
        relief='solid',
        padding=6,
        font=Fonts.NORMAL
    )
    
    # TCombobox
    style.configure('Terminal.TCombobox',
        fieldbackground=Colors.BG_ALT,
        foreground=Colors.TEXT,
        background=Colors.BG_ALT,
        borderwidth=1,
        relief='solid',
        padding=6,
        font=Fonts.NORMAL
    )
    style.map('Terminal.TCombobox',
        fieldbackground=[('readonly', Colors.BG_ALT)],
        foreground=[('readonly', Colors.TEXT)]
    )
    
    # TNotebook (Pestañas)
    style.configure('Terminal.TNotebook',
        background=Colors.BG,
        borderwidth=1,
        relief='flat'
    )
    style.configure('Terminal.TNotebook.Tab',
        background=Colors.BG_ALT,
        foreground=Colors.TEXT_DIM,
        padding=[12, 6],
        font=Fonts.BOLD
    )
    style.map('Terminal.TNotebook.Tab',
        background=[('selected', Colors.BG)],
        foreground=[('selected', Colors.TEXT_BRIGHT)]
    )
    
    # TProgressbar
    style.configure('Terminal.Horizontal.TProgressbar',
        background=Colors.PROGRESS_FG,
        troughcolor=Colors.PROGRESS_BG,
        borderwidth=0,
        thickness=20
    )
    
    # Treeview (para listados)
    style.configure('Terminal.Treeview',
        background=Colors.BG_ALT,
        foreground=Colors.TEXT,
        fieldbackground=Colors.BG_ALT,
        borderwidth=0,
        font=Fonts.SMALL
    )
    style.map('Terminal.Treeview',
        background=[('selected', Colors.SELECT_BG)],
        foreground=[('selected', Colors.SELECT_FG)]
    )
    
    # Scrollbar
    style.configure('Terminal.Vertical.TScrollbar',
        background=Colors.BG_ALT,
        troughcolor=Colors.BG,
        borderwidth=0,
        arrowsize=12
    )