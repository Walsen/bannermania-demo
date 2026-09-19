# Implementation Plan: Aplicación de Escritorio BannerMania

## Overview

Este plan convierte `design.md` en pasos de código incrementales. Cada tarea
se apoya en la anterior y termina con el cableado de todo el sistema en
`MainWindow`. Se sigue TDD (rojo → verde → refactor): las subtareas de
prueba marcadas con `*` son opcionales de omitir para una entrega rápida,
pero cuando se ejecutan deben escribirse **antes** de la implementación que
validan, confirmando que fallan, y solo entonces implementar el código
mínimo para que pasen (sección "Test-Driven Development" de las prácticas
de ingeniería del proyecto). Las 18 propiedades de corrección de
`design.md` se prueban con Hypothesis (`@given`, `@settings(max_examples=100)`
como mínimo), una función de prueba por propiedad, con el comentario de
referencia `# Feature: desktop-app, Property {n}: {enunciado}`.

Decisión de ubicación de archivos (no explicitada literalmente en
`design.md`, que usa rutas abreviadas como `desktop/rendering_port.py`):
el nuevo código de escritorio vive bajo `src/bannermania_demo/desktop/`,
como paquete hermano de `src/bannermania_demo/engine.py`, para quedar
instalable junto al resto de `bannermania_demo` (Single Responsibility:
`app.py` sigue siendo solo la capa Flask). Las pruebas viven bajo
`tests/desktop/`, recogidas automáticamente por la configuración existente
de pytest (`testpaths = ["tests"]`). `FakeRenderingEngine` se ubica en
`tests/desktop/fakes.py` (es un doble de prueba, no código de producción,
Interface Segregation: el paquete de producción no depende de utilidades
de prueba).

## Tasks

- [ ] 1. Preparar el proyecto para la app de escritorio
  - [ ] 1.1 Crear la estructura de paquetes `src/bannermania_demo/desktop/`,
    `src/bannermania_demo/desktop/ui/` y `tests/desktop/`, con sus
    `__init__.py` correspondientes
    - _Requirements: (infraestructura para Req 1-13)_
  - [ ] 1.2 Añadir `PySide6` a las dependencias principales de `pyproject.toml`,
    y `hypothesis` y `pyinstaller` al grupo `dev`, fijando versiones exactas
    o acotadas como el resto de dependencias del proyecto
    - _Requirements: (soporte para Req 1, 5, 9; Req 13.1)_
    - _Design: "Empaquetado" (PyInstaller); "Testing Strategy" (Hypothesis)_

- [ ] 2. Extraer el Motor de Renderizado a `bannermania_demo/engine.py` sin
  cambios de comportamiento
  - [ ]* 2.1 Escribir una prueba en `tests/test_engine.py` que falle porque
    `bannermania_demo.engine` todavía no existe: debe exponer
    `FONT_CANDIDATES`, `EFFECTS`, `PATTERNS`, `BORDERS`, `MOTIONS`,
    `available_fonts`, `resolve_font_path`, `load_font`, `hex_to_rgb`,
    `rainbow_color`, `shift_hue`, `lerp`, `font_size_of`, `measure`,
    `paint_background`, `draw_border`, `draw_text_effect`, `render_banner`,
    `char_color`, `draw_glyph_tile`, `render_scroll_gif`
    - Confirmar que la prueba falla (rojo) antes de continuar
    - _Requirements: 1.2_
  - [ ] 2.2 Mover, sin modificar su comportamiento ni sus firmas, el código
    listado arriba desde `app.py` a `src/bannermania_demo/engine.py`;
    actualizar `app.py` para importar esos nombres desde
    `bannermania_demo.engine` (re-exportación), de forma que
    `tests/test_app.py` siga pasando sin modificarse
    - _Requirements: 1.2_
    - _Design: "Extracción del motor (requisito previo de diseño)"_

