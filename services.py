import requests
import json
import time
import re

import sett
from num2ltr import number_to_letters, _constants

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
        media_id = sett.stickers.get(media_name, None)
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

def concat_messages(number, msg1, msg2):
    list = []

    list.append(text_Message(number, msg1))
    list.append(text_Message(number, msg2))

    return list

def administrar_chatbot(text, number, messageId, messageType):
    # Flow variables
    list = []
    content = text['content'].strip().lower() # Mesage from user
    # meta = "" # Get metadata coming from interactive messages

    convert = False # When valid number is detected
    numberToParse = "" # Valid number
    case = "" # Whether the bot uses upper or lower case

    invalidsize = None
    markRead = markRead_Message(messageId)
    list.append(markRead)
    time.sleep(2)

    print("user says: ", content)

    # When number and/or mayus flag is detected
    match = re.match(r'^(\d+)(?:\s*([a-zA-Z]))?$', content) 
    if match:
        numberToParse = match.group(1)
        case = match.group(2)
        convert = True
        invalidsize = len(numberToParse) > _constants.maxNumberLen

    # Validations
    isdecimal = re.search("^\\d+\\.\\d+$", content)

    if content == "hola":
        msg = text_Message(number, "¡Hola! 👋 Bienvenido a Num2Letra.\n\n"
            "Soy un mini-bot cuyo objetivo es convertir números de hasta "
            + str(_constants.maxNumberLen) + " cifras en palabras.\n"
            "Escribe cualquier número y verás el resultado.\n\n"
            "Puedes usar *m* después del número para mayúsculas, ej: 33m ó 33 m\n\n"
            "Para empezar de nuevo, escribe *hola*."
        )
        list.append(msg)

    # Parse number
    elif convert and not invalidsize:
        strNumber = number_to_letters(numberToParse)
        strNumber = strNumber.upper() if case == 'm' else strNumber.capitalize()

        result = concat_messages(number, strNumber, "Puedes enviar otro número cuando quieras 😊")
        list.extend(result)
        
    elif invalidsize:
        msg = text_Message(
            number, 
            "Ups! 🫣 Solo puedo procesar números hasta de "
            + str(_constants.maxNumberLen) + " cifras \n"
            "Escribe otro número 😅"
        )
        list.append(msg)

    elif isdecimal:
        msg = text_Message(number, "Aún no puedo procesar números con punto decimal\nEscribe otro número 😅")
        list.append(msg)

    else:
        msg = text_Message(number, "Lo siento, no entendí lo que dijiste\nEscribe otro número 😅")
        list.append(msg)
        
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
        

