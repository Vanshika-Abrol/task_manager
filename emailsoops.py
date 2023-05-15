import requests

def send_mail(email,subject,message):
    url = 'https://api.sendinblue.com/v3/smtp/email'
    headers = {
        'Content-Type': 'application/json',
        'api-key': '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'
    }
    data = {
        'sender': {'name': 'Vanshika', 'email': 'vanshikaabrol123@gmail.com'},
        'to': [{'email': email}],
        'subject': subject,
        'htmlContent': '<p>Hello World!</p>'
    }
    requests.post(url, headers=headers, json=data)