- [ ] 3. Checkpoint - Ensure all tests pass
  - Ejecutar `tests/test_app.py` y `tests/test_engine.py` completos.
  Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Modelos de datos de configuración
  - [ ]* 4.1 Escribir pruebas unitarias para `BannerConfig`, `AnimationConfig`,
    `ProjectFile`, `Notification` y `LogLevel`: construcción con valores
    válidos, inmutabilidad (`frozen=True`, intentar mutar lanza
    `FrozenInstanceError`), e igualdad estructural entre dos instancias con
    los mismos valores
  - [ ] 4.2 Implementar `BannerConfig`, `AnimationConfig`, `ProjectFile`,
    `Notification` (dataclass) y `LogLevel` (Enum) en
    `src/bannermania_demo/desktop/models.py`, exactamente como se describe
    en la sección "Data Models" de `design.md`
    - _Requirements: 4.3, 7.3, 10.1_
    - _Design: "Data Models" — `BannerConfig`, `AnimationConfig`, esquema
      JSON v1 de `ProjectFile`, `Notification`_

- [ ] 5. Puerto del motor de renderizado y dobles de prueba
  - [ ] 5.1 Definir el `Protocol` `RenderingEnginePort` en
    `src/bannermania_demo/desktop/rendering_port.py` con los métodos
    `font_catalog`, `effect_catalog`, `pattern_catalog`, `border_catalog`,
    `motion_catalog`, `render_static` y `render_animated`
    - _Requirements: 9.1, 9.2_
    - _Design: "Components and Interfaces" #2_
  - [ ]* 5.2 Escribir pruebas unitarias para `FakeRenderingEngine`: los
    catálogos configurados por el test se devuelven sin alteración, y
    `render_static`/`render_animated` pueden configurarse para lanzar una
    excepción a demanda o simular una demora controlada
  - [ ] 5.3 Implementar `FakeRenderingEngine` en `tests/desktop/fakes.py`,
    conforme a `RenderingEnginePort`, con catálogos y resultados de render
    inyectables en el constructor (Liskov Substitution: mismo contrato de
    entrada/salida que `PillowRenderingEngine`)
    - _Design: "Components and Interfaces" #2 ("Para pruebas se usa
      FakeRenderingEngine")_
  - [ ]* 5.4 Escribir la prueba de propiedad en
    `tests/desktop/test_property_catalog_fidelity.py`, usando
    `FakeRenderingEngine` con catálogos que Hypothesis varía (incluyendo
    agregar/quitar entradas entre dos consultas)
    - **Property 1: Fidelidad de catálogo**
    - **Validates: Requirements 2.4, 2.7, 3.1, 3.2, 7.1, 9.1**
  - [ ] 5.5 Implementar `PillowRenderingEngine` en
    `src/bannermania_demo/desktop/pillow_rendering_engine.py`: cada método
    delega en las funciones equivalentes de `bannermania_demo.engine` sin
    lógica adicional (Adapter), leyendo los catálogos desde las
    listas/diccionarios del módulo en cada llamada, sin copiarlos a un
    atributo propio
    - _Requirements: 9.1, 9.2_
    - _Design: "Components and Interfaces" #2_
  - [ ]* 5.6 Escribir pruebas unitarias de cableado para
    `PillowRenderingEngine`: los catálogos devueltos coinciden exactamente
    con los de `bannermania_demo.engine` en el momento de la llamada; una
    fuente/efecto/patrón/borde/modo concreto pasado a `render_static`/
    `render_animated` llega sin alteración a la función equivalente del
    motor
    - _Requirements: 2.6, 2.8, 3.3, 3.4, 7.2, 7.5, 9.2_

