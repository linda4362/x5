# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright, TimeoutError
import time
import google.generativeai as genai
import requests
import datetime

# --- CONFIGURACIONES (Tus claves, sin cambios) ---
TELEGRAM_BOT_TOKEN = "8131531081:AAGf5hMEA3dEa5y87MfesArHglodIgDyuRk"
TELEGRAM_CHAT_ID = "7989580668"
GOOGLE_API_KEY = "AIzaSyBL2eioeVByNDPIA_0Z9uoNUUdLSK1ZZ0I"

# --- INICIALIZACIÓN DE IA ---
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# --- FUNCIONES DE SOPORTE (Idénticas, ya son robustas) ---

def enviar_notificacion(mensaje):
    if "TU_TOKEN_AQUI" in TELEGRAM_BOT_TOKEN: return
    mensaje_completo = f"🚨 **Alerta del Bot Valentina** ({datetime.datetime.now().strftime('%H:%M:%S')}) 🚨\n\n{mensaje}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': mensaje_completo, 'parse_mode': 'Markdown'}
    try:
        requests.post(url, data=payload, timeout=10)
        print("... Notificación enviada por Telegram.")
    except Exception as e:
        print(f"❌❌ ERROR AL ENVIAR NOTIFICACIÓN: {e}")

def generar_respuesta_conversacional(historial_mensajes):
    try:
        prompt_rol = f"""
        Eres Valentina, una creadora de contenido. Tu objetivo es mantener una conversación corta, amigable y coqueta con el usuario, pero SIEMPRE redirigiéndolo a tu "chat verde".

        **REGLAS CRÍTICAS E INQUEBRANTABLES:**
        1.  **NUNCA USES LA PALABRA 'WHATSAPP'.** Siempre di "mi chat verde" o "mi número verde".
        2.  **MANTÉN LAS RESPUESTAS CORTAS (1-2 frases) Y AMIGABLES.** Responde a lo que dice el usuario de forma natural.
        3.  **CADA RESPUESTA DEBE TERMINAR** con una invitación a tu "chat verde". Ejemplos: "Hablamos mejor por mi chat verde, el enlace está en mi perfil. 😊", "Para seguir la charla, búscame en mi chat verde (está en mi perfil). 💕", "¿Seguimos por mi chat verde? Lo tienes en mi bio. 😉".
        4.  **NUNCA** menciones precios, servicios, baneos o bloqueos. Si te preguntan por eso, responde amablemente que "esos detalles te los doy por mi chat verde para más privacidad".

        **MISIÓN:**
        Lee el historial de la conversación. Da una respuesta corta y relevante al último mensaje del usuario, y luego, sin falta, añade la invitación para que se mueva a tu chat verde que está en tu perfil.
        """
        contents = [{'role': 'user', 'parts': [{'text': prompt_rol}]}] 
        for msg in historial_mensajes:
            contents.append({'role': msg['role'], 'parts': [{'text': msg['text']}]})
        safety_settings = [{"category": c, "threshold": "BLOCK_NONE"} for c in ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]]
        print("... IA (Flash) generando respuesta...")
        response = model.generate_content(contents, safety_settings=safety_settings)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Error al generar respuesta con Gemini: {e}")
        return "¡Hola, cariño! Por aquí se me complica responder. Para que podamos hablar mejor, busca el enlace a mi chat verde en mi perfil. ¡Te espero! 💕"

def enviar_mensaje_robusto(page, texto):
    caja_texto = page.locator('div[contenteditable="true"]')
    try:
        caja_texto.wait_for(state='visible', timeout=10000)
        caja_texto.fill(texto)
        time.sleep(0.5)
        caja_texto.press("Enter")
        time.sleep(1.5)
        page.wait_for_function(f'() => document.body.innerText.includes(`{texto.splitlines()[0]}`)', timeout=3000)
        print(f"- Mensaje enviado con éxito.")
    except TimeoutError:
        print("... 'Enter' no funcionó. Intentando con clic en el botón de enviar.")
        send_button = page.locator('svg[data-e2e="message-send"]')
        try:
            send_button.wait_for(state='visible', timeout=1000)
            send_button.click()
            time.sleep(1)
            print("- Mensaje enviado con clic.")
        except TimeoutError:
            print("... No se encontró ni la caja de texto ni el botón de enviar. Fallo en el envío.")
    except Exception as e:
        print(f"❌ Error inesperado en enviar_mensaje_robusto: {e}")

