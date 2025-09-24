import os
import sys
import signal
import subprocess
import install_local_layers
import build_local_api
import build_api_json

def on_cancel():
    print("\n[+] Cancelado por el usuario. Ejecutando limpieza…")
def on_error(code: int):
    print(f"[!] El servidor terminó con error (código {code}).")

def on_ok():
    print("[✓] El servidor terminó normalmente.")

def main():
    cmd = [sys.executable, "-m", "fastapi", "dev", "dev_tools/main_server.py"]

    # Lanzamos el proceso para poder controlarlo en Ctrl+C
    proc = subprocess.Popen(cmd)

    try:
        proc.wait()  # Espera a que termine
    except KeyboardInterrupt:
        # Usuario presionó Ctrl+C: pedimos al hijo que se cierre y corremos tu bloque
        print("\n[!] Ctrl+C detectado. Deteniendo servidor…")
        if os.name == "nt":
            # En Windows manda CTRL_BREAK (más fiable que CTRL_C a veces)
            proc.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            proc.send_signal(signal.SIGINT)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        on_cancel()
        return

    # Si no fue KeyboardInterrupt, revisamos cómo terminó
    rc = proc.returncode
    if rc == 0:
        on_ok()
    elif rc < 0 and abs(rc) == signal.SIGINT:
        # Algunos entornos devuelven código negativo si terminó por SIGINT
        on_cancel()
    else:
        on_error(rc)

if __name__ == "__main__":
    main()