- [ ] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Normalizadores de entrada (`validation.py`)
  - [ ]* 7.1 Escribir la prueba de propiedad en
    `tests/desktop/test_property_blank_text_default.py` para toda cadena
    compuesta solo de espacios en blanco (incluida la vacía)
    - **Property 5: Texto en blanco usa el reemplazo predeterminado**
    - **Validates: Requirements 2.3**
  - [ ]* 7.2 Escribir la prueba de propiedad en
    `tests/desktop/test_property_text_truncation.py` para cadenas más
    largas y más cortas que el límite máximo
    - **Property 6: Truncado de texto al límite máximo**
    - **Validates: Requirements 2.1, 2.2**
  - [ ] 7.3 Implementar `normalize_text(raw, max_len, default)` en
    `src/bannermania_demo/desktop/validation.py`: recorta espacios,
    sustituye por `default` si queda en blanco, trunca a `max_len` y
    devuelve `(texto, Notification | None)`
    - _Requirements: 2.1, 2.2, 2.3_
    - _Design: "Components and Interfaces" #4_
  - [ ]* 7.4 Escribir la prueba de propiedad en
    `tests/desktop/test_property_hex_color_validation.py`, generando tanto
    hexadecimales válidos de 3/6 dígitos (con y sin "#") como cadenas
    inválidas
    - **Property 3: Validación y reemplazo de color hexadecimal**
    - **Validates: Requirements 4.1, 4.2**
  - [ ] 7.5 Implementar `normalize_hex_color(raw, field, fallback_hex)` en
    `validation.py`: acepta 3 o 6 dígitos con o sin "#", normaliza a 6
    dígitos; si no es válido, usa `fallback_hex` y produce una
    `Notification` con el nombre del campo y el valor original
    - _Requirements: 4.1, 4.2_
  - [ ]* 7.6 Escribir la prueba de propiedad en
    `tests/desktop/test_property_dimension_normalization.py` para los
    cuatro parámetros y sus límites (200-3000, 120-1200, 20-400, 12-120),
    cubriendo enteros dentro de rango, fuera de rango y valores no enteros
    - **Property 4: Normalización de parámetros numéricos con límites**
    - **Validates: Requirements 4.3, 4.4, 4.5, 7.3, 7.4**
  - [ ] 7.7 Implementar
    `normalize_dimension(raw, field, minimum, maximum, default)` en
    `validation.py`: entero dentro de rango se usa igual; entero fuera de
    rango se ajusta al límite más cercano y notifica; valor no entero usa
    `default` y notifica
    - _Requirements: 4.3, 4.4, 4.5, 7.3, 7.4_
  - [ ]* 7.8 Escribir la prueba de propiedad en
    `tests/desktop/test_property_catalog_choice_rejection.py` para valores
    fuera del catálogo vigente de patrones y de bordes
    - **Property 2: Rechazo de valor de catálogo inválido conserva el
      valor previo**
    - **Validates: Requirements 3.6, 3.7**
  - [ ] 7.9 Implementar
    `normalize_catalog_choice(raw, field, catalog, previous)` en
    `validation.py`: si `raw` pertenece a `catalog` se usa; si no,
    conserva `previous` y produce una `Notification` de error
    - _Requirements: 3.6, 3.7_

- [ ] 8. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Frontera de errores (`errors.py`)
  - [ ]* 9.1 Escribir pruebas unitarias para la jerarquía de excepciones:
    cada subtipo hereda de `BannerManiaError` (o de `ProjectFileError`
    según corresponda) y puede instanciarse con un mensaje
  - [ ] 9.2 Implementar en `src/bannermania_demo/desktop/errors.py` la
    jerarquía `BannerManiaError`, `EngineValidationError`,
    `CatalogUnavailableError`, `ProjectFileError`,
    `ProjectFileNotReadableError`, `ProjectFileSchemaError` y
    `ExportWriteError`, exactamente como en "Error Handling" de
    `design.md`
    - _Design: "Error Handling" — jerarquía de excepciones_
  - [ ]* 9.3 Escribir la prueba de propiedad en
    `tests/desktop/test_property_error_boundary.py`, envolviendo con
    `guarded_operation` una función de prueba que Hypothesis hace lanzar
    distintos tipos de excepción (conocidas y genéricas no anticipadas)
    - **Property 14: Frontera de errores no controlados**
    - **Validates: Requirements 6.2, 7.7, 10.5, 11.3**
  - [ ] 9.4 Implementar el decorador/gestor de contexto `guarded_operation`
    en `errors.py`: ejecuta la función envuelta; si lanza un tipo conocido
    (`BannerManiaError`, `OSError`, `PermissionError`) o cualquier otra
    `Exception` no anticipada, registra vía el logger recibido con nivel
    ERROR (tipo de excepción, nombre de operación, timestamp) y emite un
    mensaje saneado sin traza de pila; nunca modifica el estado de
    configuración en memoria si la operación falla; nunca usa `except:`
    desnudo
    - _Requirements: 6.2, 7.7, 10.5, 11.3, 12.2_
    - _Design: "Components and Interfaces" #7; "Error Handling" — "El
      decorador guarded_operation"_
  - [ ]* 9.5 Escribir pruebas unitarias de casos borde para
    `guarded_operation`: el mensaje saneado no contiene el nombre de la
    clase de excepción interna ni texto de traza; una operación exitosa no
    registra ningún error y devuelve el resultado normal de la función

