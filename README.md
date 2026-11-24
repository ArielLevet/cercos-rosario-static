# Cercos Rosario

Sitio estático en HTML, CSS y un poco de JavaScript. Sin build ni dependencias en producción.

- `index.html`, `cercos-perimetrales.html`, `portones-puertas.html`, `construccion-general.html`, `contacto.html`, `404.html`
- `style.css`: todos los estilos
- `main.js`: menú móvil y visor de fotos (lightbox)
- `img/<categoría>/`: fotos WebP listas para la web (ampliada y `_thumb`)
- `originals/<categoría>/`: fotos originales (no van a Git; ver su README)
- `scripts/`: preparación de fotos
- `CNAME`, `sitemap.xml`, `robots.txt`, `site.webmanifest`: configuración del sitio

## Ver el sitio en local

```powershell
python -m http.server 8000
```

Abrir http://localhost:8000

## Agregar o cambiar fotos

Una sola vez, preparar Python y Pillow:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r scripts/requirements.txt
```

1. Copiar la foto a `originals/<categoría>/` (por ejemplo `originals/portones/porton10.jpg`).
2. Agregar su epígrafe en `scripts/captions.json` (clave = nombre sin extensión).
3. Ejecutar:

```powershell
.\.venv\Scripts\python.exe scripts/generate-photos.py
```

El script crea `nombre.webp` (hasta 1920 px, calidad 80) y `nombre_thumb.webp` (hasta 800 px de ancho),
y reescribe la galería de la página entre los marcadores `<!-- fotos:inicio -->` y `<!-- fotos:fin -->`.
No sobrescribe versiones existentes: para regenerar una foto, borrar sus dos `.webp` y volver a ejecutar.
No editar a mano lo que está entre los marcadores.

Las tarjetas de la portada (`index.html`) usan la primera miniatura de cada categoría; si se renombra esa foto, actualizar la ruta.

Se publica tal cual en GitHub Pages (dominio: www.cercosrosario.com.ar).
