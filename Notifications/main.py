import pika, sys, os
import time, flask_mail, mailtrap
from dotenv import load_dotenv

load_dotenv()

mail_config = {
    "MAIL_SERVER": os.getenv("SMTP_HOST"),
    "MAIL_PORT": os.getenv("SMTP_PORT"),
    "MAIL_USERNAME": os.getenv("SMTP_USERNAME"),
    "MAIL_PASSWORD": os.getenv("SMTP_PASSWORD"),
    "MAIL_SENDER": "jacopo@mailtrap.com"
}

def send(destinatario, messaggio):
    mail = flask_mail.Mail(mailtrap, mail_config)
    msg = flask_mail.Message(
        messaggio,
        sender=mail_config["MAIL_SENDER"],
        recipients=[destinatario]
    )
    msg.body = "Email inviata con successo!"
    mail.send(msg)

def main():

    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()

    channel.queue_declare(queue='hello')

    def callback(ch, method, properties, body):
        with open('notifications.txt', 'a') as f:
            f.write(f'{body}\n')
        mail = flask_mail.Mail(mailtrap, mail_config)

    channel.basic_consume(queue='hello',
                        auto_ack=True,
                        on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)