- [ ] 10. Registro de eventos (`logging_setup.py`)
  - [ ]* 10.1 Escribir la prueba de propiedad en
    `tests/desktop/test_property_log_entry_content.py`, generando pares
    (tipo de excepción, nombre de operación) y verificando el contenido de
    la entrada registrada
    - **Property 16: Contenido de la entrada de log de error**
    - **Validates: Requirements 12.2**
  - [ ]* 10.2 Escribir la prueba de propiedad en
    `tests/desktop/test_property_log_level_mapping.py`, generando eventos
    de las tres categorías (ajuste automático, error manejado, evento
    operativo general) y verificando el nivel de severidad resultante
    - **Property 17: Correspondencia entre categoría de evento y nivel de
      log**
    - **Validates: Requirements 12.3**
  - [ ] 10.3 Implementar `configure_logging(log_path)` y
    `get_logger(name)` en `src/bannermania_demo/desktop/logging_setup.py`:
    configuración única al inicio con `RotatingFileHandler` hacia un
    archivo local, formato con timestamp/nivel/componente/mensaje, sin usar
    `print()` en ningún punto del paquete `desktop`
    - _Requirements: 12.1, 12.2, 12.3_
    - _Design: "Components and Interfaces" #8_
  - [ ]* 10.4 Escribir la prueba de propiedad en
    `tests/desktop/test_property_log_write_failure_isolation.py`,
    simulando que el manejador de archivo lanza `OSError` al escribir
    - **Property 18: Un fallo de escritura del log no interrumpe la
      operación**
    - **Validates: Requirements 12.4**
  - [ ] 10.5 Envolver el manejador de escritura de `logging_setup.py` para
    capturar `OSError` (falta de permisos o de espacio) al intentar
    escribir una entrada y descartarla sin propagar, de forma que la
    operación que originó el log se complete igual
    - _Requirements: 12.4_
    - _Design: "Components and Interfaces" #8_
  - [ ]* 10.6 Escribir pruebas de ejemplo, una por cada tipo de evento
    operativo (inicio de la app, cierre de la app, exportación PNG,
    exportación GIF, guardado de proyecto, apertura de proyecto),
    verificando que cada una se registra con nivel INFO
    - _Requirements: 12.1_

- [ ] 11. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Persistencia del Archivo de Proyecto (`project_repository.py`)
  - [ ] 12.1 Definir el `Protocol` `ProjectRepositoryPort` (`save`, `load`)
    e implementar `JsonProjectRepository.save(path, project)` en
    `src/bannermania_demo/desktop/project_repository.py`, serializando
    `ProjectFile` al esquema JSON v1 descrito en "Data Models"
    - _Requirements: 10.1_
    - _Design: "Components and Interfaces" #6; "Data Models" — esquema
      JSON v1_
  - [ ] 12.2 Implementar `JsonProjectRepository.load(path)`: valida que el
    documento sea JSON parseable y contenga los ocho parámetros con tipos
    correctos y valores dentro de los límites del motor; lanza
    `ProjectFileNotReadableError` si no se puede leer/parsear, o
    `ProjectFileSchemaError` si falta un campo, el tipo es incorrecto o un
    valor está fuera de límites; no toca ningún estado en memoria de la
    ventana
    - _Requirements: 10.2, 10.3, 10.4_
    - _Design: "Components and Interfaces" #6_
  - [ ]* 12.3 Escribir la prueba de propiedad en
    `tests/desktop/test_property_project_roundtrip.py`, usando `tmp_path`
    de pytest generado por Hypothesis, para combinaciones válidas de
    `BannerConfig`/`AnimationConfig`
    - **Property 11: Ida y vuelta del Archivo de Proyecto**
    - **Validates: Requirements 10.1, 10.2, 10.3**
  - [ ]* 12.4 Escribir la prueba de propiedad en
    `tests/desktop/test_property_project_malformed.py`, generando JSON
    inválido, JSON válido con un parámetro faltante, un tipo incorrecto, o
    un valor fuera de límites, y verificando que la configuración vigente
    (pasada como fixture) no cambia
    - **Property 12: Archivo de Proyecto malformado no altera el estado
      vigente**
    - **Validates: Requirements 10.4**
  - [ ]* 12.5 Escribir pruebas unitarias de casos borde: guardar en una
    ruta no escribible lanza `ExportWriteError`/`OSError` sin perder la
    configuración vigente en memoria
    - _Requirements: 10.5_

