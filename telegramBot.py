import requests, json, time
from google import genai
from multiprocessing import Process
import os


class bot_google:

    def __init__(self, name: str):
        self.name = name

    def get_response(self, msg):
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

        client = genai.Client(api_key=GEMINI_API_KEY)

        response = client.models.generate_content(
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
            print("Comprobando actualizaciones")
            self.read_updates()
            time.sleep(self.TIME_SLEEP)

    def read_updates(self):
        response_json = requests.get(
            f"{self.url_with_token}/getUpdates?offset={self.offset+1}"
        ).json()

        if response_json["ok"] == True:
            for update in response_json["result"]:

                self.offset = update["update_id"]
                self.msg = update["message"]["text"]
                self.chat_id = update["message"]["chat"]["id"]
                command = self.msg.split()[0]
                self.check_commands(command)

                print(f"{self.offset} - {self.msg}")

    def check_commands(self, command):
        if command == "/resumen":
            edited_msg = (
                f"De todo el texto que viene a continuación, después de doble dos puntos, sólo utiliza la página web que haya para hacer un resumen si la hay y si no hay una web, pídela, pídela diciendo 'Tienes que proporcionar una URL válida', también respeta el idioma de la web:: "
                + self.msg.replace(command, "")
            )
            self.send_message(
                f"Procesando: {self.msg.replace(command, "")}", self.chat_id
            )
            self.p = Process(target=self.question_google_bot(edited_msg, self.chat_id))
            self.p.start()
            # self.send_message(edited_msg, self.chat_id)

        if command == "/help":
            mensaje = """
            Los comandos disponibles son los siguientes:
            /resumen <url> : te hará un resumen de la web que pases.
            """
            self.send_message(mensaje, self.chat_id)

    def send_message(self, msg: str, chat_id: str):
        response_msg = requests.get(
            f"{self.url_with_token}/sendMessage?chat_id={chat_id}&text={msg}"
        )

    def question_google_bot(self, msg: str, chat_id: str):
        print(msg)
        try:
            answer = self.bot_de_google.get_response(msg)
            self.send_message(answer, self.chat_id)
        except genai.errors.ServerError as e:
            self.send_message(f"hubo un problema: {e}", self.chat_id)


bot = TelegramBot()

# bot_google = bot_google("Hola")
# bot_google.get_response("hola")
