import os

CLIENT_NAME = "sessions/"+os.getenv("CLIENT_NAME")

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
CHAT_ID = os.getenv("CHAT_ID")


# MATCHERS_PATH = "/matchers_dir/matchers.db"
MATCHERS_PATH = "matchers.db"

RETENTION_PERIOD = 30

HELP_MESSAGE = """
Это кароч бот, который будет чистить этот чат от жабьего спама
Работает он максимально тупо. У него есть список мэтчеров. Он хендлит вообще все сообщения ебать. И ЕсЛи в этом сообщении есть хоть одно слово из списка, то удаляет его через РЕТЕНШОН_ПЕРИОД секунд.
Команды:
  - /janitor_help - чел...

  - /add_matchers
    matcher_1
    matcher_2
    matcher_3
    - добавляет матчеры в список. Важно писать каждый новый матчер с новой строки. И очень не желательно делать многострочные матчеры. Потому что это невозможно. Сосиска.
      списьок пустой по умолчанию

  - /delete_matchers
    matcher_1
    matcher_2
    matcher_3
    - удаляет матчеры

  - /list_matchers - списьок матчеров

  - /set_retention_period N -  Назначает РЕТЕНШОН_ПЕРИОД. Типа через сколько времени будет удален бот.
"""
