import os
import requests
import subprocess
import lzma
import zipfile
import shutil
from colorama import init, Fore, Style
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

# Inicializar colorama (es necesario hacerlo antes de usar los estilos)
init()

# Definir algunos estilos de color
color_exitoso = Fore.GREEN
color_texto = Fore.BLUE
color_error = Fore.RED
color_titulo = Fore.YELLOW
color_subtitulo = Fore.CYAN
color_reset = Style.RESET_ALL

def buscar_adb():
    # Ruta relativa a la carpeta "bin" dentro de la carpeta donde está el script
    ruta_local_adb = os.path.join(os.path.dirname(__file__), "bin", "adb.exe")
    
    # Verifica si adb.exe está en la carpeta local 'bin'
    if os.path.exists(ruta_local_adb):
        return ruta_local_adb
    
    # Si no se encuentra, devuelve un mensaje de error
    return None

# Ejecutar búsqueda de adb al inicio del script
ruta_adb = buscar_adb()

#if ruta_adb:
    #print(f"ADB encontrado en: {ruta_adb}")
#else:
   # print("Error: No se encontró adb.exe en la carpeta 'bin'.")
#print(ruta_adb)

#######################################################################################################################
def configurar_dispositivo_android():
    print(f"{color_subtitulo} \n  Android Device Settings: {color_reset}")
    print(f"{color_texto} \n  A. Insert Burp Suite certificate. {color_reset}")
    print(f"{color_texto}  B. Insert frida server and client. {color_reset}")

    opcion = input(f"{color_titulo}\n  Select an option (A/B): {color_reset}").upper()

    if opcion == "A":
        ip_burp = input(f"{color_texto}\n  Enter the Burp Suite IP address: {color_reset}")
        puerto_burp = input(f"{color_texto}  Enter Burp Suite port: {color_reset}")
        insertar_certificado_burp(ip_burp, puerto_burp)  # Pasar ip_burp y puerto_burp como argumentos
    elif opcion == "B":
        insertar_frida_server_client()
    else:
        print("  Invalid option. Please select 'A' or 'B'.")
