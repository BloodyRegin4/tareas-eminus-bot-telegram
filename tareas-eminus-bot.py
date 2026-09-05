import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import json
import os

# --- CONFIGURACIÓN DE RUTAS ---
DIRECTORIO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(DIRECTORIO_SCRIPT, "config_eminus.json")
SESSION_FILE = os.path.join(DIRECTORIO_SCRIPT, ".token_cache")
URL_BASE_API = "https://eminus.uv.mx/eminusapi8/api/Activity/getActividadesEstudiante/"

# --- CARGA DE DATOS SEGUROS (NUBE VS LOCAL) ---
USERNAME = os.environ.get("EMINUS_USER")
PASSWORD = os.environ.get("EMINUS_PASS")
TOKEN_TELEGRAM = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
materias_json_str = os.environ.get("EMINUS_MATERIAS")

MATERIAS = {}

# Si USERNAME no existe, significa que estamos corriendo localmente (no en GitHub)
if not USERNAME:
    if not os.path.exists(CONFIG_FILE):
        print("Error: No se encontró config_eminus.json ni Secrets de GitHub.")
        exit()
    
    # Leemos tu archivo local
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        creds = json.load(f)
        USERNAME = creds.get("username")
        PASSWORD = creds.get("password")
        TOKEN_TELEGRAM = creds.get("telegram_token")
        CHAT_ID = creds.get("telegram_chat_id")
        MATERIAS = creds.get("materias", {})
else:
    # Si estamos en GitHub, convertimos el string del Secret a diccionario
    MATERIAS = json.loads(materias_json_str) if materias_json_str else {}

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    try:
        res = requests.post(url, json=payload)
        res.raise_for_status()
        print("Mensaje de Telegram enviado exitosamente.")
    except Exception as e:
        print(f"Error al enviar mensaje a Telegram: {e}")

def login_con_robot():
    print("Iniciando Selenium para obtener token...")
    options = Options()
    
    # Descomenta la siguiente línea SOLO si lo vas a correr en tu compu y necesitas Brave
    # options.binary_location = r"COLOCA LA RUTA DE TU NAVEGADOR AQUI"
    
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    try:
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 30)
        
        driver.get("https://eminus.uv.mx/eminus4/login")
        
        wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='text']"))).send_keys(USERNAME)
        driver.find_element(By.XPATH, "//input[@type='password']").send_keys(PASSWORD)
        
        try: driver.find_element(By.XPATH, "//button[@type='submit']").click()
        except: driver.find_element(By.XPATH, "//input[@type='submit']").click()
        
        wait.until(lambda d: "login" not in d.current_url)
        print("Login exitoso, extrayendo token...")
        
        import time
        time.sleep(4)
        
        token = driver.execute_script("return localStorage.getItem('accessToken');")
        if not token: token = driver.execute_script("return localStorage.getItem('token');")
        if not token: token = driver.execute_script("return sessionStorage.getItem('token');")
        
        driver.quit()
        return token
    except Exception as e:
        print(f"Error en Selenium: {e}")
        if 'driver' in locals(): driver.quit()
        return None

def ejecutar_sincronizacion():
    token = ""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f: token = f.read().strip()
    
    if not token:
        token = login_con_robot()
        if token:
            with open(SESSION_FILE, "w") as f: f.write(token)

    if not token:
        print("No se pudo obtener el token. Abortando.")
        return

    headers = {"Authorization": f"Bearer {token}"}
    todas = []
    errores = 0
    
    print("Consultando API de Eminus...")
    for id_curso, nombre in MATERIAS.items():
        try:
            res = requests.get(f"{URL_BASE_API}{id_curso}", headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json().get("contenido", [])
                if data:
                    for t in data:
                        t["materia_nombre"] = nombre
                        todas.append(t)
            elif res.status_code == 401: errores += 1
        except: pass

    if errores > 0 and not todas:
        print("Token expirado o inválido. Intentando renovar...")
        if os.path.exists(SESSION_FILE): os.remove(SESSION_FILE)
        token = login_con_robot()
        if token:
            with open(SESSION_FILE, "w") as f: f.write(token)
            return ejecutar_sincronizacion()
        return

    procesar_y_notificar(todas)

def procesar_y_notificar(tareas):
    hoy = datetime.now().date()
    pendientes = []
    
    for t in tareas:
        estado = t.get("estadoEntrega")
        if estado is None or estado == 0:
            fecha_str = t["fechaTermino"].split("T")[0]
            fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            if fecha_obj >= hoy:
                pendientes.append((t, fecha_obj))
    
    pendientes.sort(key=lambda x: x[1])

    if not pendientes:
        print("Sin tareas pendientes. No se envía mensaje.")
        return

    mensaje = "📚 *Resumen de Tareas Eminus*\n\n"
    
    for t, fecha in pendientes:
        if fecha == hoy:
            icono = "‼️"
            fecha_txt = "HOY"
        else:
            icono = "⏰"
            fecha_txt = f"{fecha.day}/{fecha.month}"
            
        mensaje += f"{icono} *{t['materia_nombre']}*\n"
        mensaje += f"   _{t['titulo']}_\n"
        mensaje += f"   Límite: {fecha_txt}\n\n"
        
    enviar_telegram(mensaje)

if __name__ == "__main__":
    print(f"--- Iniciando revisión {datetime.now()} ---")
    ejecutar_sincronizacion()