- [ ] 13. Servicio de aleatorización (`randomize.py`)
  - [ ]* 13.1 Escribir la prueba de propiedad en
    `tests/desktop/test_property_randomize_validity.py`, usando
    `FakeRenderingEngine` con catálogos que Hypothesis varía
    - **Property 7: Validez de la configuración aleatoria**
    - **Validates: Requirements 8.1**
  - [ ] 13.2 Implementar `RandomizeService.generate()` en
    `src/bannermania_demo/desktop/randomize.py`: lee los catálogos
    vigentes vía `RenderingEnginePort` (nunca copia propia), sortea fuente/
    efecto/patrón/borde y los cuatro colores hexadecimales, y vuelve a
    sortear el color de fondo si coincide con el color principal de texto
    (bucle acotado)
    - _Requirements: 8.1_
    - _Design: "Components and Interfaces" #5_

- [ ] 14. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 15. `ControlsPanel` y `PreviewPanel`
  - [ ] 15.1 Implementar `ControlsPanel` en
    `src/bannermania_demo/desktop/ui/controls_panel.py`: construye
    `QComboBox` para fuente/efecto/patrón/borde/modo de movimiento a
    partir de los catálogos obtenidos de `RenderingEnginePort` en el
    momento de construirse (sin listas literales de efectos/patrones/
    bordes en el código), `QLineEdit` con validador de texto, botones de
    color con `QColorDialog`, `QSpinBox` para ancho/alto/velocidad/cuadros,
    `QCheckBox` para animar/ciclo de color; emite una señal
    `config_changed` al modificarse cualquier control
    - _Requirements: 2.1, 2.4, 2.7, 3.1, 3.2, 4.1, 4.3, 7.1, 7.3, 7.5, 9.1_
    - _Design: "Components and Interfaces" #9_
  - [ ]* 15.2 Escribir pruebas unitarias de `ControlsPanel` con
    `FakeRenderingEngine`: las opciones mostradas en cada `QComboBox`
    coinciden exactamente con el catálogo del motor fake usado en la
    construcción (Req 9.1); verificar por inspección del módulo
    (`ast`/`inspect`) que `controls_panel.py` no contiene listas literales
    de nombres de efecto/patrón/borde (Req 9.2)
    - _Requirements: 9.1, 9.2_
  - [ ] 15.3 Implementar `PreviewPanel` en
    `src/bannermania_demo/desktop/ui/preview_panel.py`: `QLabel` que
    muestra un `QPixmap` convertido desde la `PIL.Image.Image` devuelta por
    el motor (`Image.tobytes` → `QImage` → `QPixmap`), sin pasar por disco
    ni por red
    - _Requirements: 5.2_
    - _Design: "Components and Interfaces" #9_

- [ ] 16. `PreviewRenderWorker` con token de generación
  - [ ] 16.1 Implementar `PreviewRenderWorker` en
    `src/bannermania_demo/desktop/ui/preview_render_worker.py` como
    `QRunnable`: recibe una `BannerConfig`/`AnimationConfig` y un
    `generation_id`; al terminar, emite el resultado junto con ese
    `generation_id` para que el llamador decida si sigue vigente
    - _Requirements: 5.1, 5.3_
    - _Design: "Flujo de vista previa en tiempo real (Requisito 5)"_
  - [ ]* 16.2 Escribir la prueba de propiedad en
    `tests/desktop/test_property_latest_config_wins.py`, usando
    `FakeRenderingEngine` con demoras controlables para simular de 2 a N
    renders concurrentes que terminan en orden arbitrario
    - **Property 8: La última configuración gana en renders concurrentes**
    - **Validates: Requirements 5.4**

