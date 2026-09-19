# Requirements Document

## Introduction

BannerMania es actualmente una aplicación web (Flask + Pillow) que genera
banners estáticos (PNG) y marquesinas animadas (GIF) a partir de texto, con
catálogos configurables de fuentes, efectos de texto, patrones de fondo y
bordes decorativos. Esta especificación cubre una **Aplicación de Escritorio**
equivalente, que reutiliza el motor de renderizado existente (basado en
Pillow) pero se ejecuta como programa nativo instalable, sin depender de un
servidor Flask ni de un navegador para su uso normal.

**Supuestos adoptados para esta primera versión de requisitos** (a validar
con el usuario antes de pasar a diseño):

- La Aplicación de Escritorio debe funcionar completamente sin conexión a
  red (no requiere un servidor remoto para renderizar banners).
- La Aplicación de Escritorio debe soportar Windows, macOS y Linux, ya que
  el motor de renderizado actual ya contempla rutas de fuentes para ambos
  sistemas.
- El motor de renderizado (patrones, efectos, bordes, ajuste de fuente) se
  reutiliza sin cambios de comportamiento; el trabajo nuevo es la interfaz
  nativa, el empaquetado y la persistencia local.
- La elección concreta del framework de interfaz gráfica y de la herramienta
  de empaquetado por sistema operativo se define en la fase de diseño, no en
  requisitos; aquí solo se exige que la solución sea nativa, instalable y
  no dependa de un navegador para su flujo principal.

**Preguntas abiertas para el usuario** (ver sección final): confirmar
sistemas operativos objetivo, si se requiere firma de código/notarización,
y si el "Archivo de Proyecto" (guardar/cargar configuración) es necesario
para esta primera versión o puede diferirse.

## Glossary

- **Aplicación_de_Escritorio**: El programa nativo instalable, objeto de esta
  especificación, que permite crear banners e imágenes animadas sin
  requerir un navegador ni un servidor remoto.
- **Motor_de_Renderizado**: El componente que produce las imágenes PNG/GIF a
  partir de texto, fuente, efecto, patrón de fondo y borde, reutilizando la
  lógica existente basada en Pillow.
- **Catálogo_de_Fuentes**: La lista de fuentes disponibles, determinada por
  los archivos de fuente presentes en el sistema operativo anfitrión.
- **Catálogo_de_Efectos**: La lista de efectos de texto disponibles (por
  ejemplo `plano`, `contorno`, `sombra`, `3d`, `degradado`, `arcoíris`,
  `neón`, `resplandor`, `glitch`, `relieve`).
- **Catálogo_de_Patrones**: La lista de patrones de fondo disponibles (por
  ejemplo `sólido`, `rayas`, `damero`, `puntos`, `diagonal`).
- **Catálogo_de_Bordes**: La lista de estilos de borde decorativo disponibles
  (por ejemplo `ninguno`, `simple`, `doble`, `discontinuo`, `punteado`,
  `estrellas`, `zigzag`, `esquinas`).
- **Panel_de_Vista_Previa**: El área de la interfaz que muestra el resultado
  actualizado del banner mientras el usuario ajusta parámetros.
- **Gestor_de_Exportación**: El componente que guarda el resultado renderizado
  (PNG o GIF) en el sistema de archivos local, a solicitud del usuario.
- **Archivo_de_Proyecto**: Un archivo local en formato JSON que almacena la
  configuración completa de un banner (texto, fuente, efecto, patrón,
  borde, colores, tamaño y parámetros de animación) para su reapertura
  posterior.
- **Registro_de_Eventos**: El mecanismo de logging estructurado local de la
  Aplicación_de_Escritorio (no impresión por consola).

## Requirements

### Requisito 1: Ejecución nativa sin servidor web

**User Story:** Como usuario final, quiero ejecutar BannerMania como un
programa de escritorio instalado, para poder crear banners sin depender de
un navegador ni de una conexión a un servidor.

#### Criterios de Aceptación

1. WHEN el usuario inicia la Aplicación_de_Escritorio, THE
   Aplicación_de_Escritorio SHALL presentar su interfaz gráfica en una
   ventana nativa visible en un plazo máximo de 5 segundos, sin abrir ni
   requerir un navegador web ni un servidor HTTP local.
