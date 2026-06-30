# AI Profiler v1.0.0

**Perfilador de hardware para recomendar modelos de IA ejecutables localmente.**

Analiza tu PC (RAM, VRAM, CPU, disco, GPU) y te dice qué LLMs puedes ejecutar sin necesidad de internet ni servicios cloud.

---

## Tabla de Contenidos

- [Características](#características)
- [Capturas de Pantalla](#capturas-de-pantalla)
- [Requisitos](#requisitos)
- [Instalación Rápida](#instalación-rápida)
- [Uso](#uso)
  - [Interfaz Gráfica (GUI)](#interfaz-gráfica-gui)
  - [Línea de Comandos (CLI)](#línea-de-comandos-cli)
- [Guía de la Interfaz](#guía-de-la-interfaz)
  - [Pestaña Búsqueda](#pestaña-búsqueda)
  - [Pestaña Análisis](#pestaña-análisis)
  - [Pestaña Configuración](#pestaña-configuración)
- [Internacionalización (i18n)](#internacionalización-i18n)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Integración con Ollama](#integración-con-ollama)
- [Solución de Problemas](#solución-de-problemas)
- [Licencia](#licencia)

---

## Características

| Característica | Descripción |
| :--- | :--- |
| **Perfilado automático de hardware** | Detecta CPU, RAM, GPU (NVIDIA vía NVML, fallback WMI/lspci), almacenamiento |
| **Recomendaciones inteligentes** | Compara requisitos de modelos vs hardware y sugiere la mejor cuantización (int4, int8, fp16) |
| **Escaneo multi-fuente** | Busca modelos desde HuggingFace API, VRAM.io y Ollama (local) |
| **Escaneo dinámico** | Consulta modelos populares de texto en HuggingFace sin lista fija — el límite es configurable |
| **Base de datos local SQLite** | Almacena metadatos y requisitos de modelos para funcionar sin conexión |
| **Doble click → Ollama** | Genera el comando `ollama run ...` para cualquier modelo compatible |
| **Detección de casos de uso** | Evalua si un modelo sirve para tareas técnicas, procesamiento de imágenes (visión) y audio/voz |
| **Interfaz oscura tipo terminal** | GUI Tkinter con tema oscuro y tipografía monoespaciada |
| **CLI incorporado** | Misma funcionalidad desde terminal para scripting |
| **Multilenguaje** | Español (predeterminado), Inglés, Chino, Alemán, Francés, Noruego, Neerlandés |
| **Configuración persistente** | Guarda preferencias (idioma, límite de escaneo, fuentes activas) en `data/config.json` |
| **Exportación JSON** | Guarda resultados de compatibilidad para documentación o análisis posterior |

---

## Requisitos

### Hardware Mínimo
- 4 GB RAM
- 2 núcleos CPU
- 100 MB disco (más para almacenar modelos en DB)
- GPU opcional

### Software
- Python 3.10, 3.11, 3.12
- Windows 10+, Linux, macOS 11+
- pip y virtualenv (recomendado)

---

## Instalación Rápida

```bash
# 1. Clonar o copiar el proyecto
git clone https://github.com/jgarvidsson/ai_profiler.git
cd ai_profiler

# 2. Crear entorno virtual
python -m venv .venv

# 3. Activar entorno
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Ejecutar
# GUI:
python run_gui.py
# CLI:
python src/main.py
```

---

## Uso

### Interfaz Gráfica (GUI)

```bash
python run_gui.py
```

Abre una ventana de 1200×960px con tres pestañas y una barra de estado inferior que muestra el número de modelos y la fecha de última actualización.

### Línea de Comandos (CLI)

```bash
python src/main.py
```

Ejecuta el perfilado de hardware, busca modelos compatibles y muestra un informe formateado en la terminal.

---

## Guía de la Interfaz

### Pestaña Búsqueda

1. **Buscar por término** — Escribe un término (ej. "coder", "llama") y presiona Enter o clic en Buscar. Consulta HuggingFace API y muestra resultados con descargas y likes.
2. **Obtener modelo específico** — Introduce el ID completo (ej. `meta-llama/Llama-3-8B`) y clic en Obtener. Muestra detalles y requisitos de VRAM.
3. **Rastrear modelos externos** — Escanea dinámicamente las fuentes activas (HuggingFace, VRAM.io, Ollama) y añade automáticamente modelos nuevos a la DB. El límite de modelos por fuente se configura en Ajustes. Puedes detener el proceso en cualquier momento con el botón Detener; los modelos ya escaneados se conservan.
4. **Importar todos** — Descarga metadatos de una lista fija de 15 modelos populares predefinidos.

El botón **Agregar a DB** guarda el modelo seleccionado en la base de datos local para su uso sin conexión.

### Pestaña Análisis

1. **Rastrear Compatibles** — Compara todos los modelos en DB contra tu hardware actual y muestra solo los que pueden ejecutarse.
2. **Tabla de resultados** — Muestra modelo, parámetros, precisión recomendada, RAM/VRAM necesaria, y si soporta tareas técnicas y de visión.
3. **Doble click** en cualquier modelo — Abre un diálogo con el comando `ollama run <modelo>` listo para copiar al portapapeles.
4. **Exportar JSON** — Guarda los resultados como archivo JSON para documentación.
5. Las **tarjetas de hardware** en la parte superior muestran RAM total/disponible, VRAM, CPU y disco.
6. La ventana siempre es lo bastante alta para que los botones inferiores sean visibles.

### Pestaña Configuración

#### Fuentes de datos
- **Límite de búsqueda** — Número máximo de modelos a escanear por fuente (10–500, predeterminado 100).
- **Fuentes activas** — Activa/desactiva HuggingFace, VRAM.io y Ollama.
- **URLs** — Edita las URLs de cada fuente (útil para proxies o APIs alternativas).

#### Idioma
- Selecciona entre Español, Inglés, Chino, Alemán, Francés, Noruego y Neerlandés.
- El cambio es inmediato y persiste entre sesiones.

#### Base de Datos
- Muestra el número de modelos almacenados.
- **Resetear DB** — Borra todos los modelos y recarga los 13 predefinidos.

#### Registros
- Abre el archivo `data/scan_errors.txt` con el visor predeterminado del sistema.

#### Acerca de
- Información de versión, descripción, tecnologías y licencia.

---

## Internacionalización (i18n)

Todos los textos visibles en la GUI y CLI se leen de archivos JSON en `languages/`. Cada clave se invoca con `lang.get("clave")` y el resultado se usa directamente en etiquetas, botones y mensajes.

### Detección automática del idioma del sistema
Al iniciar por primera vez, la app detecta el locale del sistema (`locale.getdefaultlocale()` o variable `$LANG`). Si el idioma detectado tiene un archivo JSON en `languages/`, se carga automáticamente. Si no, se usa Español (`es`).

### Cómo añadir un idioma
1. Copia `languages/es.json` como `languages/xx.json` (donde `xx` es el código ISO del idioma).
2. Traduce los valores (no las claves).
3. **No hay que modificar nada más** — `LanguageManager.get_available_languages()` escanea el directorio y muestra el nuevo idioma automáticamente en la pestaña Configuración.

### Repositorio de traducciones
Para colaborar con nuevas traducciones o actualizar las existentes, visita:
**github.com/jgarvidsson/lenguages/tree/main/ia_profiler/1.0**
(Disponible como enlace en la pestaña Acerca de de la aplicación.)

> El repositorio de idiomas es independiente del repositorio de la aplicación.  
> Puede ser privado; la app solo necesita el acceso directo para que los colaboradores sepan dónde contribuir.

### Fallback
Si un archivo de idioma no existe o una clave no se encuentra en él, se devuelve el nombre de la clave como texto visible, garantizando que la aplicación nunca se rompa por falta de traducción.

---

## Estructura del Proyecto

```
ai_profiler/
├── run_gui.py                 # Entry point de la GUI (añade src/ al path)
├── setup.py                   # Instalación como paquete
├── requirements.txt           # Dependencias Python
├── README.md                  # Este archivo
├── AGENTS.md                  # Instrucciones para asistentes IA
│
├── src/                       # Núcleo de la aplicación
│   ├── main.py                # Entry point CLI
│   ├── hardware_profiler.py   # Detección de hardware
│   ├── model_database.py      # SQLite: modelos, requisitos, compatibilidad
│   ├── model_fetcher.py       # Consulta APIs externas (HF, VRAM.io, Ollama)
│   ├── recommendation_engine.py # Compara hardware vs modelos
│   ├── language_manager.py    # Carga archivos de idioma
│   └── settings_manager.py    # Configuración persistente (data/config.json)
│
├── gui/                       # Interfaz gráfica Tkinter
│   ├── app.py                 # Ventana principal, notebook, footer
│   ├── styles.py              # Colores, fuentes, tema oscuro
│   ├── tabs/
│   │   ├── search_tab.py      # Pestaña de búsqueda/escaneo
│   │   ├── display_tab.py     # Pestaña de análisis/resultados
│   │   └── config_tab.py      # Pestaña de configuración
│   └── widgets/               # Widgets personalizados (futuro)
│       └── __init__.py
│
├── languages/                 # Archivos de traducción JSON
│   ├── es.json                # Español
│   ├── en.json                # Inglés
│   ├── cn.json                # Chino
│   ├── de.json                # Alemán
│   ├── fr.json                # Francés
│   ├── no.json                # Noruego
│   └── nl.json                # Neerlandés
│
├── data/                      # Datos generados en tiempo de ejecución
│   ├── models.db              # SQLite (auto-creado)
│   ├── config.json            # Configuración persistente (auto-creado)
│   └── scan_errors.txt        # Log de errores de escaneo (auto-creado)
│
├── docs/                      # Documentación adicional
│   ├── README.md
│   ├── INSTALLATION.md
│   └── AI PROFILER.md
│
├── scripts/                   # Scripts auxiliares
├── tests/                     # Tests unitarios
└── structure.txt              # Esquema de archivos
```

---

## Integración con Ollama

### Detección automática
Si Ollama está instalado y accesible desde la línea de comandos, activa la fuente "Ollama (local)" en Configuración → Fuentes de datos. El escáner ejecutará `ollama list` e incluirá los modelos locales en el catálogo.

### Comando de descarga
En la pestaña Análisis, haz **doble click** sobre cualquier modelo compatible. Se abrirá un diálogo con el comando:

```
ollama run <nombre_modelo>
```

Un clic en **Copiar comando** lo copia al portapapeles.

### Mapeo de nombres
La aplicación intenta mapear automáticamente nombres de HuggingFace a nombres de Ollama (ej. `meta-llama/Llama-3-8B` → `llama3`, `google/gemma-2b` → `gemma2:2b`). Si no encuentra una correspondencia, usa el nombre del modelo en minúsculas.

---

## Solución de Problemas

| Problema | Causa | Solución |
| :--- | :--- | :--- |
| "No se pudieron obtener modelos" | APIs externas no responden | Activa la fuente "Ollama (local)" o reduce el límite de escaneo |
| Error 503 / Timeout en escaneo | VRAM.io temporalmente caído | La app usa estimación local como fallback; los modelos se añaden igual |
| No detecta GPU NVIDIA | nvidia-ml-py no instalado o sin driver | Instala `pip install nvidia-ml-py` o verifica drivers NVIDIA |
| Ventana muy pequeña | Resolución baja | La app fuerza mínimo 1000×700; redimensiona manualmente |
| El escaneo es lento | Límite alto + APIs lentas | Reduce el límite en Configuración → Fuentes de datos |
| Modelo no aparece en resultados | No está en DB o no es compatible con tu hardware | Usa la pestaña Búsqueda para añadirlo o reduce requisitos vía cuantización |

---

## Licencia

MIT License. Ver archivo `LICENSE` (si existe) para detalles completos.

---

*Documento generado el 30 de Junio de 2026.*  
*AI Profiler Development Team — Aurora T. & J.G. Arvidsson*