- [ ] 17. `MainWindow`: orquestación, arranque y catálogos
  - [ ] 17.1 Implementar `MainWindow` en
    `src/bannermania_demo/desktop/ui/main_window.py` y el punto de entrada
    `src/bannermania_demo/desktop/__main__.py`: al construirse, obtiene los
    cinco catálogos desde `RenderingEnginePort` envolviendo cada obtención
    en manejo de `CatalogUnavailableError` (mostrar mensaje comprensible y
    seguir en ejecución); ensambla `ControlsPanel`, `PreviewPanel`, un
    `QThreadPool` compartido, el contador `generation_id`, el menú Proyecto
    (acciones Guardar/Abrir), y conecta `config_changed` de
    `ControlsPanel` con el encolado de un `PreviewRenderWorker`; conecta el
    botón de aleatorizar con `RandomizeService`; la ventana debe quedar
    visible sin abrir navegador ni servidor HTTP y sin realizar peticiones
    de red durante el renderizado
    - _Requirements: 1.1, 1.2, 1.3, 5.1, 8.2, 8.3, 9.3_
    - _Design: "Vista de capas"; "Flujo de vista previa en tiempo real"_
  - [ ]* 17.2 Escribir la prueba de propiedad en
    `tests/desktop/test_property_startup_catalog_failure.py`, usando un
    `FakeRenderingEngine` configurado para lanzar una excepción al
    consultar cada uno de los cinco catálogos, uno por vez
    - **Property 15: Fallo al obtener un catálogo en el arranque no
      termina la aplicación**
    - **Validates: Requirements 9.3**
  - [ ]* 17.3 Escribir la prueba de propiedad en
    `tests/desktop/test_property_preview_retained_on_failure.py`, con una
    secuencia donde `FakeRenderingEngine` primero devuelve un render
    exitoso y luego lanza una excepción en un intento posterior
    - **Property 13: Retención de la última vista previa válida ante
      fallo del motor**
    - **Validates: Requirements 11.1**

- [ ] 18. Operaciones protegidas: exportación PNG/GIF y proyecto
  - [ ] 18.1 Implementar `export_png` y `export_gif` en `MainWindow`,
    decorados con `guarded_operation`: solicitan una ruta al usuario;
    cancelar el diálogo no muestra error ni modifica el banner; si el
    destino ya existe, se solicita confirmación explícita antes de
    sobrescribir; si el usuario declina, se conserva el archivo existente
    sin cambios
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 7.6, 7.7_
    - _Design: "Error Handling" — ejemplo `export_png` con
      `guarded_operation`_
  - [ ]* 18.2 Escribir la prueba de propiedad en
    `tests/desktop/test_property_png_export_dimensions.py`, usando
    `tmp_path`: exportar y luego leer el archivo PNG resultante con
    Pillow y comparar sus dimensiones contra las configuradas
    - **Property 9: Fidelidad dimensional de la exportación PNG**
    - **Validates: Requirements 6.1**
  - [ ] 18.3 Implementar en `MainWindow` las acciones de menú "Guardar
    proyecto" y "Abrir proyecto", decoradas con `guarded_operation` y
    respaldadas por `JsonProjectRepository`: al abrir con éxito, restaura
    los ocho parámetros en los controles; al fallar, deja la configuración
    vigente sin cambios y muestra un error descriptivo
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
    - _Design: "Components and Interfaces" #6, #9_
  - [ ]* 18.4 Escribir la prueba de propiedad en
    `tests/desktop/test_property_decline_overwrite_preserves_file.py`,
    usando `tmp_path` con un archivo preexistente de contenido generado por
    Hypothesis, simulando que el usuario declina confirmar la
    sobrescritura
    - **Property 10: Declinar sobrescritura preserva el archivo
      existente**
    - **Validates: Requirements 6.4**
  - [ ]* 18.5 Escribir pruebas unitarias/de ejemplo y de casos borde
    restantes sobre `MainWindow`: aplicar una configuración aleatoria
    refleja los valores en los widgets y solicita una nueva vista previa
    (Req 8.2, 8.3); exportar la marquesina produce un archivo con mimetype/
    extensión GIF (Req 7.6); un catálogo de fuentes vacío usa la fuente de
    reemplazo integrada y preview/exportación siguen funcionando
    (Req 2.5); el borde "ninguno" no dibuja nada visible (Req 3.5); sin
    ninguna vista previa previa y el motor falla se muestra el indicador de
    "no disponible" junto al error (Req 11.2); inicio y cierre de la
    ventana registran un evento INFO cada uno (Req 12.1)
    - _Requirements: 2.5, 3.5, 7.6, 8.2, 8.3, 11.2, 12.1_

