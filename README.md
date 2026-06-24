# Moodle Proctor — Python Worker

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-green?style=flat-square)](https://opencv.org)
[![Moodle](https://img.shields.io/badge/Moodle-5.2%2B-orange?style=flat-square&logo=moodle)](https://moodle.org)
[![Branch](https://img.shields.io/badge/Branch-MOODLE__52-green?style=flat-square)](https://github.com/Johnrivera7/moodle_proctor_python/tree/MOODLE_52)
[![License](https://img.shields.io/badge/License-GPL--3.0-blue?style=flat-square)](LICENSE)

Worker **independiente** para análisis facial (conteo de rostros en capturas). Compatible con **`local_moodle_proctor`** rama **MOODLE_52** (Moodle 5.2+ / PHP 8.5+).

| | |
|---|---|
| **Autor** | [John Rivera](https://github.com/Johnrivera7) |
| **Contacto** | [johnriveragonzalez7@gmail.com](mailto:johnriveragonzalez7@gmail.com) |
| **Repositorio** | https://github.com/Johnrivera7/moodle_proctor_python |
| **Rama** | **`MOODLE_52`** |
| **Integración** | Cola JSON en la misma ruta de almacenamiento que Moodle |

> Moodle 4.5: rama [`MOODLE_45`](https://github.com/Johnrivera7/moodle_proctor_python/tree/MOODLE_45)

---

## ¿Dónde se instala?

| Escenario | Recomendación |
|-----------|---------------|
| **Un solo servidor Moodle** | ✅ Instalar **en el mismo servidor** (opción más simple) |
| **Varios nodos web + SFS/NFS** | Instalar en **cualquier nodo** que monte la misma ruta, o en el servidor de archivos |
| **Desarrollo local** | Misma máquina que Herd/Valet/Docker con `/tmp/moodle_proctor` |

El worker **no expone puertos HTTP**. Solo lee/escribe archivos JSON e imágenes en la carpeta configurada en Moodle (**Storage path**). Por eso puede convivir en el mismo servidor sin conflictos con Apache/Nginx/PHP-FPM.

### Ruta compartida (plugin → Python automático)

| Paso | Quién | Qué pasa |
|------|-------|----------|
| 1 | **Admin Moodle** | Guarda **Storage path** = `/mnt/storage/{moodlehost}` |
| 2 | **Plugin local** | Escribe `/var/lib/moodle_proctor/worker.json` con la ruta resuelta |
| 3 | **Worker Python** | Lee ese JSON al iniciar — **sin `--storage` en systemd** |

Ejemplo del JSON que genera Moodle:

```json
{
  "storage": "/mnt/storage/campus.ejemplo.cl",
  "storage_template": "/mnt/storage/{moodlehost}",
  "wwwroot": "https://campus.ejemplo.cl",
  "updated": 1719234567
}
```

Prioridad en Python: `--storage` (override) → variable `MOODLE_PROCTOR_STORAGE` → `worker.json`.

Preparación única del servidor:

```bash
sudo mkdir -p /var/lib/moodle_proctor /mnt/storage
sudo chown www-data:www-data /var/lib/moodle_proctor /mnt/storage
```

Luego **guardar ajustes** en Moodle Proctor y arrancar el worker.

---

## Requisitos

| Requisito | Versión |
|-----------|---------|
| Python | 3.9+ |
| OpenCV | `opencv-python-headless` ≥ 4.8 |
| Moodle (suite) | **5.2+** con [`local_moodle_proctor`](https://github.com/Johnrivera7/moodle_proctor) **v1.4.0+** |
| Ruta de almacenamiento | **La misma ruta resuelta** que en Moodle (ej. `/mnt/storage/campus.ejemplo.cl`) |
| Usuario del servicio | Debe poder **leer/escribir** esa ruta (`www-data` en Debian/Ubuntu) |

---

## Instalación en el mismo servidor que Moodle

Supongamos Moodle instalado en `/var/www/moodle` y storage path configurado como `/mnt/storage/{moodlehost}`.

### 1 · Clonar el worker

```bash
sudo git clone -b MOODLE_52 https://github.com/Johnrivera7/moodle_proctor_python.git /opt/moodle_proctor_python
cd /opt/moodle_proctor_python
```

### 2 · Entorno virtual e dependencias

```bash
sudo python3 -m venv venv
sudo ./venv/bin/pip install -r requirements.txt
```

### 3 · Generar config desde Moodle

En **Administración → Plugins locales → Moodle Proctor**, guarde los ajustes de almacenamiento. El plugin escribe:

```
/var/lib/moodle_proctor/worker.json
```

Compruebe el bloque **Sincronización con Python** (debe mostrar ruta OK).

### 4 · Probar manualmente (sin --storage)

```bash
sudo -u www-data /opt/moodle_proctor_python/venv/bin/python \
  /opt/moodle_proctor_python/worker.py --once
```

### 5 · Servicio systemd (sin configurar ruta en Python)

```ini
ExecStart=/opt/moodle_proctor_python/venv/bin/python /opt/moodle_proctor_python/worker.py
```

Activar:

```bash
sudo cp /opt/moodle_proctor_python/moodle-proctor-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now moodle-proctor-worker
```

Override manual opcional: `--storage /ruta` o `MOODLE_PROCTOR_STORAGE=/ruta`.

**Administración → Plugins locales → Moodle Proctor**

| Ajuste | Valor |
|--------|-------|
| **Habilitar cola de análisis Python** | Sí |
| **Habilitar análisis facial** | Sí |

El cron de Moodle importa resultados desde `analysis_results/` mediante la tarea programada del plugin.

---

## Instalación alternativa (cron cada minuto)

Si prefiere no usar systemd:

```bash
# crontab -u www-data -e
* * * * * /opt/moodle_proctor_python/venv/bin/python /opt/moodle_proctor_python/worker.py --once
```

---

## Desarrollo / prueba local

```bash
git clone -b MOODLE_52 https://github.com/Johnrivera7/moodle_proctor_python.git
cd moodle_proctor_python
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Misma ruta que en admin Moodle (ej. /tmp/moodle_proctor)
python worker.py --storage /tmp/moodle_proctor --once
```

---

## Cómo funciona la integración

```
Moodle (captura webcam)
       ↓
Escribe imagen en storage/sessions/...
       ↓
Escribe job JSON en storage/analysis_queue/job_N.json
       ↓
Worker Python (mismo servidor o nodo con SFS)
       ↓
Detecta caras → storage/analysis_results/result_N.json
       ↓
Cron Moodle → importa alertas (0, 1 o múltiples rostros)
```

---

## Permisos recomendados

```bash
# Ruta base (Moodle crea la subcarpeta del sitio)
sudo chown -R www-data:www-data /mnt/proctoring
sudo chmod -R 770 /mnt/proctoring

# Código del worker
sudo chown -R root:www-data /opt/moodle_proctor_python
sudo chmod -R 750 /opt/moodle_proctor_python
```

Tanto **PHP (Moodle)** como el **worker Python** deben ejecutarse como usuario con acceso de lectura/escritura a la misma carpeta de storage.

---

## Suite MOODLE_52

| Repo | Rol |
|------|-----|
| [moodle_proctor](https://github.com/Johnrivera7/moodle_proctor/tree/MOODLE_52) | Cola + import |
| **moodle_proctor_python** | ← Worker |
| [moodle_quizaccess_proctor](https://github.com/Johnrivera7/moodle_quizaccess_proctor/tree/MOODLE_52) | Capturas |
| [moodle_block_proctor](https://github.com/Johnrivera7/moodle_block_proctor/tree/MOODLE_52) | Bloque |
| [moodle_proctor_extension](https://github.com/Johnrivera7/moodle_proctor_extension/tree/MOODLE_52) | Extensión |

---

## Licencia

GPL-3.0+ — [LICENSE](LICENSE)

## Soporte

- **Autor:** [John Rivera](https://github.com/Johnrivera7) · [johnriveragonzalez7@gmail.com](mailto:johnriveragonzalez7@gmail.com)
- **Issues:** https://github.com/Johnrivera7/moodle_proctor_python/issues
