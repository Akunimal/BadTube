<p align="center">
  <img src="assets/badtube_logo.jpg" alt="BadTube Logo" width="320" />
</p>

<h1 align="center">BadTube</h1>

<p align="center">
  <strong>Cliente nativo para Android de YouTube y YouTube Music</strong><br>
  Formato móvil vertical (portrait), bloqueo integral de anuncios, reproducción en segundo plano y pantalla apagada, SponsorBlock y DeArrow integrados, con soporte para inicio de sesión en cuentas Google sin root.
</p>

<p align="center">
  <a href="https://github.com/Akunimal/BadTube/releases/latest"><img src="https://img.shields.io/github/v/release/Akunimal/BadTube?style=for-the-badge&color=e50914" alt="Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-GPL%203.0-blue.svg?style=for-the-badge" alt="License"></a>
  <img src="https://img.shields.io/badge/Platform-Android%208.0%2B-green?style=for-the-badge" alt="Platform">
</p>

---

## ✨ Características Principales

- **Bloqueo Total de Publicidad**: Sin anuncios pre-roll, mid-roll, banners o patrocinios en feeds y búsquedas.
- **Reproducción en Segundo Plano y Audio-Only**: Continúa escuchando contenido con la app minimizada o la pantalla apagada.
- **Integración con SponsorBlock**: Salto automático o manual de segmentos patrocinados, intros, outros y solicitudes de suscripción.
- **Return YouTube Dislike (RYD)**: Restauración en tiempo real del contador de dislikes en videos.
- **Integración con DeArrow**: Títulos y miniaturas reemplazados por descripciones y capturas precisas comunitarias para evitar clickbait.
- **Controles Gestuales (Swipe Controls)**: Control de brillo y volumen deslizando sobre los costados de la pantalla en modo horizontal.
- **Experiencia Móvil 100% Nativa**: Orientación vertical estándar, teclado táctil Android (IME) totalmente funcional, navegación nativa de Shorts y comentarios.
- **Inicio de Sesión en Cuentas Google (Non-Root)**: Compatible con cuentas Google mediante [GmsCore / MicroG](https://github.com/ReVanced/GmsCore), sin requerir root en el dispositivo.
- **Rebranding BadTube**: Identidad visual propia en la interfaz y lanzador de aplicaciones.

---

## 📲 Instalación en Android

### 1. Instalar GmsCore (Requerido para no-root)
Para que BadTube pueda autenticar tu cuenta y gestionar streams de video sin depender de los servicios cerrados de Google Play Services:
1. Descarga el APK firmado desde [ReVanced GmsCore Releases](https://github.com/ReVanced/GmsCore/releases/latest).
2. Instala el APK (`app.revanced.android.gms-*-signed.apk`) en tu teléfono.
3. Desactiva la optimización de batería para GmsCore si el sistema lo solicita.

### 2. Instalar BadTube
1. Descarga la última versión de `BadTube-*.apk` desde la sección [Releases](https://github.com/Akunimal/BadTube/releases/latest).
2. Abre el archivo APK e instálalo.
3. Abre BadTube y disfruta de la experiencia sin anuncios.

---

## 🛠️ Compilación y Parcheo Local

BadTube utiliza un pipeline determinista de inyección de bytecode (Dexlib2/Smali) sobre el APK base stock oficial compatible (`20.05.46`).

### Requisitos Previos
- **Java JRE / JDK 17+**
- **Android SDK Build Tools** (`apksigner`, `zipalign`)
- **Python 3.10+**

### Ejecución del Builder

Clona el repositorio:
```bash
git clone https://github.com/Akunimal/BadTube.git
cd BadTube
```

Ejecuta el script automatizado:
```bash
python scripts/build.py
```

El script se encarga de:
1. Validar las dependencias locales y herramientas (`revanced-cli`, `patches.rvp`).
2. Verificar el APK base compatible (`nodpi universal`).
3. Inyectar el bundle de parches y los iconos personalizados de BadTube.
4. Alinear y firmar el APK final con esquemas V2 y V3.
5. Dejar el APK compilado listo en `dist/BadTube-latest.apk`.

---

## 🤖 CI / CD (GitHub Actions)

Este repositorio cuenta con un flujo de integración continua en `.github/workflows/build.yml` que:
- Descarga los componentes necesarios.
- Compila y firma automáticamente el APK de BadTube.
- Publica los binarios listos para descargar en cada nuevo release o tag.

---

## 📄 Licencia

Este proyecto está bajo la licencia **GNU General Public License v3.0**. Consulta [LICENSE](LICENSE) para más detalles.