- [ ] 19. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 20. Empaquetado con PyInstaller
  - [ ] 20.1 Crear los archivos de configuración de PyInstaller (`.spec`)
    para el modo `--onefile` (Windows/macOS) y `--onedir` (Linux),
    apuntando al punto de entrada
    `src/bannermania_demo/desktop/__main__.py`, incluyendo los datos de
    PySide6 necesarios
    - _Requirements: 13.1, 13.2_
    - _Design: "Components and Interfaces" #10 — "Empaquetado"_
  - [ ]* 20.2 Escribir una prueba de humo que importe
    `bannermania_demo.desktop.__main__` y construya `MainWindow` con
    `FakeRenderingEngine` sin lanzar ninguna excepción, como verificación
    automatizable de que el punto de entrada empaquetable arranca
    correctamente (la ejecución real de los instaladores por sistema
    operativo, Req 13.3/13.4, queda fuera de este plan de tareas de código)
    - _Requirements: 13.1, 13.2_

- [ ] 21. Checkpoint final - Ensure all tests pass
  - Ejecutar la suite completa (`tests/` y `tests/desktop/`) y confirmar
  que las 18 propiedades de corrección y todas las pruebas unitarias/de
  ejemplo pasan. Ensure all tests pass, ask the user if questions arise.

## Notes

- Las subtareas marcadas con `*` son pruebas (unitarias, de ejemplo o
  basadas en propiedades) y pueden omitirse para una entrega más rápida;
  si se ejecutan, deben escribirse antes de la implementación que validan
  (TDD) y confirmarse en rojo antes de implementar.
- Cada una de las 18 propiedades de corrección de `design.md` tiene
  exactamente una subtarea de prueba basada en propiedades, ubicada junto a
  la implementación que valida.
- Las tareas de Checkpoint no tienen sub-tareas: ejecutan la suite de
  pruebas acumulada hasta ese punto.
- `FakeRenderingEngine` (tarea 5.3) es el doble de prueba reutilizado por
  las propiedades 1, 7, 8, 13 y 15, y por las pruebas de `ControlsPanel`,
  `PreviewRenderWorker` y `MainWindow`.
- Las categorías "Smoke" e "Integración" de tiempo real/SO descritas en la
  sección "Testing Strategy" de `design.md` (tiempos de vista previa,
  ausencia de llamadas de red, arranque del instalador en una imagen
  limpia) no se listan como tareas de código independientes cuando
  requieren ejecución manual o en CI por plataforma, conforme a la regla
  de "Coding Tasks Only" de este flujo de trabajo; la tarea 20.2 cubre la
  parte verificable de forma automatizada.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2"] },
    { "id": 1, "tasks": ["2.2", "4.2", "5.1", "7.3", "9.2", "10.3"] },
    { "id": 2, "tasks": ["2.1", "4.1", "5.3", "5.5", "7.1", "7.2", "7.5", "9.1", "9.4", "10.1", "10.2", "10.5", "10.6", "12.1", "13.2", "15.1", "15.3", "16.1"] },
    { "id": 3, "tasks": ["5.2", "5.4", "5.6", "7.4", "7.7", "9.3", "9.5", "10.4", "12.2", "13.1", "15.2", "16.2"] },
    { "id": 4, "tasks": ["7.6", "7.9", "12.3", "12.4", "12.5", "17.1"] },
    { "id": 5, "tasks": ["7.8", "17.2", "17.3", "18.1"] },
    { "id": 6, "tasks": ["18.2", "18.3"] },
    { "id": 7, "tasks": ["18.4", "18.5", "20.1"] },
    { "id": 8, "tasks": ["20.2"] }
  ]
}
```