2. WHEN el usuario solicita generar o actualizar un banner estático o una
   animación, THE Aplicación_de_Escritorio SHALL ejecutar el
   Motor_de_Renderizado dentro del mismo proceso de la aplicación, sin
   iniciar un proceso servidor separado ni realizar ninguna petición HTTP o
   de red para dicha generación.
3. WHILE el equipo del usuario no tiene conexión a Internet, THE
   Aplicación_de_Escritorio SHALL permitir generar banners estáticos y
   animados con las mismas funciones, catálogos y tiempos de respuesta
   disponibles que con conexión a Internet, sin deshabilitar ni degradar
   ninguna característica de generación.

### Requisito 2: Selección de texto, fuente y efecto

**User Story:** Como usuario final, quiero elegir el texto, la fuente y el
efecto visual del banner, para personalizar el resultado igual que en la
versión web.

#### Criterios de Aceptación

1. THE Aplicación_de_Escritorio SHALL permitir ingresar el texto del banner
   mediante un campo editable, admitiendo una longitud de hasta el límite
   máximo de caracteres definido por el Motor_de_Renderizado.
2. IF el texto ingresado supera el límite máximo de caracteres definido por
   el Motor_de_Renderizado, THEN THE Aplicación_de_Escritorio SHALL truncar
   el texto a dicho límite y notificar al usuario del ajuste realizado.
3. IF el campo de texto está vacío al momento de generar el banner, THEN THE
   Aplicación_de_Escritorio SHALL utilizar un texto de reemplazo
   predeterminado para el renderizado.
4. WHEN la Aplicación_de_Escritorio inicia, THE Aplicación_de_Escritorio
   SHALL detectar el Catálogo_de_Fuentes disponible en el sistema operativo
   anfitrión y presentarlo para su selección.
5. IF ninguna fuente del Catálogo_de_Fuentes está disponible en el sistema
   operativo anfitrión, THEN THE Aplicación_de_Escritorio SHALL utilizar una
   fuente de reemplazo integrada, manteniendo disponibles la generación de
   vista previa y la exportación del banner con dicha fuente.
6. WHEN el usuario selecciona una fuente del Catálogo_de_Fuentes, THE
   Motor_de_Renderizado SHALL aplicar dicha fuente al texto renderizado.
7. THE Aplicación_de_Escritorio SHALL presentar el Catálogo_de_Efectos
   completo para su selección sobre el texto del banner.
8. WHEN el usuario selecciona un efecto del Catálogo_de_Efectos, THE
   Motor_de_Renderizado SHALL aplicar dicho efecto al texto renderizado.

### Requisito 3: Selección de patrón de fondo y borde decorativo

**User Story:** Como usuario final, quiero elegir un patrón de fondo y un
borde decorativo, para lograr distintos estilos visuales de banner.

#### Criterios de Aceptación

1. THE Aplicación_de_Escritorio SHALL presentar el Catálogo_de_Patrones
   completo para su selección como fondo del banner.
2. THE Aplicación_de_Escritorio SHALL presentar el Catálogo_de_Bordes
   completo para su selección como borde decorativo del banner.
3. WHEN el usuario selecciona un patrón del Catálogo_de_Patrones, THE
   Motor_de_Renderizado SHALL pintar dicho patrón como fondo del banner.
4. WHEN el usuario selecciona un estilo de borde del Catálogo_de_Bordes
   distinto de "ninguno", THE Motor_de_Renderizado SHALL dibujar dicho borde
   sobre el banner.
5. WHEN el usuario selecciona el estilo de borde "ninguno" del
   Catálogo_de_Bordes, THE Motor_de_Renderizado SHALL renderizar el banner
   sin ningún borde decorativo visible.
6. IF se especifica un valor de patrón que no pertenece al
   Catálogo_de_Patrones, THEN THE Aplicación_de_Escritorio SHALL rechazar
   dicho valor, conservar el patrón de fondo previamente vigente, y
   notificar al usuario un mensaje de error indicando que el valor no es
   válido.
7. IF se especifica un valor de borde que no pertenece al
   Catálogo_de_Bordes, THEN THE Aplicación_de_Escritorio SHALL rechazar
   dicho valor, conservar el borde decorativo previamente vigente, y
   notificar al usuario un mensaje de error indicando que el valor no es
   válido.

### Requisito 4: Control de colores y tamaño

