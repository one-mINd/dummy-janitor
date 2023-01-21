import asyncio
import logging
from telethon.sync import TelegramClient, events

from conf import *
from matchers_driver import MatchersDriver
from deletion_logic import DeletionLogic

logging.basicConfig(
  level=logging.INFO 
)

client = TelegramClient(CLIENT_NAME, api_id=API_ID, api_hash=API_HASH).start()
db = MatchersDriver(db_pass=MATCHERS_PATH)
deletion_logic = DeletionLogic(db=db)


@client.on(events.NewMessage(pattern='ping'))
async def handle_ping(event: events.NewMessage):
  await client.send_message(entity=event.message.chat_id, message="pong", background=True)


@client.on(events.NewMessage(pattern='/janitor_help'))
async def handle_help(event: events.NewMessage):
  if event.chat_id != CHAT_ID: return None
  await client.send_message(entity=event.message.chat_id, message=HELP_MESSAGE, background=True)
    

@client.on(events.NewMessage(pattern='/add_matchers'))
async def handle_add_matcher(event: events.NewMessage):
  if event.chat_id != CHAT_ID: return None
  await db.append_many(event.message.message.split("\n")[1:])


@client.on(events.NewMessage(pattern='/delete_matchers'))
async def handle_delete_matchers(event: events.NewMessage):
  if event.chat_id != CHAT_ID: return None
  await db.delete_many(event.message.message.split("\n")[1:])
    

@client.on(events.NewMessage(pattern='/list_matchers'))
async def handle_delete_matchers(event: events.NewMessage):
  if event.chat_id != CHAT_ID: return None
  matchers = await db.get_matchers()
  matchers = "\n".join(matchers)
  splited_matchers = [matchers[i:i+1024] for i in range(0, len(matchers), 1024)]
  for matcher in splited_matchers:
    await client.send_message(entity=event.message.chat_id, message=matcher, background=True)


@client.on(events.NewMessage(pattern='/set_retention_period'))
async def handle_set_retenction_period(event: events.NewMessage):
  if event.chat_id != CHAT_ID: return None
  global RETENTION_PERIOD
  RETENTION_PERIOD = int(event.message.message.split(" ")[1])


async def deletion_queue(event):
  await asyncio.sleep(RETENTION_PERIOD)
  await client.delete_messages(entity=event.message.chat_id, message_ids=event.message)


@client.on(events.NewMessage())
async def filter(event):
  if event.chat_id != CHAT_ID: return None
  await deletion_logic.add_to_queue(client=client, event=event) 

client.run_until_disconnected()
