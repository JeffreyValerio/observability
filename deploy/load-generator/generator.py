"""
Generador de carga: produce tráfico normal contra el frontend y, con cierta
probabilidad, dispara los endpoints de caos para simular anomalías reales
que Davis AI (Dynatrace) debe detectar.
"""
import os
import random
import time

import requests

FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://frontend")
CHAOS_PROBABILITY = float(os.environ.get("CHAOS_PROBABILITY", "0.05"))
REQUEST_INTERVAL_SECONDS = float(os.environ.get("REQUEST_INTERVAL_SECONDS", "0.5"))


def normal_traffic():
    try:
        resp = requests.get(f"{FRONTEND_URL}/work", timeout=5)
        print(f"[normal] status={resp.status_code} body={resp.json()}", flush=True)
    except requests.RequestException as exc:
        print(f"[normal] error={exc}", flush=True)


def chaos_traffic():
    scenario = random.choice(["cpu", "memory"])
    try:
        if scenario == "cpu":
            resp = requests.post(f"{FRONTEND_URL}/chaos/cpu",
                                  params={"seconds": 20, "threads": 2}, timeout=5)
        else:
            resp = requests.post(f"{FRONTEND_URL}/chaos/memory",
                                  params={"mb": 256}, timeout=5)
        print(f"[chaos:{scenario}] status={resp.status_code} body={resp.json()}", flush=True)
    except requests.RequestException as exc:
        print(f"[chaos:{scenario}] error={exc}", flush=True)


def main():
    print(f"load-generator targeting {FRONTEND_URL} "
          f"(chaos_probability={CHAOS_PROBABILITY})", flush=True)
    while True:
        if random.random() < CHAOS_PROBABILITY:
            chaos_traffic()
        else:
            normal_traffic()
        time.sleep(REQUEST_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