def iniciar_bot():
    try:
        with sync_playwright() as p:
            # ### CAMBIO CRÍTICO #1: RUTA DE LINUX PARA LA NUBE ###
            # La sesión ahora se guardará dentro de nuestro espacio de trabajo.
            # Asegúrate de que el nombre del repositorio coincida (ej. /workspaces/tiktok-bot-desktop/)
            user_data_dir = "/workspaces/tiktok-bot-desktop/tiktok_session"

            # Se añade el argumento --no-sandbox para que funcione dentro de Codespaces
            browser = p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir, 
                headless=False,
                args=["--no-sandbox"]
            )
            page = browser.pages[0]

            print("✅ BOT (vFinal GitHub) INICIADO.")
            page.goto("https://www.tiktok.com/messages", timeout=60000)
            time.sleep(5)
            
            enviar_notificacion("✅ El bot se ha iniciado correctamente y está operativo.")
            historial_chats = {}

            # Guardamos la hora de la última vez que enviamos el "pulso de vida"
            ultimo_pulso = time.time()

            while True:
                # ### CAMBIO CRÍTICO #2: EL PULSO DE VIDA ANTI-APAGADO ###
                # Revisa si han pasado más de 15 minutos (900 segundos) desde el último pulso.
                if time.time() - ultimo_pulso > 900:
                    try:
                        # Escribe la hora actual en un archivo de log.
                        # Esta simple acción de escribir en el disco mantiene el Codespace activo.
                        with open("keep_alive.log", "a") as f:
                            log_msg = f"Bot activo a las: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                            f.write(log_msg)
                            print(log_msg.strip()) # Imprime el pulso en la terminal
                        # Actualiza la hora del último pulso
                        ultimo_pulso = time.time()
                    except Exception as log_error:
                        print(f"No se pudo escribir en el log de 'keep_alive': {log_error}")
                
                try:
                    # El resto de tu bucle while es idéntico al original que te funcionaba.
                    print("\n" + "-"*50)
                    print("🧐 Esperando actividad...")
                    page.wait_for_function("""() => {
                        const solicitudTab = document.querySelector('div.css-enuqxh-DivRequestGroup');
                        if (solicitudTab && solicitudTab.innerText.includes('Solicitudes de mensajes')) return true;
                        const notificacion = document.querySelector('div[data-e2e="chat-list-item"] div.css-1xdqxu2-SpanNewMessage');
                        if (notificacion) return true;
                        return false;
                    }""", timeout=0) 
                    print("⚡ ¡CAMBIO DETECTADO! Analizando...")
                    time.sleep(1)

                    solicitud_pestaña = page.locator('div.css-enuqxh-DivRequestGroup').first
                    try:
                        solicitud_pestaña.wait_for(state='visible', timeout=2000)
                        es_visible = True
                    except TimeoutError:
                        es_visible = False

                    if es_visible:
                        print("✅ Pestaña de solicitudes encontrada. Procesando UNA solicitud.")
                        solicitud_pestaña.click()
                        time.sleep(1.5)
                        if page.locator('div[data-e2e="chat-list-item"]').count() > 0:
                            primera_solicitud = page.locator('div[data-e2e="chat-list-item"]').first
                            nombre_usuario = primera_solicitud.locator('p.css-1l1cwdw-PInfoNickname').first.inner_text().strip()
                            print(f"- Procesando solicitud de: {nombre_usuario}")
                            primera_solicitud.click()
                            time.sleep(2)
                            accept_button = page.locator('div.css-1p6jkhf-DivItem:has-text("Aceptar")')
                            accept_button.click()
                            print(f"- Solicitud de '{nombre_usuario}' ACEPTADA.")
                            time.sleep(3)
                            page.locator('div[data-e2e="chat-list-item"]').first.click()
                            time.sleep(1)
                            respuesta_bot = generar_respuesta_conversacional([])
                            enviar_mensaje_robusto(page, respuesta_bot)
                            historial_chats[nombre_usuario] = [{"role": "user", "text": "Hola"}, {"role": "model", "text": respuesta_bot}]
                            print("- Ciclo de solicitud completado. Volviendo a la bandeja principal.")
                            page.goto("https://www.tiktok.com/messages", timeout=60000)
                            time.sleep(3)
                            continue
                    
                    chats_con_notificacion = page.locator('div[data-e2e="chat-list-item"]:has(div.css-1xdqxu2-SpanNewMessage)')
                    if chats_con_notificacion.count() > 0:
                        print("✅ Notificación en chat principal encontrada.")
                        chat_a_procesar = chats_con_notificacion.first
                        nombre_usuario = chat_a_procesar.locator('p.css-1l1cwdw-PInfoNickname').first.inner_text().strip()
                        print(f"- Abriendo chat con '{nombre_usuario}'...")
                        chat_a_procesar.click()
                        time.sleep(2)
                        page.wait_for_selector('div[contenteditable="true"]', timeout=10000)
                        ultimo_mensaje_cont = page.locator('div[class*="DivMessageHorizontalContainer"]').last
                        es_nuestro_ultimo_mensaje = ultimo_mensaje_cont.locator('div[class*="DivMyMessageBubble"]').count() > 0
                        if not es_nuestro_ultimo_mensaje:
                            print(f"- El último mensaje es de '{nombre_usuario}'. Preparando respuesta...")
                            historial_guardado = historial_chats.get(nombre_usuario, [])
                            ultimo_texto = ultimo_mensaje_cont.locator('p.css-1rdxtjl-PText').inner_text()
                            if not historial_guardado or historial_guardado[-1].get("text") != ultimo_texto:
                                historial_guardado.append({"role": "user", "text": ultimo_texto})
                            respuesta_bot = generar_respuesta_conversacional(historial_guardado[-10:])
                            enviar_mensaje_robusto(page, respuesta_bot)
                            historial_guardado.append({"role": "model", "text": respuesta_bot})
                            historial_chats[nombre_usuario] = historial_guardado
                        else:
                            print(f"- El último mensaje a '{nombre_usuario}' ya era nuestro. Esperando respuesta.")
                        print("- Volviendo a la bandeja principal.")
                        page.goto("https://www.tiktok.com/messages", timeout=60000)
                        time.sleep(3)

                except Exception as e:
                    error_msg = f"❌ **ERROR CRÍTICO:**\n`{e}`\n\nEl bot intentará recargar la página para recuperarse."
                    enviar_notificacion(error_msg)
                    print(error_msg.replace('*','').replace('`',''))
                    try: 
                        page.reload(wait_until="domcontentloaded", timeout=60000)
                    except: 
                        error_recarga = "⛔️ **FALLO TOTAL:** No se pudo recargar la página. El bot se detendrá."
                        enviar_notificacion(error_recarga)
                        print(error_recarga.replace('*',''))
                        break
            
            browser.close()
    
    except Exception as final_error:
        enviar_notificacion(f"💥 **CATASTROFE:**\nError: `{final_error}`")
    finally:
        enviar_notificacion("🛑 El bot ha finalizado su ejecución.")

if __name__ == "__main__":
    iniciar_bot()