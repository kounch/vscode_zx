# vscode_zx

Visual Studio Code Tasks and Scripts for NextBASIC and ZX Basic

[![Demo Video](./img/Demo_01.gif)](./img/Demo_01.mp4 "Demo")

Features:

- NextBASIC text to `.bas` file converter
- NextBASIC text renumbering
- Next BASIC auto formatter (Beta)
- Converts [unicode block elements](https://en.wikipedia.org/wiki/Block_Elements) to Sinclair block graphics
- Supports non-printable characters using ` as escape character
- Task support to compile with ZX Basic
- Task integration to build (or convert) and run in ZEsarUX and CSpect emulators
- Works with Windows, MacOS and (possibly) Linux

Works best if used with [ZX Spectrum BASIC syntax highlighting for Visual Studio Code](https://github.com/jsanjose/zxbasic-vscode) or [NextBASIC VSCode Syntax
](https://github.com/remy/vscode-nextbasic).

---

## English

A ZIP file with the latest version is available following [this link](https://github.com/kounch/vscode_zx/releases/latest)

### Software Requirements

- **Visual Studio Code**. Docs, downloads, etc. [here](https://code.visualstudio.com/)

- **Python (version 3.6 or later)**. Docs, downloads, etc. [here](https://www.python.org/)

- **ZX Basic**. Version 1.8.10 or later (.zip or .tar.gz). Docs, download, etcs. [here](https://zxbasic.readthedocs.io)

- **NextLibs for ZX Basic**. More info [here](http://zxbasic.uk/nextbuild/the-nextlibs/). Download [here](http://zxbasic.uk/nextbuild/download/)

### Optional Software

- **hdfmonkey**. Download, [here](http://files.zxdemo.org/gasman/speccy/hdfmonkey/). Source Code [here](https://github.com/gasman/hdfmonkey). Binary for Windows [here](http://uto.speccy.org/)

- **CSpect**. The latest development version can be found [here](https://dailly.blogspot.com/)

- **ZEsarUX**. Docs, downloads, etc. [here](https://github.com/chernandezba/zesarux)

### Installation

#### Basic Install

Install Python 3. On Windows, make sure that `py launcher` is selected as install option.

Create a directory structure like this:

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
       +--rennextbasic.py
       +--txt2nextbasic.py
       +--zxn_renumber.sh (zxn_renumber.bat on Windows)
       +--zxb_build.sh  (zxb_build.bat on Windows)

`Projects` directory can be renamed, but it *must* be next to  `txt2nextbasic.py`, `rennextbasic.py`, `zxb_build...` and `zxn_renumber...`.

Extract to `zxbasic` the full ZX Basic distribution, and then copy the file `nextlib.bas` (from `NextBuild-current.zip`: `NextBuildv5/ZXBC/library/`) to `zxbasic/library/`.

#### Installation with two emulators

If you also want the option to compile and launch with the emulators, expand the directory structure like this:

    vscode_zx/
       |
       +--CSpect/
       +--ZEsarUX/
       +--zesaruxrc (zesaruxwinrc for Windows)
       +--zxbasic/
       |
       +--Projects/
       |     |
       |     +--.vscode/
       |           |
       |           +--tasks.json
       |
       +--rennextbasic.py
       +--txt2nextbasic.py
       +--zxn_renumber.sh (zxn_renumber.bat for Windows)
       +--zxb_build.sh  (zxb_build.bat for Windows)
       |
       +--hdfmonkey  (hdfmonkey.exe for Windows)

...and extract in `CSpect/` and `ZEsarUX/` both emulators (on MacOS, copy ZEsarUX app next to `zxb_build.sh`).

Now we have to set up the virtual SD card for each emulator.

##### CSpect configuration

After obtaining an SD image file, rename it as `systemnext.img`, and copy to `CSpect/` directory, with the files `enNextZX.rom` and `enNxtmmc.rom`. (Read [here](https://www.specnext.com/latestdistro/) and [here](http://www.zxspectrumnext.online/cspect/) to download).

Create the SD directory where the compiled software will be put:

    cd /(...)/vscode_zx/
    hdfmonkey mkdir ./CSpect/systemnext.img /devel

Optionally, using `hdfmonkey`, we can replace the original distro `autoexec.bat` for the one availble in `ToInstall/autoexec.bas`. For example:

    hdfmonkey put ./CSpect/systemnext.img ./ToInstall/autoexec.bat /nextzxos/autoexec.bas

##### ZEsarUX Configuration

Edit the file `zesaruxrc` (`zesaruxwinrc` for Windows), writing after `--mmc-file` the full path to the file `tbblue.mmc`.

You can use the file that comes with the emulator distribution. If you prefer using another one, change its name to `tbblue.mmc`, and copy to `ZEsarUX/` directory.

The, create the structure in the virtual SD where the compiled software will be copied:

    cd /(...)/vscode_zx/
    hdfmonkey mkdir ./ZEsarUX/tbblue.mmc /devel

If you are using MacOS:

    cd /(...)/vscode_zx/
    hdfmonkey mkdir ./ZEsarUX.app/Contents/Resources/tbblue.mmc /devel

Optionally, using `hdfmonkey`, we can replace the original distro `autoexec.bat` for the one availble in `ToInstall/autoexec.bas`. For example:

    hdfmonkey put ./ZEsarUX/tbblue.mmc ./ToInstall/autoexec.bat /nextzxos/autoexec.bas

On MacOS:

    hdfmonkey put ./ZEsarUX.app/Contents/Resources/tbblue.mmc ./ToInstall/autoexec.bat /nextzxos/autoexec.bas

### How to use

**NOTE**: Please read the included PDF manual. The following is only a small part of what can be done with this tools.

#### BAS Files

The tasks and scripts are designed to deal with text files, with `.bas` extension, and encoded using UTF-8, with windows line endings (CRLF).

NextBASIC keywords must be written always in uppercase (this offers compatibility with programs that use variable names similar to keywords).

You can use [unicode block elements](https://en.wikipedia.org/wiki/Block_Elements) which will be automatically converted. Also , it is possible to have non-printable characters.

**NOTE**: To launch any of the following tasks, you have to use menu option `Terminal->Run Build Task...` or the equivalente keyboard shortcut (for example: Command+Shitf+B on MacOS).

#### Renumbering

Open the directory "Projects" with Visual Studio Code.

The `tasks.json` file creates a Visual Studio Code task named `Renumber NextBASIC`. When invoked with a `.bas` text file selected, tries to renumber the source code content.

#### Compiling

Open the directory "Projects" with Visual Studio Code.

The `tasks.json` file creates a couple of Visual Studio Code tasks named `Build ZX Basic` and `Build NextBASIC` that, when invoked with a `.bas` text file selected, creates a `build` directory and, inside of this, a `.bin` file with the compiled program if ZX Basic was selected, or a `.bas` file if NextBASIC. Also, in the case of ZX Basic, a launcher  `.bas` file is created, so it can be launched from the ZX Next Browser, ESXDOS o +3e DOS.

#### Compiling and executing with emulator

For each of the compiling options, there are also two other tasks named `Build ... And Run (CSpect)` and `Build ... And Run (ZEsarUX)` which can be used to compile, copy the new created files (`.bas` and, possibly, `.bin`) inside the virtual SD for the selected emulator, and then launch the emulator. If the `autoexec.bas` file has also been changed, a small BASIC program will start, where, pressing any key but BREAK will try to start the new program. If you press BREAK, ZX Next browser will be launched instead.

---

Tareas y scripts de Visual Studio Code para el desarrollo en NextBASIC y ZX Basic

Características:

- Conversor de texto a ficheros `.bas` de NextBASIC
- Función para volver a numerar un listado de NextBASIC
- Formato automático de código NextBASIC (en pruebas - Beta)
- Conversión de [caracteres unicode de bloques](https://en.wikipedia.org/wiki/Block_Elements) a gráficos de bloques de Sinclair
- Soporte de caracteres no imprimibles usando ` como código de escape
- Tareas para compilar con ZX Basic
- Integración de tareas para compilar (o convertir) y ejecutar en los emuladores ZEsarUX y CSpect
- Funciona en Windows, MacOS y (teóricamente) Linux

Se recomienda usar junto con el plugin [ZX Spectrum BASIC syntax highlighting for Visual Studio Code](https://github.com/jsanjose/zxbasic-vscode) o [NextBASIC VSCode Syntax
](https://github.com/remy/vscode-nextbasic).

---

## Castellano

Se puede descargar un archivo ZIP con la última versión siguiendo [este enlace](https://github.com/kounch/vscode_zx/releases/latest)

### Software necesario

- **Visual Studio Code**. Documentación, descarga, etc. [aquí](https://code.visualstudio.com/)

- **Python (versión 3.6 o superior)**. Documentación, descarga, etc. [aquí](https://www.python.org/)

- **ZX Basic**. Documentación, descarga, etc. [aquí](https://zxbasic.readthedocs.io). Se necesita, al menos, la versión 1.8.10 (en formato .zip o .tar.gz)

- **NextLibs para ZX Basic**. Leer más [aquí](http://zxbasic.uk/nextbuild/the-nextlibs/). Descargar [aquí](http://zxbasic.uk/nextbuild/download/)

### Software opcional

- **hdfmonkey**. Descarga, [aquí](http://files.zxdemo.org/gasman/speccy/hdfmonkey/). Código fuente [aquí](https://github.com/gasman/hdfmonkey). Versión compilada para Windows [aquí](http://uto.speccy.org/)

- **CSpect**. La última versión en desarrollo se puede obtener [aquí](https://dailly.blogspot.com/)

- **ZEsarUX**. Documentación, descarga, etc. [aquí](https://github.com/chernandezba/zesarux)

### Instalación

#### Instalación Básica

Instalar Python 3 para el sistema operativo correspondiente. En el caso de Windows, asegurarse de que se incluye `py launcher` en las opciones de instalación.

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
       +--locale/
       |
       +--rennextbasic.py
       +--txt2nextbasic.py
       +--zxn_renumber.sh (zxn_renumber.bat si es Windows)
       +--zxb_build.sh  (zxb_build.bat en el caso de Windows)

El directorio `Projects` se puede renombrar, pero *ha de estar* al lado de `txt2nextbasic.py` y `zxb_build...`.

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
       +--locale/
       |
       +--rennextbasic.py
       +--txt2nextbasic.py
       +--zxn_renumber.sh (zxn_renumber.bat en Windows)
       +--zxb_build.sh  (zxb_build.bat para Windows)
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

**NOTA**: Por favor, lea el manual incluido en PDF. Lo que hay a continuación es una pequeña parte de lo que se puede hacer con estas herramientas.

#### Ficheros BAS

Las tareas y scripts están diseñados para tratar con ficheros de texto, con extensión `.bas`, con codificación UTF-8, con saltos de línea windows (CRLF).

Las palabras clave de NextBASIC deben estar siempre en mayúsculas (esto ofrece compatibilidad con programas que usan nombres de variable iguales a los nombres de alguna palabra clave).

Es posible utilizar [caracteres unicode de bloques](https://en.wikipedia.org/wiki/Block_Elements) que serán automáticamente convertidos, así como caracteres no imprimibles.

**NOTA**: Para ejecutar las tareas que se describen a continuación, se debe usar la opción de menú `Terminal->Run Build Task...` o la combinación de teclas equivalente (por ejemplo: Comando+Mayúsculas+B en MacOS).

#### Numeración de líneas

Abrir el directorio "Projects" (o con el nombre que se haya definido al instalar) desde Visual Studio Code.

El fichero `tasks.json` define una tarea de Visual Studio Code `Renumber NextBASIC` que, al ser invocada sobre un fichero `.bas` de texto, intentará ajustar de forma automática todos los números de línea del código.

#### Compilación

Abrir el directorio "Projects" (o con el nombre que se haya definido) desde Visual Studio Code.

El fichero `tasks.json` define varias tareas de Visual Studio Code `Build ZX Basic` y `Build NextBASIC` que, al ser invocadas sobre un fichero `.bas` de texto con código, creará un directorio `build` y, dentro de este, en el caso de NextBASIC, un fichero `.bas` con el programa y, en el caso de ZX Basic, un fichero `.bin` con el programa compilado, y un lanzador `.bas` para poder iniciarlo desde el navegador de ZX Next, ESXDOS o +3e DOS.

#### Compilación y ejecución en emulador

Existen otras dos tareas llamadas `Build ... And Run (CSpect)` y `Build .. And Run (ZEsarUX)` que sirven para realizar una compilación, copiar los dos archivos (`.bin` y `.bas`) en la SD virtual del emulador correspondiente, y luego lanzarlo. Si, además, se ha configurado el archivo `autoexec.bas`, se iniciará directamente un programa donde, pulsando cualquier tecla, excepto BREAK (Mayúsculas + Espacio), se intentará ejecutar el programa compilado. Si se pulsa BREAK, se saldrá al navegador de ZX Next.

---

## Copyright

Copyright (c) 2020-2022 kounch

Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE
