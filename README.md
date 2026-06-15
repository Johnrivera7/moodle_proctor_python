# Moodle Proctor — Python Worker

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-green?style=flat-square)](https://opencv.org)
[![Moodle](https://img.shields.io/badge/Moodle-5.2%2B-orange?style=flat-square&logo=moodle)](https://moodle.org)
[![Branch](https://img.shields.io/badge/Branch-MOODLE__52-green?style=flat-square)](https://github.com/Johnrivera7/moodle_proctor_python/tree/MOODLE_52)
[![License](https://img.shields.io/badge/License-GPL--3.0-blue?style=flat-square)](LICENSE)

Worker **independiente** para análisis facial. Compatible con **`local_moodle_proctor`** rama **MOODLE_52** (Moodle 5.2+ / PHP 8.5+ en el servidor Moodle).

| | |
|---|---|
| **Repositorio** | https://github.com/Johnrivera7/moodle_proctor_python |
| **Rama** | **`MOODLE_52`** |
| **Integración** | Cola JSON en Huawei SFS |

> Moodle 4.5: rama [`MOODLE_45`](https://github.com/Johnrivera7/moodle_proctor_python/tree/MOODLE_45)

---

## Requisitos

| Requisito | Versión |
|-----------|---------|
| Python | 3.9+ |
| OpenCV | `opencv-python-headless` ≥ 4.8 |
| Moodle (suite) | **5.2+** con rama MOODLE_52 |
| SFS | Misma ruta que Storage path en Moodle |

---

## Instalación

```bash
git clone -b MOODLE_52 https://github.com/Johnrivera7/moodle_proctor_python.git /opt/moodle_proctor_python
cd /opt/moodle_proctor_python
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

---

## Uso

```bash
# Daemon
python worker.py --storage /mnt/huawei-sfs/proctor

# Cron
python worker.py --storage /mnt/huawei-sfs/proctor --once
```

### systemd

```bash
sudo cp moodle-proctor-worker.service /etc/systemd/system/
sudo systemctl enable --now moodle-proctor-worker
```

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
