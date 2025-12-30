import requests
import json
import time
import re

import sett
from num2ltr import number_to_letters, _functions, _constants

def obtener_Mensaje_whatsapp(message):
    typeMessage = message['type']
    meta = ""

    if 'type' not in message :
        return {
            "content": 'mensaje no reconocido',
            "metadata": meta
        }

    if typeMessage == 'text':
        text = message['text']['body']

    elif typeMessage == 'button':
        text = message['button']['text']

    elif typeMessage == 'interactive' and message['interactive']['type'] == 'list_reply':
        text = message['interactive']['list_reply']['title']

    elif typeMessage == 'interactive' and message['interactive']['type'] == 'button_reply':
        text = message['interactive']['button_reply']['title']
        meta = message['interactive']['button_reply']['id']
        
    else:
        text = 'mensaje no procesado'

    return {
        "content": text,
        "metadata": meta
    }

def enviar_Mensaje_whatsapp(data):
    try:
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + sett.whatsapp_token}
        print("se envia ", data)
        response = requests.post(sett.whatsapp_url, headers=headers, data=data)
        
        if response.status_code == 200:
            return 'mensaje enviado', 200
        else:
            return 'error al enviar mensaje', response.status_code
    except Exception as e:
        return e,403
    
def text_Message(number, text):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",    
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "body": text
            }
        }
    )
    return data

def markRead_Message(messageId):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id":  messageId
        }
    )
    return data

def extract_numeric(input):
    # When number and/or mayus flag is detected
    match = re.fullmatch(r'^(\d+)(?:[.,](\d+))?(?:\s*([a-zA-Z]))?$', input)

    result = {
        "status": "PASSED",
        "original": input,
        "extracted": None,
        "error_msg": None
    }

    if match:
        result["extracted"] = {
            "integer": match.group(1),
            "decimal": match.group(2),
            "case": match.group(3),
        }

        error = validate_numeric(result["extracted"])
        result["status"] = "ERROR" if error else "OK"
        result["error_msg"] = error if error else None

    return result

def build_messages(phone_number, data):
    messages = []
    extracted = data["extracted"]
    original = data["original"]

    if extracted:
        # Process number
        messages = process_number(extracted)

    else:
        if original == "hola":
            msg = ("¡Hola! 👋 Bienvenido a Num2Letra.\n\n"
                "Soy un mini-bot cuyo objetivo es convertir números de hasta *"
                + str(_constants.maxNumberLen) + " cifras* en palabras.\n"
                "Escribe cualquier número y verás el resultado.\n\n"
                "Puedes usar *m* después del número para mayúsculas, ej: 33m ó 33 m\n\n"
                "Para empezar de nuevo, escribe *hola*."
            )

            messages.append(msg)

        else:
            msg = "Lo siento, no entendí lo que escribiste 😅"
            messages.append(msg)

    return [text_Message(phone_number, msg) for msg in messages]

def validate_numeric(extracted):
    msg = None
    integer = extracted["integer"]
    decimal = extracted["decimal"]

    # Validations
    invalidsize = len(integer) > _constants.maxNumberLen

    if invalidsize:
        msg = ("Ups! 🫣 Solo puedo procesar números hasta de "
            + str(_constants.maxNumberLen) + " cifras \n"
            "Escribe otro número 😅"
        )
        
    elif decimal:
        msg = "Aún no puedo procesar números con punto decimal\nEscribe otro número 😅"

    return msg

def process_number(extracted):
    result = []
    integer = extracted["integer"]
    case = extracted["case"]

    str_integer = number_to_letters(integer)
    str_integer = str_integer.upper() if case == 'm' else str_integer.capitalize()
    result.append(str_integer)

    if len(integer) >= 4:
        formatted_input = _functions._joinByGroups(integer)
        result.append("El número es: " + formatted_input)
        
    result.append("Puedes enviar otro número cuando quieras 😊")

    return result

def process_user_input(phone_number, user_input):
    messages = []
    result = extract_numeric(user_input)
    status = result["status"]

    if status == "OK" or status == "PASSED":
        messages.extend(build_messages(phone_number, result))
    elif status == "ERROR":
        error_msg = result["error_msg"]
        messages.append(text_Message(phone_number, error_msg))
            
    return messages

def mark_as_read(messageId):
    markRead = markRead_Message(messageId)
    time.sleep(2)

    return markRead

def administrar_chatbot(text, phone_number, messageId):
    # Flow variables
    messages = []
    user_input = text['content'].strip().lower() # Mesage from user
    print("user says: ", user_input)
    # meta = "" # Get metadata coming from interactive messages

    # Mark message from user as read
    messages.append(
        mark_as_read(messageId)
    )
    
    # Process user_input    
    messages.extend(
        process_user_input(phone_number, user_input)
    )
            
    for item in messages:
        enviar_Mensaje_whatsapp(item)

#al parecer para mexico, whatsapp agrega 521 como prefijo en lugar de 52,
# este codigo soluciona ese inconveniente.
def replace_start(s):
    number = s[3:]
    if s.startswith("521"):
        return "52" + number
    elif s.startswith("549"):
        return "54" + number
    else:
        return s
        

