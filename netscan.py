import subprocess
import platform
import concurrent.futures
from datetime import datetime
import psycopg2

# Configuración de la Base de Datos PostgreSQL
DB_CONFIG = {
    "dbname": "homelab_db",
    "user": "postgres",       # Cambia esto por tu usuario de Postgres
    "password": "", # Cambia esto por tu contraseña
    "host": "localhost",      # Si luego lo pasas a un servidor del homelab, cambias esto por su IP
    "port": "5432"
}

def save_to_db(active_hosts):
    """
    Guarda los dispositivos activos encontrados en la base de datos PostgreSQL.
    """
    if not active_hosts:
        print("[!] No hay dispositivos para guardar en la base de datos.")
        return

    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("[*] Guardando resultados en PostgreSQL...")
        for ip in active_hosts:
            query = "INSERT INTO network_devices (ip_address, status) VALUES (%s, %s);"
            cursor.execute(query, (ip, "Active"))
            
        connection.commit()
        cursor.close()
        connection.close()
        print(f"[✔] {len(active_hosts)} dispositivos guardados exitosamente en la base de datos.")
        
    except Exception as error:
        print(f"[X] Error al conectar o guardar en la base de datos: {error}")

def ping_host(ip):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    timeout_param = "-w" if platform.system().lower() == "windows" else "-W"
    command = ["ping", param, "1", timeout_param, "1", ip]
    
    try:
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode == 0:
            return ip
    except Exception:
        pass
    return None

def scan_network(base_ip):
    print(f"[*] Iniciando escaneo en la red: {base_ip}.1 al {base_ip}.254 a las {datetime.now().strftime('%H:%M:%S')}")
    active_hosts = []
    
    ip_list = [f"{base_ip}.{i}" for i in range(1, 255)]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(ping_host, ip_list)
        
    for ip in results:
        if ip:
            active_hosts.append(ip)
            print(f"[+] ¡Dispositivo activo encontrado!: {ip}")
            
    return active_hosts

if __name__ == "__main__":
    subnet = "192.168.1"  # Cambia según tu subred local
    
    print("--- NETSCAN PY : FASE 2 ---")
    devices = scan_network(subnet)
    print(f"\n[✔] Escaneo finalizado. Total de dispositivos activos: {len(devices)}")
    
    # Llamamos a la función para guardar en Postgres
    save_to_db(devices)