**User Story:** Como usuario final, quiero definir los colores del texto, el
fondo y el acento del patrón, así como el tamaño del banner, para ajustar el
resultado a mis necesidades.

#### Criterios de Aceptación

1. THE Aplicación_de_Escritorio SHALL permitir configurar de forma
   independiente, mediante un valor de código de color hexadecimal, el color
   principal del texto, el color secundario del texto, el color de fondo y
   el color de acento del patrón.
2. IF el usuario ingresa, en cualquiera de los cuatro campos de color (texto
   principal, texto secundario, fondo o acento), un valor que no es un
   código hexadecimal válido de 3 o 6 dígitos (con o sin el prefijo "#"),
   THEN THE Aplicación_de_Escritorio SHALL aplicar a ese campo su propio
   color de reemplazo predefinido y notificar al usuario indicando el campo
   afectado y el valor ingresado que no fue válido.
3. THE Aplicación_de_Escritorio SHALL permitir configurar el ancho del
   banner entre 200 y 3000 píxeles, y el alto del banner entre 120 y 1200
   píxeles.
4. IF el ancho o el alto ingresado por el usuario es un valor numérico fuera
   de los límites admitidos por el Motor_de_Renderizado (200 a 3000 píxeles
   de ancho, 120 a 1200 píxeles de alto), THEN THE Aplicación_de_Escritorio
   SHALL ajustar el valor al límite más cercano admitido y notificar al
   usuario indicando la dimensión ajustada y el valor aplicado.
5. IF el valor de ancho o alto ingresado por el usuario no es un número
   entero válido, THEN THE Aplicación_de_Escritorio SHALL aplicar el valor
   predeterminado de esa dimensión, notificar al usuario indicando cuál
   valor no fue válido, y continuar generando el banner sin interrupción.

### Requisito 5: Vista previa en tiempo real

**User Story:** Como usuario final, quiero ver una vista previa del banner
mientras ajusto los parámetros, para decidir la combinación final sin tener
que exportar repetidamente.

#### Criterios de Aceptación

1. WHEN el usuario modifica el texto, la fuente, el efecto, el patrón, el
   borde, un color o el tamaño, THE Panel_de_Vista_Previa SHALL mostrar una
   imagen actualizada que refleje la configuración vigente en un plazo
   máximo de 500 milisegundos desde la detección del cambio.
2. THE Panel_de_Vista_Previa SHALL mostrar la vista previa dentro de la
   ventana principal de la Aplicación_de_Escritorio, sin abrir una ventana o
   proceso externo.
3. WHILE el Motor_de_Renderizado está generando una actualización de la
   vista previa, THE Aplicación_de_Escritorio SHALL continuar aceptando y
   procesando la entrada del usuario (por ejemplo, edición de texto o
   cambios de controles) sin bloquear la interfaz, respondiendo a cada
   evento de entrada en un plazo no mayor a 100 milisegundos.
4. WHILE el Motor_de_Renderizado está generando una actualización de la
   vista previa, WHEN el usuario modifica otro parámetro de configuración,
   THE Panel_de_Vista_Previa SHALL descartar la actualización en curso y
   generar una nueva actualización que refleje únicamente la configuración
   vigente más reciente.

### Requisito 6: Exportación de banner estático

**User Story:** Como usuario final, quiero guardar el banner generado como
archivo PNG en mi equipo, para usarlo fuera de la aplicación.

#### Criterios de Aceptación

1. WHEN el usuario solicita guardar el banner estático actual, THE
   Gestor_de_Exportación SHALL escribir un archivo con extensión ".png" en
   la ubicación del sistema de archivos elegida por el usuario, con el
   banner renderizado según el texto, fuente, efecto, patrón, borde, colores
   y dimensiones configurados por el usuario en el momento de la solicitud.
2. IF la escritura del archivo no puede completarse por cualquier motivo
   (por ejemplo, la ubicación elegida no es escribible o no hay espacio
   disponible en el destino), THEN THE Gestor_de_Exportación SHALL informar
   al usuario el motivo del fallo, sin finalizar la aplicación ni alterar la
   configuración actual del banner.
3. IF el usuario cancela la selección de la ubicación sin elegir un destino,
   THEN THE Gestor_de_Exportación SHALL cancelar la operación de guardado
   sin mostrar un mensaje de error y sin modificar el banner actual.
