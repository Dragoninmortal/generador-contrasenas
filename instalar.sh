#!/usr/bin/env bash
#
# Instala el lanzador de menú para el usuario actual, usando rutas absolutas
# derivadas de $HOME (o de donde esté clonado el repositorio).
#
# Uso:  ./instalar.sh
#
set -e

# Directorio donde está este script (el repo), sin depender de dónde se llame.
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

APP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"

mkdir -p "$APP_DIR" "$ICON_DIR"

# Asegura que el programa es ejecutable
chmod +x "$REPO_DIR/generador.py"

# Copia el icono al tema de iconos del usuario
cp "$REPO_DIR/icono.svg" "$ICON_DIR/generador-contrasenas.svg"

# Genera el .desktop con la ruta real de ESTE usuario
cat > "$APP_DIR/generador-contrasenas.desktop" <<EOF
[Desktop Entry]
Type=Application
Version=1.0
Name=Generador de Contraseñas
Name[en]=Password Generator
Comment=Genera contraseñas combinando tus datos con aleatoriedad segura
Comment[en]=Generate passwords by combining your data with secure randomness
Exec="$REPO_DIR/generador.py"
Icon=generador-contrasenas
Terminal=false
Categories=Utility;Security;
Keywords=password;contraseña;generador;seguridad;security;
StartupNotify=true
EOF

chmod +x "$APP_DIR/generador-contrasenas.desktop"

# Actualiza las cachés del escritorio
update-desktop-database "$APP_DIR" 2>/dev/null || true
gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true

echo "✓ Lanzador instalado: $APP_DIR/generador-contrasenas.desktop"
echo "  Programa:  $REPO_DIR/generador.py"
echo "  Icono:     $ICON_DIR/generador-contrasenas.svg"
echo
echo "Busca 'Generador de Contraseñas' en el menú de aplicaciones."
