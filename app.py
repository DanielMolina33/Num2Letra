from flask import Flask, request, Response
import sett
from services import *

app = Flask(__name__)

@app.route('/welcome', methods=['GET'])
def welcome():
    return 'Hola, desde Flask'

@app.route('/webhooks', methods=['GET']) # type: ignore
def verify_token():
    try:
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if token == sett.token and challenge != None and mode == 'subscribe':
            print("Route responds: ", str(challenge))
            return Response(str(challenge), mimetype="text/plain")
        else:
            return 'token incorrecto', 403
    except Exception as e:
        return str(e), 403
    
@app.route('/webhooks', methods=['POST'])
def get_mensajes():
    try:
        body = request.get_json()
        entry = body['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        message = value['messages'][0]
        number = message['from']
        messageId = message['id']
        contacts = value['contacts'][0]
        name = contacts['profile']['name']
        messageType = message['type']
        text = obtener_Mensaje_whatsapp(message)

        administrar_chatbot(text, number, messageId, messageType)
        return 'enviado'

    except Exception as e:
        return 'no enviado ' + str(e)

if __name__ == '__main__':
    app.run()
