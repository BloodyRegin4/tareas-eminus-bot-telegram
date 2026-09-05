# Notificador de Tareas Eminus4 (UV)
Un script automatizado en Python que extrae tus tareas pendientes de Eminus4 y te envía un resumen diario directamente a tu celular vía Telegram.

## ¿Cómo funciona?
El script utiliza `Selenium` en modo *headless* para iniciar sesión en tu cuenta de Eminus, extraer el token de acceso de la API oficial y consultar tus materias. Todo sin abrir ventanas molestas.

## ¿Cómo obtener los IDs de tus materias?
Para que el bot sepa qué buscar, necesitas los IDs únicos de tus cursos actuales del semestre. 
  1. Inicia sesión en Eminus 4 y presiona `F12` para abrir las herramientas de desarrollador.
  2. Ve a la pestaña **Network** (Red), filtra por **Fetch/XHR** y recarga la página (`F5`).
  3. Busca la petición donde cargan tus cursos (getAllCourses) y da clic.
  4. En la pestaña de **Preview**, verás el objeto JSON con la lista completa de todas tus materias y sus respectivos IDs.

## ¿Cómo crear tu Bot y obtener el Token y Chat ID?
Para que los mensajes lleguen a tu celular, necesitas crear un bot personal en Telegram. Es gratis y toma poco tiempo:
   **Paso 1: Crear el Bot y obtener el Token**
     1. Abre Telegram y busca al usuario **@BotFather** (el que tiene la palomita azul).
     2. Inicia el chat y envíale el comando `/newbot`.
     3. Te pedirá un nombre para tu bot (ej. *MisTareasEminus*) 
     4. Te pedirá un nombre de usuario que debe terminar en "bot" (ej. *mis_tareas_uv_bot*).
     5. Al terminar, el BotFather te dará un mensaje largo que contiene tu **Token HTTP API** (ej. `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`). Cópialo.

   **Paso 2: Obtener tu Chat ID (A dónde se enviarán los mensajes)**
     1. En el buscador de Telegram, busca el bot llamado **@userinfobot**.
     2. Envíale el comando `/getid` (o inicia el bot).
     3. Te devolverá tu id (ej. `1667702151`). Ese es tu **Chat ID**.

   **Paso 3: ¡Muy importante! Activar tu bot**
   Antes de correr el código, debes ir al chat del bot que tú acabas de crear y enviarle un mensaje (como "Hola" o presionar "Iniciar"). Si no haces esto, Telegram bloqueará los mensajes por seguridad y el código marcará error.

## Uso Local
1. Clona este repositorio
2. Instala las dependencias:
   `pip install requests selenium`
3. Crea un archivo llamado `config_eminus.json` en la raíz del proyecto (está ignorado en git por seguridad) con la siguiente estructura:
```json
{
  "username": "zSXXXXXXXX",
  "password": "tu_contraseña",
  "telegram_token": "TOKEN_DE_TU_BOTFATHER",
  "telegram_chat_id": "TU_CHAT_ID_NUMERICO",
  "materias": {
    "id_de_tu_materia1": "Nombre de la Materia 1",
    "id_de_tu_materia2": "Nombre de la Materia 2"
    # Termina de listar los ids y nombres de tus materias del semestre
  }
}