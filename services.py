import requests
import json
import time

from num2ltr import numberToLetters, _functions
from .sett import *

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
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + whatsapp_token}
        print("se envia ", data)
        response = requests.post(whatsapp_url, headers=headers, data=data)
        
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

def buttonReply_Message(number, options, text, footer, metadata, messageId):
    buttons = []
    for i, option in enumerate(options):
        buttons.append(
            {
                "type": "reply",
                "reply": {
                    "id": metadata + "_btn" + str(i+1),
                    "title": option
                }
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": text,
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "buttons": buttons
                }
            }
        }
    )
    return data

def listReply_Message(number, options, body, footer, sedd,messageId):
    rows = []

    for i, option in enumerate(options):
        rows.append(
            {
                "id": sedd + "_row_" + str(i+1),
                "title": option,
                "description": ""
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "button": "Ver Opciones",
                    "sections": [
                        {
                            "title": "Secciones",
                            "rows": rows
                        }
                    ]
                }
            }
        }
    )
    return data

def document_Message(number, url, caption, filename):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": url,
                "caption": caption,
                "filename": filename
            }
        }
    )
    return data

def sticker_Message(number, sticker_id):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "sticker",
            "sticker": {
                "id": sticker_id
            }
        }
    )
    return data

def get_media_id(media_name , media_type):
    media_id = ""
    if media_type == "sticker":
        media_id = stickers.get(media_name, None)
    #elif media_type == "image":
    #    media_id = images.get(media_name, None)
    #elif media_type == "video":
    #    media_id = videos.get(media_name, None)
    #elif media_type == "audio":
    #    media_id = audio.get(media_name, None)
    return media_id

def replyReaction_Message(number, messageId, emoji):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "reaction",
            "reaction": {
                "message_id": messageId,
                "emoji": emoji
            }
        }
    )
    return data

def replyText_Message(number, messageId, text):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "context": { "message_id": messageId },
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

def warning_message(number, warning, tryAgain):
    list = []

    list.append(text_Message(number, warning))
    list.append(text_Message(number, tryAgain))

    return list

def administrar_chatbot(text, number, messageId, messageType):
    # Flow variables
    list = []
    content = text['content'].lower() # Mesage from user
    meta = "" # Store metadata coming from interactive messages
    markRead = markRead_Message(messageId)
    list.append(markRead)
    time.sleep(2)

    # Validations
    isInteractive = messageType == 'interactive'
    isnumeric = str.isnumeric(content)
    invalidsize = isnumeric and len(content) > 15
    isdecimal = isnumeric and str.__contains__(content, '.')

    print("user says: ", content)

    if isInteractive:
        meta = text['metadata'].split("_")[0]

    if content == "hola":
        msg = text_Message(number, "¡Hola! 👋 Bienvenido a Num2Letra. ¿Qué números quieres convertir hoy?")
        list.append(msg)

    # Parse to upper case
    elif "si" in content and isInteractive:
        numToLetters = numberToLetters(meta)
        msg = text_Message(number, numToLetters.upper())
        list.append(msg)
    
    # Capitalize number
    elif "no" in content and isInteractive:
        numToLetters = numberToLetters(meta)
        msg = text_Message(number, numToLetters.capitalize())
        list.append(msg)
        
    elif invalidsize:
        result = warning_message(number, "Ups! 🫣 Solo puedo procesar números hasta de 15 cifras", "Escribe otro número 😅")
        list.extend(result)

    elif isdecimal:
        result = warning_message(number, "Aún no puedo procesar números con punto decimal o con potencias", "Escribe otro número 😅")
        list.extend(result)

    elif isnumeric:
        options = ["Si", "No"]
        msg = "¿Te gustaría la respuesta en mayusculas?"
        footer = "Tu número es: " + _functions._joinByGroups(content)
        buttonReplyData = buttonReply_Message(number, options, msg, footer, content, messageId)
        list.append(buttonReplyData)

    else:
        result = warning_message(number, "Lo siento, no entendí lo que dijiste", "Escribe otro número 😅")
        list.extend(result)
        
    for item in list:
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
        

