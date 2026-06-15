# Moodle Proctor — Python worker

Worker asíncrono para análisis facial en snapshots almacenados en Huawei SFS.

- **Repositorio:** https://github.com/Johnrivera7/moodle_proctor_python
- **Requiere:** Python 3.9+, OpenCV

## Instalación

```bash
git clone https://github.com/Johnrivera7/moodle_proctor_python.git /opt/moodle_proctor_python
cd /opt/moodle_proctor_python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Uso

### Daemon (recomendado)

```bash
python worker.py --storage /mnt/huawei-sfs/proctor
```

### systemd

```bash
cp moodle-proctor-worker.service /etc/systemd/system/
systemctl enable --now moodle-proctor-worker
```

### Una sola pasada (cron)

```bash
python worker.py --storage /mnt/huawei-sfs/proctor --once
```

### Análisis manual

```bash
python analyze_faces.py --image /path/snap.jpg --output /path/result.json
```

## Integración Moodle

1. En `local_moodle_proctor`: activar **Python analysis queue**
2. Moodle escribe jobs en `{storage}/analysis_queue/`
3. Worker escribe `{storage}/analysis_results/result_{id}.json`
4. Tarea programada Moodle importa resultados

## Salida JSON

```json
{
  "face_count": 2,
  "alert": true,
  "alert_reason": "multiple_faces"
}
```

## Licencia

GPL-3.0+