4. IF la ubicación elegida por el usuario ya contiene un archivo con el
   mismo nombre, THEN THE Gestor_de_Exportación SHALL solicitar confirmación
   explícita del usuario antes de sobrescribirlo, conservando el archivo
   existente sin cambios si el usuario no confirma la sobrescritura.

### Requisito 7: Generación y exportación de marquesina animada

**User Story:** Como usuario final, quiero generar una marquesina animada
con distintos modos de movimiento y guardarla como GIF, para obtener una
versión dinámica del banner.

#### Criterios de Aceptación

1. WHERE el usuario activa el modo de animación, THE Aplicación_de_Escritorio
   SHALL permitir seleccionar un modo de movimiento entre desplazamiento,
   onda y salto.
2. WHEN el usuario selecciona un modo de movimiento, THE
   Motor_de_Renderizado SHALL aplicar dicho modo de movimiento a la
   animación de la marquesina.
3. WHERE el usuario activa el modo de animación, THE Aplicación_de_Escritorio
   SHALL permitir configurar la velocidad de reproducción entre 20 y 400
   milisegundos por cuadro, y la cantidad de cuadros de la animación entre
   12 y 120 cuadros, límites admitidos por el Motor_de_Renderizado.
4. IF el usuario ingresa un valor de velocidad de reproducción o de cantidad
   de cuadros fuera de los límites admitidos por el Motor_de_Renderizado,
   THEN THE Aplicación_de_Escritorio SHALL ajustar el valor al límite más
   cercano admitido y notificar al usuario del ajuste.
5. WHERE el usuario activa el ciclo de color, THE Motor_de_Renderizado SHALL
   rotar el tono del texto a lo largo del bucle de la animación.
6. WHEN el usuario solicita guardar la marquesina actual, THE
   Gestor_de_Exportación SHALL escribir un archivo en formato GIF en la
   ubicación del sistema de archivos elegida por el usuario.
7. IF la ubicación elegida por el usuario para guardar la marquesina no es
   escribible, THEN THE Gestor_de_Exportación SHALL informar al usuario el
   motivo del fallo sin finalizar la aplicación.

### Requisito 8: Selección aleatoria de configuración

**User Story:** Como usuario final, quiero solicitar una combinación
aleatoria de fuente, efecto, patrón, borde y colores, para descubrir
resultados sin configurarlos manualmente.

#### Criterios de Aceptación

1. WHEN el usuario solicita una configuración aleatoria, THE
   Aplicación_de_Escritorio SHALL seleccionar de forma independiente una
   fuente del Catálogo_de_Fuentes, un efecto del Catálogo_de_Efectos, un
   patrón del Catálogo_de_Patrones y un borde del Catálogo_de_Bordes, junto
   con un color principal de texto, un color secundario de texto, un color
   de fondo y un color de acento, cada uno expresado como un código
   hexadecimal válido y con el color principal de texto distinto del color
   de fondo.
2. WHEN se aplica una configuración aleatoria, THE Aplicación_de_Escritorio
   SHALL reflejar los valores seleccionados en los controles
   correspondientes de fuente, efecto, patrón, borde y colores.
3. WHEN se aplica una configuración aleatoria, THE Panel_de_Vista_Previa
   SHALL actualizarse para reflejar dicha configuración.

### Requisito 9: Extensibilidad de catálogos

**User Story:** Como responsable de mantenimiento del proyecto, quiero que
nuevos efectos, patrones o bordes se agreguen sin modificar la lógica de la
interfaz de escritorio, para mantener el código abierto a extensión y
cerrado a modificación.

#### Criterios de Aceptación

1. WHEN la Aplicación_de_Escritorio inicia, THE Aplicación_de_Escritorio
   SHALL presentar en sus controles correspondientes exactamente las
   entradas vigentes del Catálogo_de_Efectos, el Catálogo_de_Patrones y el
   Catálogo_de_Bordes obtenidas del Motor_de_Renderizado en ese momento,
   incluyendo toda entrada agregada y excluyendo toda entrada eliminada
   desde el inicio anterior, sin que la interfaz gráfica contenga código
   específico por cada entrada.
2. THE Aplicación_de_Escritorio SHALL obtener el Catálogo_de_Fuentes, el
   Catálogo_de_Efectos, el Catálogo_de_Patrones y el Catálogo_de_Bordes
   desde el Motor_de_Renderizado en cada inicio de la aplicación, en lugar
   de mantener copias propias codificadas de dichas listas en el código de
   la interfaz gráfica.
