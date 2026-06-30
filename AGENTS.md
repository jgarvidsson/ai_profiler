<!-- fullWidth: false tocVisible: false tableWrap: true -->
# AGENTS.md — Guía para Asistentes IA

## Identidad

- **1st**: Aurora T. (Rol: Desarrolladora Junior / Asistente de Programación)
- **2n:** J.G. Arvidsson (Rol: Arquitecto de Software / Tech Lead)
- **Proyecto**: AI Profiler — Perfilador de hardware para recomendar modelos de IA locales
- **Versión actual**: 1.0.0

## Responsabilidades

### Actualización del manual

Cada vez que se introduzca un cambio significativo (nueva funcionalidad, cambio de flujo, nueva dependencia, cambio en la estructura de archivos), **debes actualizar `README.md`** para reflejarlo. Esto incluye:

- Nuevos módulos o componentes
- Cambios en la interfaz de usuario (nuevas pestañas, botones, diálogos)
- Nuevas fuentes de datos o integraciones
- Cambios en requisitos de hardware/software
- Nuevas opciones de configuración

### Internacionalización (i18n)

- **Todos los textos visibles** (labels, botones, mensajes, títulos) deben cargarse desde el `LanguageManager` usando `lang.get("clave")`.
- **Nunca uses cadenas literales** en español u otros idiomas directamente en el código. Siempre pasa por el archivo de idioma.
- **Lista dinámica de idiomas**: `LanguageManager.get_available_languages()` escanea `languages/*.json` — no hay lista hardcodeada. Para añadir un idioma, basta con crear un nuevo archivo JSON.
- **Idioma predeterminado**: Detección automática del locale del sistema (`locale.getdefaultlocale()` + `$LANG`). Si no se encuentra, fallback a Español (`es`).
- **Fallback**: Si una clave no existe en el archivo de idioma, `LanguageManager.get()` devuelve el nombre de la clave como texto, para que la app nunca se rompa por falta de traducción.
- Al añadir una nueva cadena visible, agrégala a TODOS los archivos JSON en `languages/` (al menos con una traducción aproximada; si no sabes el idioma, deja una nota).
- **Repositorio de idiomas**: `https://github.com/jgarvidsson` — botón en About que abre el perfil para colaborar con traducciones.

### Convenios de código

- Los imports de módulos del proyecto usan path absoluto añadiendo `src/` al `sys.path` en cada entry point (`run_gui.py` y `src/main.py`). Los módulos internos usan imports simples (`from model_database import ModelDatabase`).
- Los archivos de la GUI están en `gui/tabs/`.
- Los estilos (colores, fuentes) están en `gui/styles.py`.
- La base de datos SQLite se crea/abre en `data/models.db`.
- La configuración persistente se guarda en `data/config.json`.
- No uses commas, emojis ni comentarios en el código a menos que sean necesarios para la funcionalidad.

## Estado del proyecto

### Implementado

- Perfilado de hardware (CPU, RAM, GPU vía NVML/WMI/lspci, disco)
- Base de datos SQLite con 13 modelos precargados, escaneo dinámico multi-fuente
- Recomendación de modelos con evaluación de casos de uso (técnica, visión)
- GUI Tkinter con 3 pestañas (Búsqueda, Análisis, Configuración)
- CLI funcional (`python src/main.py`)
- Escaneo de modelos desde HuggingFace API, VRAM.io, Ollama (local)
- Fallback de estimación local cuando VRAM.io falla (silencioso)
- Doble click → diálogo con comando `ollama run ...` y copia al portapapeles
- Configuración persistente (idioma, límite de escaneo, fuentes activas, URLs)
- Internacionalización (7 idiomas, fallback a clave)
- Exportación JSON de resultados
- Botón Detener en escaneos con resumen parcial

### Pendiente / Trabajo futuro

- Traducciones completas en archivos `cn.json`, `de.json`, `fr.json`, `no.json`, `nl.json` (algunas claves nuevas pueden no estar traducidas)
- Soporte para AMD GPUs
- Integración con LM Studio
- API REST para integración
- Tests unitarios más completos

## Notas importantes

- La app funciona completamente offline excepto para la búsqueda opcional de modelos.
- VRAM.io suele dar 503; el fallback de estimación local es el flujo normal.
- `_estimate_params()` busca patrones de mayor a menor longitud (32B antes que 2B).
- La ventana GUI mide 1200×960 por defecto, mínimo 1000×700.
- El entry point de GUI es `run_gui.py`; el de CLI es `src/main.py`.
- Al crear nuevos componentes de GUI, sigue el patrón existente: hereda de `ttk.Frame`, usa `style='Terminal.TFrame'`, y recibe `db`, `lang`, `settings` según sea necesario.