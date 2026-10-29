import subprocess
import platform
import concurrent.futures
from datetime import datetime

def ping_host(ip):
    """
    Hace un ping a una IP específica dependiendo del sistema operativo.
    Retorna la IP si está activa, o None si no responde.
    """
    # Detectar el sistema operativo para ajustar el comando ping
    param = "-n" if platform.system().lower() == "windows" else "-c"
    timeout_param = "-w" if platform.system().lower() == "windows" else "-W"
    
    # Un ping rápido con timeout de 1 segundo
    command = ["ping", param, "1", timeout_param, "1", ip]
    
    try:
        # Ejecutar el comando silenciosamente
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode == 0:
            return ip
    except Exception:
        pass
    return None

def scan_network(base_ip):
    """
    Escanea la subred (ej. 192.168.1.0/24) usando concurrencia para que sea rápido.
    """
    print(f"[*] Iniciando escaneo en la red: {base_ip}.1 al {base_ip}.254 a las {datetime.now().strftime('%H:%M:%S')}")
    active_hosts = []
    
    # Generar las IPs del .1 al .254
    ip_list = [f"{base_ip}.{i}" for i in range(1, 255)]
    
    # Usar ThreadPoolExecutor para lanzar pings en paralelo (súper rápido)
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(ping_host, ip_list)
        
    for ip in results:
        if ip:
            active_hosts.append(ip)
            print(f"[+] ¡Dispositivo activo encontrado!: {ip}")
            
    return active_hosts

if __name__ == "__main__":
    # Cambia esto según tu subred local (por ejemplo, si tu router es 192.168.1.1, pon "192.168.1")
    # O puedes usar "127.0.0" para pruebas locales rápidas.
    subnet = "192.168.1" 
    
    print("--- NETSCAN PY : FASE 1 ---")
    devices = scan_network(subnet)
    print(f"\n[✔] Escaneo finalizado. Total de dispositivos activos: {len(devices)}")
