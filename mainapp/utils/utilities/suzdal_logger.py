import datetime
import threading
import queue
import requests
import os

import os
import datetime
import threading
import queue

class SuzdalLogger:
    LOG_DIR = "/var/log/doc"
    LOG_FILE = os.path.join(LOG_DIR, "app.log")
    SEMANA_FILE = os.path.join(LOG_DIR, "semana.log")

    log_queue = queue.Queue()
    _worker_started = False
    _lock = threading.Lock()

    @staticmethod
    def _get_current_week():
        """Devuelve el número de la semana actual como string: '2025-W24'"""
        now = datetime.datetime.now()
        year, week, _ = now.isocalendar()
        return f"{year}-W{week:02}"

    @staticmethod
    def _read_stored_week():
        try:
            if os.path.exists(SuzdalLogger.SEMANA_FILE):
                with open(SuzdalLogger.SEMANA_FILE, "r") as f:
                    return f.read().strip()
        except Exception:
            pass
        return None

    @staticmethod
    def _write_current_week(week_str):
        try:
            with open(SuzdalLogger.SEMANA_FILE, "w") as f:
                f.write(week_str)
        except Exception:
            pass

    @staticmethod
    def _worker():
        os.makedirs(SuzdalLogger.LOG_DIR, exist_ok=True)

        while True:
            message = SuzdalLogger.log_queue.get()
            if message is None:
                break

            try:
                current_week = SuzdalLogger._get_current_week()
                stored_week = SuzdalLogger._read_stored_week()

                if current_week != stored_week:
                    # Semana cambió: limpiar log y actualizar archivo de semana
                    try:
                        if os.path.exists(SuzdalLogger.LOG_FILE):
                            os.remove(SuzdalLogger.LOG_FILE)
                    except Exception:
                        pass
                    SuzdalLogger._write_current_week(current_week)

                now = datetime.datetime.now()
                timestamp = now.strftime("%H:%M:%S %d/%m/%Y")
                log_entry = f"{timestamp} {message}\n"

                with open(SuzdalLogger.LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(log_entry)

            except Exception:
                pass

            SuzdalLogger.log_queue.task_done()

    @staticmethod
    def log(message):
        with SuzdalLogger._lock:
            if not SuzdalLogger._worker_started:
                threading.Thread(target=SuzdalLogger._worker, daemon=True).start()
                SuzdalLogger._worker_started = True

        SuzdalLogger.log_queue.put(message)
