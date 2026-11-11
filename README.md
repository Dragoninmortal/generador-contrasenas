# 🔐 Generador de Contraseñas (Parrot OS / Linux)

Generador de contraseñas que combina **tus datos** (nombre, fecha, palabra clave, número)
con **aleatoriedad criptográfica** para crear la contraseña.

## Contenido

| Archivo | Descripción |
|---|---|
| `generador.py` | App de escritorio nativa (Python + Tkinter). **Sin dependencias.** |
| `diccionario.py` | Generador de diccionarios (wordlist) estilo CUPP. Módulo + CLI. |
| `instalar.sh` | Instalador del lanzador de menú (usa tu `$HOME`). |
| `generador-contrasenas.desktop` | Lanzador genérico (usa `$HOME`) para el menú. |
| `icono.svg` | Icono de la aplicación. |
| `generador-contrasenas.html` | Versión web (opcional), abre en Firefox. |

## Cómo ejecutarla

**Opción 1 — Menú de Parrot**
Busca "Generador de Contraseñas" en el menú de aplicaciones y haz clic.

**Opción 2 — Terminal**
```bash
python3 ~/generador-contrasenas/generador.py
```
o directamente:
```bash
~/generador-contrasenas/generador.py
```

## Instalar desde GitHub (para cualquier usuario)

```bash
git clone https://github.com/Dragoninmortal/generador-contrasenas.git ~/generador-contrasenas
cd ~/generador-contrasenas
./instalar.sh
```

`instalar.sh` copia el icono al tema del usuario y crea el lanzador en
`~/.local/share/applications/` con la **ruta real** de tu equipo. Después aparecerá
"Generador de Contraseñas" en el menú.

> El `.desktop` incluido en el repo es **genérico** y usa `$HOME`, por lo que también
> funciona copiándolo a mano a `~/.local/share/applications/` **siempre que** hayas clonado
> el repositorio en `~/generador-contrasenas`. Si lo clonas en otra ruta, usa `./instalar.sh`.

## Qué hace

- **Datos de base:** nombre/usuario, fecha (dd/mm/aaaa), palabra clave, número/teléfono.
- **Opciones:** longitud (8–40), mayúsculas, minúsculas, números, símbolos,
  sustitución tipo *leet* (a→4, e→3, o→0…) e incluir o no tus datos.
- **Resultado:** botón de copiar al portapapeles y medidor de seguridad (bits de entropía).
- **Historial:** guarda las últimas 100 contraseñas generadas (la más reciente arriba).
  Puedes copiar cualquiera (selecciónala y pulsa *Copiar seleccionada*, o haz doble clic)
  y borrar todo con el botón *Borrar*.

> El historial vive **solo en memoria**: se borra al cerrar la app. No se escribe en disco
> a propósito, para no dejar contraseñas en texto plano guardadas en el equipo.

## Generador de diccionarios (wordlist)

Genera **muchas** contraseñas posibles a partir de tus datos (variantes, leet, años,
números, símbolos y combinaciones de palabras), como hace CUPP.

**Desde la app:** rellena los datos, ajusta *"Máx. contraseñas del diccionario"* y pulsa
**📚 Generar diccionario de contraseñas…**. Elige dónde guardar el `.txt`.

**Desde la terminal (CLI):**
```bash
python3 ~/generador-contrasenas/diccionario.py \
  --nombre Diego --palabra "montaña azul" --numero 2026 --fecha 1998-11-05 \
  -o ~/palabras.txt --max 500000
```

| Opción | Descripción |
|---|---|
| `--nombre` | Nombre o usuario |
| `--palabra` | Palabra clave o frase |
| `--numero` | Número o teléfono |
| `--fecha` | Fecha `AAAA-MM-DD` |
| `-o`, `--salida` | Archivo de salida (por defecto `diccionario.txt`) |
| `--max` | Máximo de contraseñas (`0` = sin límite) |

Cada línea del archivo es una contraseña única. Ejemplo de uso con herramientas de Parrot:

```bash
# con hashcat
hashcat -a 0 -m 0 hash.txt ~/palabras.txt

# con john
john --wordlist=~/palabras.txt hash.txt
```

## Seguridad

La contraseña **nunca es solo tus datos**: como máximo ocupan ~55% de la longitud;
el resto se rellena con `secrets` (aleatoriedad criptográfica del sistema) y luego todo se mezcla.
Aun así, para cuentas importantes usa contraseñas 100 % aleatorias y únicas, guardadas en un
gestor de contraseñas (KeePassXC viene incluido en Parrot).

> ⚠️ **Aviso legal:** el generador de diccionarios es una herramienta de auditoría.
> Úsalo **solo** contra sistemas, cuentas o hashes para los que tengas **autorización explícita**
> (tus propios equipos, laboratorios de práctica, CTF o auditorías contratadas). El uso no
> autorizado es ilegal.

## Desinstalar

```bash
rm -f ~/.local/share/applications/generador-contrasenas.desktop
rm -f ~/.local/share/icons/hicolor/scalable/apps/generador-contrasenas.svg
rm -rf ~/generador-contrasenas
```

## Licencia

Este proyecto está bajo la licencia **MIT**. Consulta el archivo [LICENSE](LICENSE).
