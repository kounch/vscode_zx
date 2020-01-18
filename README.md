# vscode_zx

Visual Studio Tasks and Scripts for NextBASIC and ZX Basic

---

## English

### What this plugin does

---

Tareas y scripts de Visual Studio Code para el desarrollo en NextBASIC y ZX Basic

## Castellano

### Software necesario

#### Visual Studio Code

Documentación, descarga, etc. [aquí](https://code.visualstudio.com/)

#### Python 3.x

Documentación, descarga, etc. [aquí](https://www.python.org/)

#### ZX Basic

Documentación, descarga, etc. [aquí](https://zxbasic.readthedocs.io)

Se necesita, al menos, la versión 1.8.10 (en formato .zip o .tar.gz)

NextLibs para ZX Basic. Leer más [aquí](http://zxbasic.uk/nextbuild/the-nextlibs/). Descargar [aquí](http://zxbasic.uk/nextbuild/download/)

### Software opcional

#### hdfmonkey

Descarga, [aquí](http://files.zxdemo.org/gasman/speccy/hdfmonkey/). Código fuente [aquí](https://github.com/gasman/hdfmonkey). Versión compilada para Windows [aquí](http://uto.speccy.org/)

#### CSpect

La última versión en desarrollo se puede obtener [aquí](https://dailly.blogspot.com/)

#### ZEsarUX

Documentación, descarga, etc. [aquí](https://github.com/chernandezba/zesarux)

### Instalación

#### Instalación Básica

Si no estaba ya, instalar Python 3. En el caso de Windows, asegurarse de que se incluye `py launcher` en las opciones de instalación.

Crear una estructura de directorios similar a la siguiente:

    vscode_zx/
       |
       +--zxbasic/
       |
       +--Projects/
       |     |
       |     +--.vscode/
       |           |
       |           +--tasks.json
       |
       +--zxbloadermaker.py
       +--zxb_build.sh  (zxb_build.bat en el caso de Windows)

La carpeta Projects se puede renombrar, pero ha de estar al lado de `zxbloadermaker.py` y `zxb_build...`.

Descomprimir en `zxbasic` la distribución completa de ZX Basic, y luego copiar el archivo `nextlib.bas` (de `NextBuild-current.zip`: `NextBuildv5/ZXBC/library/`) en `zxbasic/library/`.

#### Instalación con emuladores

Si se desea tener también la opción de compilar y lanzar en los emuladores, ampliar la estructura así:

    vscode_zx/
       |
       +--CSpect/
       +--ZEsarUX/
       +--zesaruxrc (zesaruxwinrc en el caso de Windows)
       +--zxbasic/
       |
       +--Projects/
       |     |
       |     +--.vscode/
       |           |
       |           +--tasks.json
       |
       +--zxbloadermaker.py
       +--zxb_build.sh  (zxb_build.bat en el caso de Windows)
       |
       +--hdfmonkey  (hdfmonkey.exe en el caso de Windows)

...y descomprimir en `CSpect/` y `ZEsarUX/` los dos emuladores (en el caso de MacOS, copiar directamente la app de ZEsarUX al lado de `zxb_build.sh`).

Ahora, para cada emulador, se ha de configurar la SD para la emulación.

##### Configuración de CSpect

Tras obtener un archivo de imagen de SD, renombrarlo como `systemnext.img`, y copiarlo en el directorio `CSpect/`, junto con los ficheros `enNextZX.rom` y `enNxtmmc.rom`. (Ver [aquí](https://www.specnext.com/latestdistro/) para más información y [aquí](http://www.zxspectrumnext.online/cspect/) para la descarga).

Creamos la estructura en la SD donde se guardarán nuestros programas compilados:

    cd /(...)/vscode_zx/
    hdfmonkey mkdir ./CSpect/systemnext.img /devel

Opcionalmente, usando `hdfmonkey`, sustituimos `autoexec.bat` de la distribución original por el que está disponible en `ToInstall/autoexec.bas`. Por ejemplo:

    hdfmonkey put ./CSpect/systemnext.img ./ToInstall/autoexec.bat /nextzxos/autoexec.bas

##### Configuración de ZEsarUX

Modificar el archivo `zesaruxrc` (`zesaruxwinrc` en el caso de Windows), poniendo en `--mmc-file` la ruta completa al archivo tbblue.mmc`.

Se puede utilizar el archivo proporcionado por la propia distribución del emulador. Si se prefiere utilizar uno descargado, renombrarlo como `tbblue.mmc`, y copiarlo en el directorio `ZEsarUX/`.

Creamos la estructura en la SD donde se guardarán nuestros programas compilados:

    cd /(...)/vscode_zx/
    hdfmonkey mkdir ./ZEsarUX/tbblue.mmc /devel

En el caso de MacOS

    cd /(...)/vscode_zx/
    hdfmonkey mkdir ./ZEsarUX.app/Contents/Resources/tbblue.mmc /devel

Opcionalmente, usando `hdfmonkey`, sustituimos `autoexec.bat` de la distribución original por el que está disponible en `ToInstall/autoexec.bas`. Por ejemplo:

    hdfmonkey put ./ZEsarUX/tbblue.mmc ./ToInstall/autoexec.bat /nextzxos/autoexec.bas

En el caso de MacOS

    hdfmonkey put ./ZEsarUX.app/Contents/Resources/tbblue.mmc ./ToInstall/autoexec.bat /nextzxos/autoexec.bas

### Uso

#### Compilación

Abrir el directorio "Projects" (o con el nombre que se haya definido) desde Visual Studio Code.

El fichero `tasks.json` define una tarea llamada de Visual Studio Code `Build` que, al ser invocada sobre un fichero `.zbas` de ZX Basic, creará un directorio `build` y, dentro de este, un fichero `.bin` con el programa compilado, y un lanzador `.bas` para poder iniciarlo desde el navegador de ZX Next, ESXDOS o +3e DOS.

Por ejemplo, partiendo de

       +--Projects/
             |
             +--.vscode/
             |     |
             |     +--tasks.json
             |
             +--Ejemplo.bas

Tras ejecutar la tarea, se creará

       +--Projects/
             |
             +--.vscode/
             |     |
             |     +--tasks.json
             |
             +--Ejemplo.bas
             |
             +--build/
                  |
                  +-Ejemplo.bas
                  +-Ejemplo.bin

Los ficheros `.bas` no tienen por qué estar en la raíz del directorio `Projects`, pudiendo crearse tantos subdirectorios como se desee.

#### Compilación y ejecución en emulador

Existen otras dos tareas llamadas `Build And Run (CSpect)` y `Build And Run (ZEsarUX)` que sirven para realizar una compilación, copiar los dos archivos (`.bin` y `.bas`) en la SD virtual del emulador correspondiente, y luego lanzarlo. Si, además, se ha configurado el archivo `autoexec.bas`, se iniciará directamente un programa donde, pulsando cualquier tecla, excepto BREAK (Mayúsculas + Espacio), se intentará ejecutar el programa compilado. Si se pulsa BREAK, se saldrá al navegador de ZX Next.
