import requests, json, time
from google import genai
from multiprocessing import Process
import os


class bot_google:

    def __init__(self, name: str):
        self.name = name
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.GEMINI_API_KEY)

    def get_response(self, msg):

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=msg,
        )
        print(response.text)
        return response.text


class TelegramBot:

    def __init__(self):
        self.TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
        self.offset = 0
        self.url_with_token = f"https://api.telegram.org/bot{self.TELEGRAM_TOKEN}"
        self.TIME_SLEEP = 1
        self.bot_de_google = bot_google("google_bot")

        while True:
            self.read_updates()
            time.sleep(self.TIME_SLEEP)

    def read_updates(self):
        response_json = requests.get(
            f"{self.url_with_token}/getUpdates?offset={self.offset+1}"
        ).json()

        if response_json["ok"]:
            for update in response_json["result"]:
                print(update)
                try:
                    self.offset = update["update_id"]

                    if "supergroup" in str(update):
                        print("SUPER GROUP")
                        self.msg = update["message"]["text"]
                        self.tema_id = update["message"]["chat"]["id"]
                        print(self.tema_id)
                        command = self.msg.split()[0]
                        self.check_commands(command, self.tema_id)

                    if "channel" in str(update):
                        self.msg = update["channel_post"]["text"]
                        self.channel_id = update["channel_post"]["chat"]["id"]
                        command = self.msg.split()[0]
                        self.check_commands(command, self.channel_id)

                    if "private" in str(update):
                        self.msg = update["message"]["text"]
                        self.private_chat_id = update["message"]["chat"]["id"]
                        command = self.msg.split()[0]
                        self.check_commands(command, self.private_chat_id)
                except Exception as e:
                    print(f"Alguna excepcion: {e}")

    def check_commands(self, command, id_to_send_msg):
        print(f"{self.offset} -  - {self.msg}")

        if command == "/resumen":
            valida_msg = self.msg.split()
            if len(valida_msg) < 2:
                print("Algo pasa con el comando.")
                self.send_message(
                    "No ha hecho una solicitud correcta, ejemplo -> /resumen <página_web>",
                    self.chat_id,
                )
                return

            edited_msg = (
                f"De todo el texto que viene a continuación, después de doble dos puntos, sólo utiliza la página web que haya para hacer un resumen si la hay y si no hay una web, pídela, pídela diciendo 'Tienes que proporcionar una URL válida'. Se pueden aceptar webs sin http, https, www, intenta filtrar correctamente que es una web:: "
                + self.msg.replace(command, "")
            )

            self.send_message(
                f"Procesando: {self.msg.replace(command, "")}", id_to_send_msg
            )

            self.p = Process(target=self.question_google_bot(edited_msg, id_to_send_msg))
            self.p.start()

        if command == "/help":
            mensaje = """
            Los comandos disponibles son los siguientes:
            /resumen <url> : te hará un resumen de la web que pases.
            """
            self.send_message(mensaje, id_to_send_msg)

    def send_message(self, msg: str, chat_id: str):
        response_msg = requests.get(
            f"{self.url_with_token}/sendMessage?chat_id={chat_id}&text={msg}"
        )

    def question_google_bot(self, msg: str, chat_id: str):
        print(msg)
        try:
            answer = self.bot_de_google.get_response(msg)
            self.send_message(answer, chat_id)
        except genai.errors.ServerError as e:
            self.send_message(f"hubo un problema: {e}", chat_id)


bot = TelegramBot()

# bot_google = bot_google("Hola")
# bot_google.get_response("hola")
