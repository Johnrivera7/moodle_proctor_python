# Moodle Proctor — Python Worker

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-green?style=flat-square)](https://opencv.org)
[![License](https://img.shields.io/badge/License-GPL--3.0-blue?style=flat-square)](LICENSE)
[![Moodle](https://img.shields.io/badge/Integrates-local__moodle__proctor-orange?style=flat-square&logo=moodle)](https://github.com/Johnrivera7/moodle_proctor)
[![Deploy](https://img.shields.io/badge/Deploy-systemd%20%7C%20cron-lightgrey?style=flat-square)](#systemd-recomendado)

Worker **independiente** para análisis facial en snapshots. Se comunica con Moodle **solo vía disco compartido (SFS)** — no es un plugin Moodle.

| | |
|---|---|
| **Repositorio** | https://github.com/Johnrivera7/moodle_proctor_python |
| **Autor** | [John Rivera](https://github.com/Johnrivera7) |
| **Integración** | Cola JSON en Huawei SFS |

> 🐍 **Separado a propósito** — corre en el servidor Huawei, no dentro de PHP/Moodle.

---

## Requisitos

| Requisito | Versión |
|-----------|---------|
| Python | 3.9+ |
| pip | Cualquier reciente |
| OpenCV | `opencv-python-headless` ≥ 4.8 |
| SFS | Misma ruta que `local_moodle_proctor` → Storage path |

---

## Instalación

```bash
git clone -b MOODLE_45 https://github.com/Johnrivera7/moodle_proctor_python.git /opt/moodle_proctor_python
cd /opt/moodle_proctor_python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Configuración en Moodle

**Administración → Plugins locales → Moodle Proctor**

- ✅ **Enable face analysis**
- ✅ **Enable Python analysis queue**

La ruta SFS debe ser **idéntica** en Moodle y en el worker.

---

## Uso

### Daemon continuo

```bash
python worker.py --storage /mnt/huawei-sfs/proctor
```

### Una pasada (cron cada minuto)

```bash
python worker.py --storage /mnt/huawei-sfs/proctor --once
```

### Análisis manual

```bash
python analyze_faces.py \
  --image /mnt/huawei-sfs/proctor/sessions/1/2/3/snap_0001.jpg \
  --output /tmp/result.json
```

---

## systemd (recomendado)

```bash
sudo cp moodle-proctor-worker.service /etc/systemd/system/
# Editar ExecStart con tu ruta SFS y venv
sudo systemctl enable --now moodle-proctor-worker
sudo systemctl status moodle-proctor-worker
```

---

## Flujo de datos

```
Moodle guarda snap.jpg
       ↓
Escribe analysis_queue/job_{id}.json
       ↓
Python worker procesa imagen
       ↓
Escribe analysis_results/result_{id}.json
       ↓
Tarea programada Moodle importa face_count
```

---

## Salida JSON

```json
{
  "face_count": 2,
  "alert": true,
  "alert_reason": "multiple_faces",
  "snapshotid": 42,
  "processed": 1718467200
}
```

| `face_count` | Significado |
|:------------:|-------------|
| `0` | No detecta rostro — alerta |
| `1` | OK |
| `≥ 2` | Múltiples personas — alerta crítica |

---

## Suite Moodle Proctor

| Repo | Rol |
|------|-----|
| [moodle_proctor](https://github.com/Johnrivera7/moodle_proctor) | Genera cola + importa resultados |
| **moodle_proctor_python** | ← Este worker |
| [moodle_quizaccess_proctor](https://github.com/Johnrivera7/moodle_quizaccess_proctor) | Captura webcam |
| [moodle_block_proctor](https://github.com/Johnrivera7/moodle_block_proctor) | Bloque curso |
| [moodle_proctor_extension](https://github.com/Johnrivera7/moodle_proctor_extension) | Extensión |

---

## Licencia

GPL-3.0+ — [LICENSE](LICENSE)