###------------------------------------------------------------------------------------------
def insertar_certificado_burp(ip_burp, puerto_burp):
    color_exitoso = "\033[1;32m"
    color_reset = "\033[0;0m"
    # print(f"Insertando certificado de Burp Suite para IP: {ip_burp}, Puerto: {puerto_burp}")

    # Construir la URL para descargar el certificado desde Burp Suite
    url_certificado = f"http://{ip_burp}:{puerto_burp}/cert"

    # Descargar el certificado desde la URL
    try:
        response = requests.get(url_certificado)
        if response.status_code == 200:
            # Guardar el certificado descargado en la carpeta C:\Windows\Temp
            certificado_path = os.path.join("C:\\Windows\\Temp", "cacert.der")
            with open(certificado_path, "wb") as f:
                f.write(response.content)
            print(f"{color_exitoso}\n  [+]    Burp Suite certificate downloaded successfully. {color_reset}")
            
            # Guardar el certificado PEM en un archivo
            certificado_pem_path = os.path.join("C:\\Windows\\Temp", "cacert.pem")
            with open(certificado_pem_path, "wb") as f_pem:
                with open(certificado_path, "rb") as f_der:
                    f_pem.write(f_der.read())
            print(f"{color_exitoso}\n  [+]    Certificate converted to PEM successfully. {color_reset}")
            
            # Renombrar el archivo PEM a "9a5ba575.0"
            nuevo_nombre = os.path.join("C:\\Windows\\Temp", "9a5ba575.0")
            os.rename(certificado_pem_path, nuevo_nombre)
            #print(f"{color_exitoso}\n[+]   Certificado PEM renombrado a: {nuevo_nombre} {color_reset}")

            # Ejecutar adb push con la ruta completa al archivo renombrado
            if ruta_adb:
                comando_adb_push = f'"{ruta_adb}" push "{nuevo_nombre}" /sdcard/'
                try:
                    resultado_push = subprocess.run(comando_adb_push, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    print(f"{color_exitoso}\n  [+]    PEM certificate sent to /sdcard/ successfully using ADB. {color_reset}")

                    # Ejecutar adb remount para volver a montar el sistema de archivos en modo escritura
                    comando_adb_remount = f'"{ruta_adb}" remount'
                    try:
                        resultado_remount = subprocess.run(comando_adb_remount, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        print(f"{color_exitoso}\n  [+]    File system remounted successfully using ADB. {color_reset}")

                        # Ejecutar adb shell mv para mover el archivo a /system/etc/security/cacerts/
                        comando_adb_mv = f'"{ruta_adb}" shell mv /sdcard/9a5ba575.0 /system/etc/security/cacerts/'
                        try:
                            resultado_mv = subprocess.run(comando_adb_mv, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            print(f"{color_exitoso}\n  [+]    File moved to /system/etc/security/cacerts/ successfully using ADB. {color_reset}")

                            # Ejecutar adb shell chmod para cambiar permisos
                            comando_adb_chmod = f'"{ruta_adb}" shell chmod 644 /system/etc/security/cacerts/9a5ba575.0'
                            try:
                                resultado_chmod = subprocess.run(comando_adb_chmod, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                print(f"{color_exitoso}\n  [+]    File permissions changed correctly using ADB. {color_reset}")

                                # Ejecutar adb reboot para reiniciar el dispositivo
                                comando_adb_reboot = f'"{ruta_adb}" reboot'
                                try:
                                    resultado_reboot = subprocess.run(comando_adb_reboot, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                    print(f"{color_exitoso}\n  [+]    The device will reboot. {color_reset}")
                                except subprocess.CalledProcessError as e:
                                    print(f"  [X]    Error when running adb reboot: {e.stderr.decode()}")

                                # Eliminar los archivos temporales
                                try:
                                    os.remove(certificado_path)
                                    os.remove(nuevo_nombre)
                                    print(f"{color_exitoso}\n  [+]    Temporary files deleted successfully. {color_reset}")
                                except OSError as e:
                                    print(f"  [X]    Error deleting temporary files: {e.strerror}")

                            except subprocess.CalledProcessError as e:
                                print(f"  [X]    Error running adb shell chmod: {e.stderr.decode()}")

                        except subprocess.CalledProcessError as e:
                            print(f"  [X]    Error running adb shell mv: {e.stderr.decode()}")

                    except subprocess.CalledProcessError as e:
                        print(f"  [X]    Error running adb remount: {e.stderr.decode()}")

                except subprocess.CalledProcessError as e:
                    print(f"  [X]    Error when running adb push: {e.stderr.decode()}")
            else:
                print("  [X]    adb.exe was not found on the system. Make sure you have ADB installed and configured correctly.")
            
            return nuevo_nombre  # Devolver la ruta del certificado PEM renombrado
        else:
            print(f"  [X] The certificate could not be downloaded. Application Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"  [X] Error downloading certificate: {e}")
    
    return None  # Devolver None si ocurrió un error durante la descarga

# Ejecutar búsqueda de adb al inicio del script
ruta_adb = buscar_adb()

###--------------------------------------------------------------------------------------
def insertar_frida_server_client():
    color_exitoso = "\033[1;32m"
    color_reset = "\033[0;0m"
    
    # URLs para descargar frida-server según la arquitectura
    urls_frida_server = {
        "arm64": "https://github.com/frida/frida/releases/download/16.3.3/frida-server-16.3.3-android-arm64.xz",
        "armeabi-v7a": "https://github.com/frida/frida/releases/download/16.3.3/frida-server-16.3.3-android-arm.xz",
        "x86_64": "https://github.com/frida/frida/releases/download/16.3.3/frida-server-16.3.3-android-x86_64.xz"
    }
    
    if ruta_adb:
        # Ejecutar adb shell getprop ro.product.cpu.abi para obtener la arquitectura del dispositivo
        comando_adb_getprop = f'"{ruta_adb}" shell getprop ro.product.cpu.abi'
        try:
            resultado_getprop = subprocess.run(comando_adb_getprop, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            arquitectura = resultado_getprop.stdout.decode().strip()
            print(f"{color_exitoso}\n  [+]    Device architecture detected: {arquitectura} {color_reset}")

            # Determinar la URL del frida-server según la arquitectura detectada
            url_frida_server = None
            if arquitectura.startswith("arm64"):
                url_frida_server = urls_frida_server["arm64"]
            elif arquitectura.startswith("armeabi-v7a"):
                url_frida_server = urls_frida_server["armeabi-v7a"]
            elif arquitectura.startswith("x86_64"):
                url_frida_server = urls_frida_server["x86_64"]
            else:
                print(f"  [X]    Architecture not supported or recognized: {arquitectura}")

            if url_frida_server:
                # Descargar frida-server según la arquitectura
                try:
                    response = requests.get(url_frida_server)
                    if response.status_code == 200:
                        frida_server_xz_path = os.path.join("C:\\Windows\\Temp", "frida-server.xz")
                        with open(frida_server_xz_path, "wb") as f:
                            f.write(response.content)
                        print(f"{color_exitoso}\n  [+]    frida-server version 16.3.3, successfully downloaded for {arquitectura}. {color_reset}")
                        
                        # Descomprimir frida-server.xz
                        frida_server_path = os.path.join("C:\\Windows\\Temp", "frida-server")
                        with lzma.open(frida_server_xz_path) as f_xz:
                            with open(frida_server_path, "wb") as f_out:
                                shutil.copyfileobj(f_xz, f_out)
                        print(f"{color_exitoso}\n  [+]    frida-server unzipped correctly. {color_reset}")
                        
                        # Enviar frida-server al dispositivo Android
                        comando_adb_push = f'"{ruta_adb}" push {frida_server_path} /data/local/tmp'
                        try:
                            resultado_push = subprocess.run(comando_adb_push, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            print(f"{color_exitoso}\n  [+]    frida-server transferred to device at /data/local/tmp. {color_reset}")
                            
                            # Dar permisos al archivo frida-server en el dispositivo
                            comando_adb_chmod = f'"{ruta_adb}" shell chmod 777 /data/local/tmp/frida-server'
                            try:
                                resultado_chmod = subprocess.run(comando_adb_chmod, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                print(f"{color_exitoso}\n  [+]    Permissions successfully granted to the frida-server file on the device. {color_reset}")
                                
                                # Eliminar archivos temporales frida-server.xz y frida-server en Windows
                                try:
                                    os.remove(frida_server_xz_path)
                                    os.remove(frida_server_path)
                                    print(f"{color_exitoso}\n  [+]    Temporary files deleted successfully. {color_reset}")
                                except OSError as e:
                                    print(f"  [X]    Error deleting temporary files: {e}")
                                
                                # INSTALACIÓN DEL CLIENTE DE FRIDA (frida-tools y versión específica)
                                print(f"{color_exitoso}\n  [+]    Installing frida-tools and frida client version 16.3.3... {color_reset}")
                                
                                try:
                                    # Instalar frida-tools
                                    subprocess.run("pip install frida-tools", shell=True, check=True)
                                    print(f"{color_exitoso}\n  [+]    frida-tools installed correctly. {color_reset}")
                                    
                                    # Instalar frida client versión 16.3.3
                                    subprocess.run("pip install frida==16.3.3", shell=True, check=True)
                                    print(f"{color_exitoso}\n  [+]    frida client version 16.3.3 installed correctly. {color_reset}")
                                
                                except subprocess.CalledProcessError as e:
                                    print(f"  [X]    Error during installation of frida-tools or frida client: {e.stderr.decode()}")

                            except subprocess.CalledProcessError as e:
                                print(f"  [X]    Error running adb shell chmod: {e.stderr.decode()}")
                        
                        except subprocess.CalledProcessError as e:
                            print(f"  [X]    Error when running adb push: {e.stderr.decode()}")
                        
                    else:
                        print(f"  [X]    Could not download frida-server. Application Status: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f"  [X]    Error downloading frida-server: {e}")

        except subprocess.CalledProcessError as e:
            print(f"  [X]    Error running adb shell getprop ro.product.cpu.abi: {e.stderr.decode()}")
    else:
        print("  [X]    adb.exe was not found on the system. Make sure you have ADB installed and configured correctly.")

# Ejecutar búsqueda de adb al inicio del script
ruta_adb = buscar_adb()

###########################################################################################################################################################

def analizar_estatico_apk(ruta_apk):
    try:
        print(f"{Fore.BLUE}\n  Starting static analysis with apkleaks...{Fore.RESET}")
        resultado = subprocess.run(['apkleaks', '-f', ruta_apk], capture_output=True, text=True)
        if resultado.returncode == 0:
            # Filtrar las líneas que contienen "ERROR"
            output_lines = resultado.stdout.splitlines()
            filtered_output = "\n".join(line for line in output_lines if "ERROR" not in line)
            print(f"{Fore.GREEN}\n  Analysis completed successfully. Results:\n{Fore.RESET}")
            print(filtered_output)
        else:
            print(f"{Fore.RED}\n  Error during analysis: {resultado.stderr}{Fore.RESET}")
    except Exception as e:
        print(f"{Fore.RED}\n  An error occurred while running static analysis: {e}{Fore.RESET}")

##########################################################################################################################################################
def detectar_tecnologia_aplicacion(ruta_archivo):
    tecnologias = {
        'Flutter': ['assets/flutter_assets/', 'lib/arm64-v8a/libflutter.so', 'App.framework', 'flutter_assets'],
        'Cordova': ['assets/www/', 'cordova.js', 'config.xml', 'www/index.html'],
        'PhoneGap': ['assets/www/', 'phonegap.js', 'www/index.html'],
        'Ionic': ['assets/www/', 'ionic.js', 'ionic.config.json', 'www/index.html'],
        'Capacitor': ['capacitor.config.json', 'assets/capacitor.config.json', 'www/index.html'],
        'React Native': ['assets/index.android.bundle', 'lib/arm64-v8a/libreactnativejni.so', 'main.jsbundle'],
        'Xamarin': ['lib/arm64-v8a/libxamarin.so', 'assemblies/', 'xamarin.forms', 'mscorlib.dll'],
        'Native': []  # Las aplicaciones nativas no tendrán estos indicadores
    }
    
    try:
        with zipfile.ZipFile(ruta_archivo, 'r') as archivo_zip:
            file_list = archivo_zip.namelist()
            
            detected_technologies = []
            
            for tech, indicators in tecnologias.items():
                for indicator in indicators:
                    if any(indicator in file for file in file_list):
                        detected_technologies.append(tech)
                        break
            
            # Determinar si es híbrida o nativa
            tipo_app = 'Híbrida' if any(tech in detected_technologies for tech in tecnologias if tech != 'Native') else 'Nativa'
            print(f"{color_texto}\n [+]Application : {color_exitoso}{tipo_app}{color_reset}")
            print(f"{color_texto}\n [+] Technologies detected: {color_exitoso}{', '.join(detected_technologies)}{color_reset}")
            
            # Si se detecta que la app está hecha en Flutter, preguntar si se desea parchar
            if 'Flutter' in detected_technologies:
                respuesta = input(f"\n  It has been detected that the application is made in Flutter. Do you want to patch the app to intercept? (S/N): ")
                if respuesta.lower() == 's':
                    opcion = "1"  # Selección automática de la opción 1
                    ip_proxy = input(f"\n  Please enter the IP address of the proxy (ex. 192.168.1.154): ")

                    # Comando para parchar la app usando ReFlutter
                    comando_parcheo = ['reflutter', ruta_archivo]
                    try:
                        proceso = subprocess.Popen(
                            comando_parcheo, 
                            stdin=subprocess.PIPE, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE, 
                            text=True
                        )
                        
                        # Automáticamente enviar la opción y la IP del proxy a ReFlutter
                        proceso.stdin.write(f"{opcion}\n")
                        proceso.stdin.write(f"{ip_proxy}\n")
                        proceso.stdin.flush()

                        # Procesar la salida de ReFlutter y capturar solo la ruta final
                        ruta_parcheada = None
                        for linea in proceso.stdout:
                            if 'The resulting apk file:' in linea:
                                ruta_parcheada = linea.split(': ')[1].strip()
                        
                        proceso.wait()
                        if proceso.returncode == 0 and ruta_parcheada:
                            print(f"{color_exitoso}\n  The app has been successfully patched.{color_reset}")
                            print(f"{color_exitoso}\n  The patched application is located at: {ruta_parcheada}{color_reset}")
                        else:
                            print(f"{color_error}\n  Error patching the app: {proceso.stderr.read()}{color_reset}")
                    except Exception as e:
                        print(f"{color_error}\n  Error running ReFlutter command: {str(e)}{color_reset}")
            
            # No retornar valores para evitar que se muestre la información nuevamente
            return None, None
            
    except Exception as e:
        print(f"{color_error}  Error parsing file: {e}{color_reset}")
        return None, None

banner = f"""
{Fore.RED}
     __  __       _       _     _____ 
    |  \/  | ___ | |__ (_) | __|_   _|
    | |\/| |/ _ \| '_ \| | |/ _ \| |  
    | |  | | (_) | |_) | | |  __/| |  
    |_|  |_|\___/|_.__/|_|_|\___||_|  
{Style.RESET_ALL}
                By: T1N0
"""

def mostrar_menu():

    print(banner)
    while True:
        print(f"{Fore.CYAN}\n    MENU: {Fore.RESET}")
        print(f"{Fore.BLUE}\n  1. Android Device Configuration. {Fore.RESET}")
        print(f"{Fore.BLUE}  2. Static Analysis of APK. {Fore.RESET}")
        print(f"{Fore.BLUE}  3. Detect Application Technology. {Fore.RESET}")
        print(f"{Fore.BLUE}  4. Exit. {Fore.RESET}")

        opcion = input(f"{Fore.YELLOW}\n  Select an option (1-4): {Fore.RESET}")

        if opcion == "1":
            configurar_dispositivo_android()
        elif opcion == "2":
            ruta_archivo = input("\n  Enter the path of the APK file for static analysis: ").strip()
            analizar_estatico_apk(ruta_archivo)
        elif opcion == "3":
            apk_path = input(f"{Fore.BLUE}\n  Enter the path to the APK or IPA file: {Fore.RESET}").strip()
            tipo_aplicacion, tecnologias_detectadas = detectar_tecnologia_aplicacion(apk_path)
            if tipo_aplicacion:
                print(f"{Fore.BLUE}\n  The application is: {Fore.RESET}{tipo_aplicacion}.{Fore.RESET}")
                if tecnologias_detectadas:
                    print(f"{Fore.BLUE}\n  Technologies detected:{Fore.RESET}", ', '.join(tecnologias_detectadas))
                else:
                    print("  No specific technologies detected.")
        elif opcion == "4":
            print(f"{Fore.GREEN} \n  Going out... \n{Fore.RESET}")
            break
        else:
            print(f"{Fore.WHITE} \nInvalid option. Please select a valid option (1-4). {Fore.RESET}")

# Ejecutar el menú
mostrar_menu()