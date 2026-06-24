# Moodle Proctor — Python Worker

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-green?style=flat-square)](https://opencv.org)
[![Moodle](https://img.shields.io/badge/Moodle-5.2%2B-orange?style=flat-square&logo=moodle)](https://moodle.org)
[![Branch](https://img.shields.io/badge/Branch-MOODLE__52-green?style=flat-square)](https://github.com/Johnrivera7/moodle_proctor_python/tree/MOODLE_52)
[![Version](https://img.shields.io/badge/Suite-1.4.1-informational?style=flat-square)](https://github.com/Johnrivera7/moodle_proctor)
[![License](https://img.shields.io/badge/License-GPL--3.0-blue?style=flat-square)](LICENSE)

Worker **independiente** para análisis facial (conteo de rostros en capturas). Compatible con **`local_moodle_proctor`** rama **MOODLE_52** (Moodle 5.2+ / PHP 8.5+).

| | |
|---|---|
| **Autor** | [John Rivera](https://github.com/Johnrivera7) |
| **Contacto** | [johnriveragonzalez7@gmail.com](mailto:johnriveragonzalez7@gmail.com) |
| **Repositorio** | https://github.com/Johnrivera7/moodle_proctor_python |
| **Rama** | **`MOODLE_52`** |
| **Integración** | Cola JSON en disco + `worker.json` generado por Moodle |

> Moodle 4.5: rama [`MOODLE_45`](https://github.com/Johnrivera7/moodle_proctor_python/tree/MOODLE_45)

---

## Cómo se integra (cola JSON en disco)

**No hay API HTTP.** Moodle y Python se comunican solo con archivos en la **misma ruta montada** — da igual si es disco local, NFS, NAS u otro almacenamiento compartido.

```mermaid
flowchart LR
    subgraph moodle [Moodle PHP]
        CAP[Captura webcam]
        ENQ[Encola job JSON]
        CRON[Cron importa resultados]
    end

    subgraph storage [Disco compartido]
        IMG[sessions/.../snap_N.jpg]
        JOB[analysis_queue/job_N.json]
        RES[analysis_results/result_N.json]
    end

    subgraph worker [Worker Python]
        READ[Lee job]
        CV[OpenCV face count]
        WRITE[Escribe result]
    end

    CAP --> IMG
    ENQ --> JOB
    READ --> JOB
    READ --> IMG
    CV --> WRITE
    WRITE --> RES
    CRON --> RES
```

```mermaid
sequenceDiagram
    autonumber
    participant M as Moodle
    participant D as Disco compartido
    participant W as worker.py

    M->>D: snap_0003.jpg + job_42.json
    loop cada N segundos
        W->>D: ¿Hay jobs pendientes?
        W->>D: Lee imagen + detecta rostros
        W->>D: result_42.json face_count alert
    end
    M->>D: Cron lee result_42.json
    M->>M: Marca snapshot + incidencia multiple_faces
```

---

## ¿Dónde se instala?

| Escenario | Recomendación |
|-----------|---------------|
| **Un solo servidor Moodle** | ✅ Instalar **en el mismo servidor** (opción más simple) |
| **Varios nodos web + disco compartido** | Instalar en **cualquier nodo** que monte la misma ruta |
| **Desarrollo local** | Misma máquina con `/tmp/moodle_proctor` |

El worker **no expone puertos**. Lee/escribe archivos en la carpeta que Moodle configura.

---

## Configuración automática (v1.4.1+)

**No configure la ruta en Python.** Moodle la exporta al guardar ajustes:

| Paso | Quién | Qué pasa |
|------|-------|----------|
| 1 | **Admin Moodle** | Guarda **Storage path** = `/mnt/storage/{moodlehost}` |
| 2 | **Plugin local** | Escribe `/var/lib/moodle_proctor/worker.json` |
| 3 | **Worker Python** | Lee ese JSON al iniciar — **sin `--storage` en systemd** |

```json
{
  "storage": "/mnt/storage/campus.ejemplo.cl",
  "storage_template": "/mnt/storage/{moodlehost}",
  "wwwroot": "https://campus.ejemplo.cl",
  "updated": 1719234567
}
```

**Prioridad en Python:** `--storage` (override) → `MOODLE_PROCTOR_STORAGE` → `worker.json`.

---

## Requisitos

| Requisito | Versión |
|-----------|---------|
| Python | 3.9+ |
| OpenCV | `opencv-python-headless` ≥ 4.8 |
| Moodle (suite) | **5.2+** con [`local_moodle_proctor`](https://github.com/Johnrivera7/moodle_proctor) **v1.4.1+** |
| Disco compartido | Misma ruta resuelta que Moodle (lectura/escritura `www-data`) |
| `worker.json` | Generado por Moodle al guardar ajustes |

---

## Instalación en el mismo servidor que Moodle

### 1 · Preparar carpetas

```bash
sudo mkdir -p /var/lib/moodle_proctor /mnt/storage
sudo chown www-data:www-data /var/lib/moodle_proctor /mnt/storage
sudo chmod 770 /var/lib/moodle_proctor /mnt/storage
```

### 2 · Clonar e instalar dependencias

```bash
sudo git clone -b MOODLE_52 https://github.com/Johnrivera7/moodle_proctor_python.git /opt/moodle_proctor_python
cd /opt/moodle_proctor_python
sudo python3 -m venv venv
sudo ./venv/bin/pip install -r requirements.txt
```

### 3 · Generar config desde Moodle

**Administración → Plugins locales → Moodle Proctor → Guardar.**

Comprobar **Sincronización con Python** = OK y que exista `/var/lib/moodle_proctor/worker.json`.

### 4 · Probar

```bash
sudo -u www-data /opt/moodle_proctor_python/venv/bin/python \
  /opt/moodle_proctor_python/worker.py --once
```

### 5 · Servicio systemd

El archivo incluido ya **no usa `--storage`**:

```bash
sudo cp /opt/moodle_proctor_python/moodle-proctor-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now moodle-proctor-worker
sudo journalctl -u moodle-proctor-worker -f
```

### 6 · Activar en Moodle

| Ajuste | Valor |
|--------|-------|
| **Habilitar cola de análisis Python** | Sí |
| **Habilitar análisis facial** | Sí |

---

## Cron alternativo (sin systemd)

```bash
# crontab -u www-data -e
* * * * * /opt/moodle_proctor_python/venv/bin/python /opt/moodle_proctor_python/worker.py --once
```

---

## Desarrollo local

```bash
git clone -b MOODLE_52 https://github.com/Johnrivera7/moodle_proctor_python.git
cd moodle_proctor_python
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Con worker.json de Moodle, o override:
python worker.py --storage /tmp/moodle_proctor --once
```

---

## Permisos

```bash
sudo chown -R www-data:www-data /mnt/storage /var/lib/moodle_proctor
sudo chmod -R 770 /mnt/storage /var/lib/moodle_proctor
sudo chown -R root:www-data /opt/moodle_proctor_python
sudo chmod -R 750 /opt/moodle_proctor_python
```

---

## Suite MOODLE_52

| Repo | Rol |
|------|-----|
| [moodle_proctor](https://github.com/Johnrivera7/moodle_proctor/tree/MOODLE_52) | Cola + `worker.json` |
| **moodle_proctor_python** | ← Worker |
| [moodle_quizaccess_proctor](https://github.com/Johnrivera7/moodle_quizaccess_proctor/tree/MOODLE_52) | Capturas |
| [moodle_block_proctor](https://github.com/Johnrivera7/moodle_block_proctor/tree/MOODLE_52) | Bloque |
| [moodle_proctor_extension](https://github.com/Johnrivera7/moodle_proctor_extension/tree/MOODLE_52) | Extensión |

Diagramas completos de arquitectura: [README del núcleo](https://github.com/Johnrivera7/moodle_proctor/blob/MOODLE_52/README.md).

---

## Licencia

GPL-3.0+ — [LICENSE](LICENSE)

## Soporte

- **Autor:** [John Rivera](https://github.com/Johnrivera7) · [johnriveragonzalez7@gmail.com](mailto:johnriveragonzalez7@gmail.com)
- **Issues:** https://github.com/Johnrivera7/moodle_proctor_python/issues
