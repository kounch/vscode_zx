# vscode_zx Examples

Some NextBASIC code examples

---

## English

These examples show the use of some of vscode zs (like copying more than one file to an emulator) and also some of the new features of NextBASIC.

### NextLayer2Scroll

Two examples that load an image into layer 2, and then move the layer. The first one calculates the coordinates on every frame, the second one precalculates the coordinates into an array, and then does the animation, showing that layer operations are very fast.

### NextSprite

Two examples that move a group of sprites loaded from a file. The first one only uses the standard NextBASIC commands to load and move the sprites. The second one uses REG commands to create an anchor and relative sprites before moving them, which is faster and removes tearing. At this moment the last one only works fine with CSpect emulator and not ZesarUX.

See Chapter 23 of the manual for more information about the registers that are being used.

### Blocks

A simple program that shows how txt2nexbasic can convert UTF block images to Sinclair Block characters.

### Ellipses

Small classic program with calculations and plotting that gets better when increasing the clock speed of the ZX Next.

---

## Castellano

Estos ejemplos demuestran algunas de las capacidades de los scripts de vscode_zx ( por ej. copia de varios ficheros al emulador) y de las nuevas características de NextBASIC.

### Next Layer2Scroll

Dos ejemplos que cargan una imagen la capa 2 (layer 2) y luego la mueven. El primer ejemplo calcula las coordenadas en cada fotograma, mientras que la segunda hace el cálculo primero y guarda las coordenadas en una matriz, mostrando cómo las operaciones de capa son realmente rápidas.

### Next Sprite

Dos ejemplos que mueven grupo de sprites cargados desde fichero. El primero sólo utiliza los comandos de NextBASIC estándar para manipular sprites. El segundo usa el comando REG para crear un sprite ancla y otros relaivos a él, antes de moverlos, lo que es mucho más rápido y fluido. Este último sólo funciona bien en este momento con el emulador CSpect, y no con ZesarUX.

Se puede consultar el capítulo 23 del manual para ver más informaciñon sobre los registros que se utilizan.

### Bloques

Un programa sencillo que demuestra cómo se convierten imágenes UTF de bloques en caracteres de bloque de Sinclair ASCII.

### Elipses

Pequeño programa clásico de Spectrum con cálculos y dibujo en pantalla, que mejora al incrementar la velocidad de reloj del ZX Next.

---

## Copyright

Copyright (c) 2020-2021 kounch

Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE
