# Envío automático de tareas por correo

Este script permite enviar archivos por correo mediante **Microsoft Graph** desde una cuenta de Microsoft 365, sin depender de mantener abierta una sesión en Outlook Web.

Está pensado para tareas repetitivas en las que normalmente cambian solo algunos datos, por ejemplo:

- número o identificador de la tarea;
- archivo adjunto;
- nombre del alumno;
- número de control o matrícula;
- destinatario;
- materia;
- asunto.

El script puede clonarse y configurarse para distintos usuarios. No depende de una ruta específica ni de los datos de una persona concreta.

> [!IMPORTANT]
> Se debe cambiar el nombre de `example.py` a `script.py`

---

## Funcionamiento general

El flujo normal es:

1. Seleccionar un archivo desde el Explorador de Windows o escribir su ruta.
2. Escribir el número de tarea.
3. Revisar los datos del correo.
4. Confirmar el envío.
5. Microsoft Graph envía el mensaje desde la cuenta institucional autenticada.

Ejemplo:

```text
=== Envío de tareas ===

Archivo seleccionado: tarea.pdf
Número de tarea: 1.6

Asunto:       Tarea 1.6 de Lenguajes y Autómatas 1
Destinatario: profesor@institucion.edu.mx
Archivo:      tarea.pdf

Contenido:
----------------
12345678
Nombre del alumno
----------------

¿Enviar? [s/N]:
```

---

## Requisitos

- Windows 10 u 11.
- Python 3.
- Una cuenta de Microsoft 365.
- Acceso a Microsoft Entra ID.
- Una aplicación registrada en Microsoft Entra.
- Permiso delegado de Microsoft Graph `Mail.Send`.

Las dependencias principales del script son:

```text
msal
requests
```

---

## Clonar el repositorio

Ejemplo:

```powershell
git clone https://github.com/iowosyse/EnvioTarea
cd EnvioTarea
```

La ubicación del proyecto puede ser cualquiera.

Ejemplos válidos:

```text
C:\Users\usuario\code\EnvioTarea
D:\Proyectos\EnvioTarea
C:\Dev\correo-tareas
```

Las rutas utilizadas en el menú contextual y en el perfil de PowerShell deben adaptarse a la ubicación elegida por cada usuario.

---

## Crear el entorno virtual

Desde PowerShell, dentro de la carpeta del proyecto:

```powershell
python -m venv .venv
```

Activarlo:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalar las dependencias:

```powershell
python -m pip install -r requirements.txt
```

Si todavía no existe `requirements.txt`, pueden instalarse directamente:

```powershell
python -m pip install msal requests
```

---

## Generar `requirements.txt`

Con el entorno virtual activado:

```powershell
python -m pip freeze > requirements.txt
```

Para instalar posteriormente las mismas dependencias:

```powershell
python -m pip install -r requirements.txt
```

---

# Configuración de Microsoft Entra

Entrar a:

```text
https://entra.microsoft.com/
```

e iniciar sesión con la cuenta de Microsoft 365 desde la que se enviarán los correos.

---

## 1. Registrar una aplicación

Ir a:

```text
Entra ID
→ Registros de aplicaciones
→ Nuevo registro
```

Puede usarse cualquier nombre descriptivo, por ejemplo:

```text
Envío Tareas
```

### Tipo de cuenta

Si la aplicación se utilizará únicamente dentro de una institución u organización, seleccionar:

```text
Solo cuentas en este directorio organizativo
```

Esto crea una aplicación **single-tenant**.

No es necesario introducir una URI de redirección para el flujo usado por este proyecto.

---

## 2. Permitir flujos de clientes públicos

Dentro de la aplicación registrada, ir a:

```text
Authentication
```

o, dependiendo de la interfaz actual de Microsoft Entra:

```text
Authentication (Preview)
```

Buscar:

```text
Permitir flujos de clientes públicos
```

y dejarlo en:

```text
Habilitado
```

El script se comporta como una aplicación de escritorio o CLI, por lo que utiliza autenticación de cliente público.

No es necesario crear un `client secret`.

---

## 3. Agregar el permiso `Mail.Send`

Ir a:

```text
Permisos de API
→ Agregar un permiso
→ Microsoft Graph
→ Permisos delegados
```

Buscar:

```text
Mail.Send
```

y agregarlo.

El proyecto utiliza permisos **delegados**, por lo que cada usuario inicia sesión con su propia cuenta y los correos se envían desde esa cuenta.

Una organización puede aplicar políticas de consentimiento más restrictivas. Si Microsoft solicita aprobación administrativa, será necesario que el administrador del tenant autorice la aplicación.

---

## 4. Obtener los identificadores de la aplicación

En:

```text
Información general
```

copiar:

```text
Id. de aplicación (cliente)
Id. de directorio (inquilino)
```

En el código corresponden a:

```python
CLIENT_ID = "ID_DE_APLICACION"
TENANT_ID = "ID_DE_DIRECTORIO"
```

Estos identificadores no son contraseñas.

---

# ¿Pueden varias personas usar la misma aplicación de Entra?

Sí.

Si la aplicación fue creada como:

```text
Solo cuentas en este directorio organizativo
```

otros usuarios pertenecientes al mismo tenant pueden utilizar el mismo:

```text
CLIENT_ID
TENANT_ID
```

No es obligatorio que cada usuario cree una aplicación distinta.

Cada persona puede:

1. clonar el repositorio;
2. instalar sus dependencias;
3. utilizar el mismo `CLIENT_ID` y `TENANT_ID`;
4. configurar sus propios datos;
5. iniciar sesión con su propia cuenta;
6. enviar correos desde su propia cuenta.

Ejemplo conceptual:

```text
Usuario A inicia sesión
→ el mensaje sale desde Usuario A

Usuario B inicia sesión
→ el mensaje sale desde Usuario B
```

Nunca debe compartirse la caché de autenticación de otro usuario.

### Restricciones posibles

El tenant puede tener políticas como:

- consentimiento de usuario deshabilitado;
- aprobación administrativa obligatoria;
- asignación explícita de usuarios;
- acceso condicional;
- restricciones para aplicaciones empresariales.

Si otro usuario recibe un mensaje de aprobación administrativa, esto puede ser consecuencia de la configuración de la organización y no necesariamente de un error del script.

---

# Configurar `script.py`

Cada usuario debe revisar las constantes de configuración del script.

Ejemplo:

```python
CLIENT_ID = "ID_DE_APLICACION"
TENANT_ID = "ID_DE_DIRECTORIO"

DESTINATARIO = "profesor@institucion.edu.mx"

NUMERO_CONTROL = "TU_NUMERO_DE_CONTROL"
NOMBRE = "TU_NOMBRE"

MATERIA = "NOMBRE_DE_LA_MATERIA"
```

Todos esos valores son modificables.

El asunto puede construirse automáticamente con algo como:

```python
asunto = f"Tarea {numero_tarea} de {MATERIA}"
```

Por ejemplo:

```text
Tarea 1.6 de Lenguajes y Autómatas 1
```

El cuerpo puede configurarse según las necesidades del usuario.

---

# Primera ejecución

Con el entorno virtual activado:

```powershell
python script.py
```

La primera vez, Microsoft solicitará autenticación.

Después de iniciar sesión, MSAL puede crear un archivo de caché, por ejemplo:

```text
token_cache.bin
```

No debe subirse al repositorio ni compartirse.

Se recomienda agregar a `.gitignore`:

```gitignore
.venv/
token_cache.bin
__pycache__/
```

---

# Ejecutar sin activar manualmente el entorno virtual

No es obligatorio ejecutar `Activate.ps1`.

Puede llamarse directamente al Python del entorno virtual:

```powershell
& "RUTA_DEL_PROYECTO\.venv\Scripts\python.exe" "RUTA_DEL_PROYECTO\script.py"
```

Ejemplo genérico:

```powershell
& "C:\ruta\al\proyecto\.venv\Scripts\python.exe" "C:\ruta\al\proyecto\script.py"
```

---

# Ejecutar el script con el comando `tarea`

Es posible crear una función de PowerShell para poder ejecutar el programa desde cualquier carpeta escribiendo simplemente:

```powershell
tarea
```

## 1. Abrir el perfil de PowerShell

Ejecutar:

```powershell
notepad $PROFILE
```

Si PowerShell indica que el archivo no existe, puede crearse con:

```powershell
New-Item -ItemType File -Path $PROFILE -Force
```

y después:

```powershell
notepad $PROFILE
```

## 2. Añadir la función

Agregar al archivo:

```powershell
function tarea {
    $VenvPython = "RUTA_DEL_PROYECTO\.venv\Scripts\python.exe"
    $Script     = "RUTA_DEL_PROYECTO\script.py"

    if (-not (Test-Path $VenvPython)) {
        Write-Host "No encontré el venv en $VenvPython" -ForegroundColor Red
        return
    }

    if (-not (Test-Path $Script)) {
        Write-Host "No encontré el script en $Script" -ForegroundColor Red
        return
    }

    & $VenvPython $Script @args
}
```

Cada usuario debe reemplazar:

```text
RUTA_DEL_PROYECTO
```

por la carpeta en la que clonó o guardó el repositorio.

Ejemplo:

```powershell
function tarea {
    $VenvPython = "D:\Proyectos\EnvioTarea\.venv\Scripts\python.exe"
    $Script     = "D:\Proyectos\EnvioTarea\script.py"

    if (-not (Test-Path $VenvPython)) {
        Write-Host "No encontré el venv en $VenvPython" -ForegroundColor Red
        return
    }

    if (-not (Test-Path $Script)) {
        Write-Host "No encontré el script en $Script" -ForegroundColor Red
        return
    }

    & $VenvPython $Script @args
}
```

Guardar el archivo.

## 3. Recargar el perfil

Puede cerrarse y abrirse PowerShell, o ejecutar:

```powershell
. $PROFILE
```

Después será posible ejecutar:

```powershell
tarea
```

desde cualquier directorio.

También pueden pasarse argumentos al script:

```powershell
tarea "C:\Documentos\tarea.pdf"
```

La expresión:

```powershell
@args
```

transfiere al script todos los argumentos escritos después de `tarea`.

---

# Añadir "Enviar como tarea" al menú contextual de Windows

El archivo:

```text
instalar-menu.reg
```

es una **plantilla**.

No debe importarse sin antes modificar sus rutas.

Su contenido es:

```reg
Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\Software\Classes\*\shell\EnviarTarea]
@="Enviar como tarea"
"Icon"="RUTA_DOBLE_BARRA\\.venv\\Scripts\\python.exe"

[HKEY_CURRENT_USER\Software\Classes\*\shell\EnviarTarea\command]
@="\"RUTA_DOBLE_BARRA\\.venv\\Scripts\\python.exe\" \"RUTA_DOBLE_BARRA\\script.py\" \"%1\""
```

## Importante sobre las rutas del `.reg`

Los archivos `.reg` requieren escapar las barras invertidas dentro de las cadenas.

Una ruta normal como:

```text
C:\Users\usuario\code\EnvioTarea
```

debe escribirse en el `.reg` como:

```text
C:\\Users\\usuario\\code\\EnvioTarea
```

Por ejemplo:

```reg
Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\Software\Classes\*\shell\EnviarTarea]
@="Enviar como tarea"
"Icon"="C:\\Users\\usuario\\code\\EnvioTarea\\.venv\\Scripts\\python.exe"

[HKEY_CURRENT_USER\Software\Classes\*\shell\EnviarTarea\command]
@="\"C:\\Users\\usuario\\code\\EnvioTarea\\.venv\\Scripts\\python.exe\" \"C:\\Users\\usuario\\code\\EnvioTarea\\script.py\" \"%1\""
```

## Instalar la opción del menú contextual

1. Abrir `instalar-menu.reg` con un editor de texto.
2. Sustituir todas las apariciones de:

```text
RUTA_DOBLE_BARRA
```

por la ruta real del proyecto usando `\\`.
3. Guardar el archivo.
4. Hacer doble clic sobre `instalar-menu.reg`.
5. Aceptar el aviso del Editor del Registro.
6. Hacer clic derecho sobre un archivo.
7. Seleccionar:

```text
Enviar como tarea
```

En Windows 11 puede aparecer inicialmente dentro de:

```text
Mostrar más opciones
```

---

## ¿Qué hace `%1`?

Esta parte:

```text
"%1"
```

representa el archivo sobre el que se hizo clic derecho.

Por ejemplo, si se selecciona:

```text
C:\Documentos\Tarea 1.6.pdf
```

Windows ejecutará conceptualmente:

```text
python.exe script.py "C:\Documentos\Tarea 1.6.pdf"
```

El script recibe esa ruta mediante:

```python
sys.argv[1]
```

---

## Eliminar la opción del menú contextual

Puede crearse un archivo llamado:

```text
desinstalar-menu.reg
```

con:

```reg
Windows Registry Editor Version 5.00

[-HKEY_CURRENT_USER\Software\Classes\*\shell\EnviarTarea]
```

Al importarlo se elimina la entrada del menú contextual.

---

# Referencias

- Microsoft Entra admin center: https://entra.microsoft.com/
- Tipos de cuenta compatibles: https://learn.microsoft.com/en-us/entra/identity-platform/single-and-multi-tenant-apps
- Permisos de Microsoft Graph: https://learn.microsoft.com/en-us/graph/permissions-reference
- Microsoft Graph `sendMail`: https://learn.microsoft.com/en-us/graph/api/user-sendmail
