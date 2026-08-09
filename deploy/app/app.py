"""
Servicio de demostración instrumentado con Dynatrace OneAgent.

Expone endpoints de tráfico "normal" y endpoints /chaos/* que simulan
anomalías de sistema operativo (pico de CPU, pico de memoria) para que
Davis AI tenga comportamientos anómalos reales que detectar.

Uso exclusivo de demostración académica: los endpoints de caos no deben
exponerse en un despliegue real.
"""
import os
import socket
import time
import random
import threading

import redis
from flask import Flask, jsonify, request

app = Flask(__name__)

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

HOSTNAME = socket.gethostname()

# memoria retenida deliberadamente para simular un pico/fuga durante la
# ventana de la demo de caos
_chaos_memory_blocks = []


@app.get("/")
def index():
    return jsonify(service="app", hostname=HOSTNAME, status="ok")


@app.get("/health")
def health():
    return jsonify(status="healthy", hostname=HOSTNAME), 200


@app.get("/work")
def work():
    """Simula trabajo normal: latencia variable + contador en redis."""
    delay = random.uniform(0.01, 0.15)
    time.sleep(delay)
    count = r.incr(f"requests:{HOSTNAME}")
    return jsonify(hostname=HOSTNAME, delay_ms=round(delay * 1000, 1), count=count)


def _burn_cpu(seconds: float):
    end = time.time() + seconds
    while time.time() < end:
        # trabajo intencionalmente inútil para saturar un núcleo de CPU
        pow(1234567, 1000, 999999937)


@app.post("/chaos/cpu")
def chaos_cpu():
    """Genera un pico de CPU controlado para que Davis AI lo detecte."""
    duration = float(request.args.get("seconds", 30))
    threads = int(request.args.get("threads", os.cpu_count() or 1))
    for _ in range(threads):
        threading.Thread(target=_burn_cpu, args=(duration,), daemon=True).start()
    return jsonify(hostname=HOSTNAME, chaos="cpu", duration_seconds=duration, threads=threads)


@app.post("/chaos/memory")
def chaos_memory():
    """Genera un pico de memoria controlado (bloques retenidos en memoria)."""
    megabytes = int(request.args.get("mb", 256))
    block = bytearray(megabytes * 1024 * 1024)
    _chaos_memory_blocks.append(block)
    return jsonify(hostname=HOSTNAME, chaos="memory", mb_allocated=megabytes,
                   total_blocks=len(_chaos_memory_blocks))


@app.post("/chaos/reset")
def chaos_reset():
    """Libera la memoria retenida por /chaos/memory."""
    _chaos_memory_blocks.clear()
    return jsonify(hostname=HOSTNAME, chaos="reset")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