3. IF el Motor_de_Renderizado no puede proporcionar el Catálogo_de_Fuentes,
   el Catálogo_de_Efectos, el Catálogo_de_Patrones o el Catálogo_de_Bordes
   durante el inicio de la Aplicación_de_Escritorio, THEN THE
   Aplicación_de_Escritorio SHALL mostrar al usuario un mensaje de error
   comprensible y continuar en ejecución sin finalizar el proceso.

### Requisito 10: Guardar y cargar configuración de banner (Archivo de Proyecto)

**User Story:** Como usuario final, quiero guardar la configuración completa
de un banner en un archivo local y volver a abrirla más tarde, para
continuar editando un diseño sin reconfigurar todos los parámetros.

#### Criterios de Aceptación

1. WHEN el usuario solicita guardar el proyecto actual, THE
   Aplicación_de_Escritorio SHALL serializar el texto, la fuente, el
   efecto, el patrón, el borde, los colores, el tamaño y los parámetros de
   animación vigentes en un Archivo_de_Proyecto ubicado en el destino del
   sistema de archivos que el usuario haya seleccionado.
2. WHEN el usuario solicita abrir un Archivo_de_Proyecto que contiene los
   ocho parámetros requeridos (texto, fuente, efecto, patrón, borde,
   colores, tamaño y parámetros de animación) con valores dentro de los
   límites admitidos por el Motor_de_Renderizado, THE
   Aplicación_de_Escritorio SHALL restaurar en la interfaz cada uno de
   dichos parámetros con el valor almacenado en el archivo.
3. WHEN el usuario abre un Archivo_de_Proyecto inmediatamente después de
   haberlo guardado sin modificaciones externas al archivo, THE
   Aplicación_de_Escritorio SHALL restaurar un valor idéntico al vigente en
   el momento de guardar para cada uno de los parámetros serializados
   (texto, fuente, efecto, patrón, borde, colores, tamaño y parámetros de
   animación).
4. IF el archivo seleccionado para abrir no puede leerse, o no contiene la
   estructura JSON esperada de un Archivo_de_Proyecto (faltan uno o más de
   los ocho parámetros requeridos, alguno tiene un tipo de dato incorrecto,
   o algún valor está fuera de los límites admitidos por el
   Motor_de_Renderizado), THEN THE Aplicación_de_Escritorio SHALL informar
   al usuario un error descriptivo indicando la causa, sin modificar la
   configuración vigente en la interfaz.
5. IF la ubicación elegida por el usuario para guardar el
   Archivo_de_Proyecto no es escribible (por ejemplo, por permisos
   insuficientes o espacio en disco insuficiente), THEN THE
   Aplicación_de_Escritorio SHALL informar al usuario el motivo del fallo
   sin perder la configuración vigente en la interfaz ni finalizar la
   aplicación.

### Requisito 11: Manejo de errores en la interfaz

**User Story:** Como usuario final, quiero recibir mensajes claros cuando
algo falla, para entender qué corregir sin que la aplicación se cierre
inesperadamente.

#### Criterios de Aceptación

1. IF el Motor_de_Renderizado genera un error al procesar la configuración
   vigente Y existe una vista previa válida generada previamente, THEN THE
   Aplicación_de_Escritorio SHALL mostrar un mensaje de error que identifique
   el parámetro o la operación que causó el fallo, sin incluir detalles
   técnicos internos (por ejemplo, trazas de pila), y conservar sin
   modificar la última vista previa válida en el Panel_de_Vista_Previa.
2. IF el Motor_de_Renderizado genera un error al procesar la configuración
   vigente Y no existe ninguna vista previa válida generada previamente,
   THEN THE Aplicación_de_Escritorio SHALL mostrar en el
   Panel_de_Vista_Previa un indicador de estado que señale que no hay vista
   previa disponible, junto con el mensaje de error correspondiente al
   fallo.
3. IF ocurre un error no previsto durante una operación solicitada por el
   usuario (por ejemplo, exportar un banner o marquesina, guardar o abrir un
   Archivo_de_Proyecto, o generar una vista previa), THEN THE
   Aplicación_de_Escritorio SHALL evitar el cierre del proceso, conservar sin
   pérdida los valores de configuración ingresados por el usuario antes del
   error, mostrar al usuario un mensaje de error que indique la operación
   que no se completó (sin incluir detalles técnicos internos), y registrar
   el error mediante el Registro_de_Eventos.

