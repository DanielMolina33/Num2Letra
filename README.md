# num2ltr Whatsapp bot

num2ltr Whatsapp bot is a simple automation for converting numbers to words.

It uses num2ltr python package v1.0.

This project is under **testing**, so you may experience inconsistencies.

This is a personal project intended for financial use.

## Features
- Send text messages
- Send responses using upper or lower case
- Mark messages as "seen"
- Convert numbers to letters up to 15 digits (for now)

## Limitations
- No decimal support yet
- No negative numbers
- No scientific notation

## How to try it?

1. Go to downloaded location

```bash
  cd whatsappbot
```
2. Create a virtual environment using python 3.10+

```bash
  virtualenv -p 3.10.11 .venv
```
3. Activate the virtual environment

Linux / macOS:
```bash
source .venv/bin/activate
```

Windows:
```cmd
  .venv\Scripts\activate
```
4. Install dependencies

```bash
  pip install -r requirements.txt
```

5. Get your Whatsapp token from Meta. And create your own verification token

Linux / macOS:
```bash
  export VERIFY_TOKEN=your_verify_token_here
  export WPP_TOKEN=your_whatsapp_token_here
```

Windows (CMD):
```cmd
  set VERIFY_TOKEN=your_verify_token_here
  set WPP_TOKEN=your_whatsapp_token_here
```

PowerShell:
```powershell
  $env:VERIFY_TOKEN="your_verify_token_here"
  $env:WPP_TOKEN="your_whatsapp_token_here"
```

6. Run the app

```bash
  py -m app
```

## Simulate user messages using postman

```javascript
URL
http://127.0.0.1:5000/webhooks

select "raw" body and "JSON" type, DO NOT FORGET TO ADD YOUR NUMBER
{
  "object": "whatsapp_business_account",
  "entry": [{
      "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
      "changes": [{
          "value": {
              "messaging_product": "whatsapp",
              "metadata": {
                  "display_phone_number": "PHONE_NUMBER",
                  "phone_number_id": "PHONE_NUMBER_ID"
              },
              "contacts": [{
                  "profile": {
                    "name": "NAME"
                  },
                  "wa_id": "PHONE_NUMBER"
                }],
              "messages": [{
                  "from": "YOUR NUMBER HERE",
                  "id": "wamid.ID",
                  "timestamp": "TIMESTAMP",
                  "text": {
                    "body": "hola"
                  },
                  "type": "text"
                }]
          },
          "field": "messages"
        }]
  }]
}
```

This project is a fork and adaptation from https://github.com/JPierr3/bigdateros-whatsappbot-python

All credits to JPierr3 from bigdateros