### Requisito 12: Registro de eventos local

**User Story:** Como responsable de mantenimiento del proyecto, quiero que la
aplicación de escritorio registre sus eventos relevantes en un archivo
local, para poder diagnosticar problemas reportados por los usuarios.

#### Criterios de Aceptación

1. THE Registro_de_Eventos SHALL escribir en un archivo de registro local,
   incluyendo una marca de fecha y hora en cada entrada, los siguientes
   eventos operativos de la Aplicación_de_Escritorio: inicio y cierre de la
   aplicación, exportación de un banner o una marquesina (Requisito 6,
   Requisito 7), guardado y apertura de un Archivo_de_Proyecto (Requisito
   10), y errores manejados conforme al Requisito 11; en lugar de utilizar
   salida estándar de depuración.
2. WHEN la Aplicación_de_Escritorio captura y maneja un error conforme al
   Requisito 11, THE Registro_de_Eventos SHALL incluir en la entrada
   correspondiente el tipo de error, el nombre de la operación que lo
   originó y la marca de fecha y hora del evento.
3. THE Registro_de_Eventos SHALL admitir al menos los niveles de severidad
   informativo, advertencia y error, registrando como advertencia los
   eventos de reemplazo o ajuste automático de valores descritos en el
   Requisito 2 (criterio 3) y el Requisito 4 (criterio 4), como error los
   eventos descritos en el Requisito 11, y como informativo el resto de los
   eventos operativos listados en el criterio 1.
4. IF el Registro_de_Eventos no puede escribir una entrada en el archivo de
   registro local por falta de permisos o de espacio en disco, THEN THE
   Aplicación_de_Escritorio SHALL continuar ejecutando la operación
   solicitada por el usuario sin interrumpirla ni finalizar el proceso.

### Requisito 13: Empaquetado e instalación multiplataforma

**User Story:** Como usuario final, quiero instalar BannerMania en mi
sistema operativo mediante un paquete o instalador estándar, para usarlo sin
configurar manualmente un entorno de Python.

#### Criterios de Aceptación

1. THE Aplicación_de_Escritorio SHALL distribuirse como un paquete
   instalable o ejecutable independiente para Windows, macOS y Linux, que
   incluya el intérprete de Python y todas las dependencias necesarias, sin
   requerir que el usuario instale Python ni dependencias manualmente.
2. WHEN el paquete de instalación se ejecuta en un sistema operativo
   soportado, THE Aplicación_de_Escritorio SHALL quedar disponible para su
   ejecución mediante un acceso directo, entrada de menú de aplicaciones, o
   ejecutable independiente, sin que el usuario deba realizar pasos
   adicionales de configuración manual.
3. IF la instalación del paquete falla o se interrumpe antes de completarse,
   THEN THE Aplicación_de_Escritorio SHALL dejar el sistema del usuario sin
   una instalación parcial o inconsistente, y el instalador SHALL informar
   al usuario el motivo del fallo.
4. IF el paquete de instalación se ejecuta en un sistema operativo no
   soportado, THEN THE Aplicación_de_Escritorio SHALL informar al usuario
   que dicho sistema operativo no está soportado, sin dejar archivos ni
   configuración residual en el sistema.

## Preguntas abiertas / decisiones pendientes

Estas preguntas no bloquean esta primera versión del documento, pero deben
resolverse antes o durante el diseño:

1. **Sistemas operativos objetivo**: ¿se confirma Windows, macOS y Linux
   como alcance de la versión 1, o se prioriza uno solo para un primer
   lanzamiento?
2. **Archivo de Proyecto (Requisito 10)**: ¿es necesario para esta primera
   versión, o puede diferirse a una iteración posterior?
3. **Firma de código y notarización**: ¿se requiere firma de código para
   Windows/macOS en esta primera versión, considerando que es un proyecto de
   demostración?
4. **Framework de interfaz gráfica**: la elección técnica (por ejemplo, una
   interfaz nativa con un binding de Python, o reutilizar la interfaz web
   actual embebida en una ventana nativa) se definirá en la fase de diseño;
   ¿existe alguna preferencia previa del usuario que deba condicionar esa
   decisión?
