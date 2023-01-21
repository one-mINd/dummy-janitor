import asyncio
from telethon.sync import TelegramClient, events

from conf import *
from matchers_driver import MatchersDriver


class DeletionLogic:
  def __init__(self, db: MatchersDriver):
    self.db = db
    self.last_event = ''
    self.last_rule = ''

  async def _delete_event(self, client: TelegramClient, event: events.NewMessage):
    await asyncio.sleep(RETENTION_PERIOD)
    await client.delete_messages(entity=event.message.chat_id, message_ids=event.message)

  async def _delete_answer(self, client: TelegramClient, event: events.NewMessage):
    current_nick = await event.get_sender()
    current_nick = "@"+current_nick.username
    last_rule_nick = self.last_rule.split(" ")[1]

    if current_nick == last_rule_nick:
      await self._delete_event(client, self.last_event)
      await self._delete_event(client, event)
      self.last_event = ''
      self.last_rule = ''
      return True
    
    return False

  async def _delete_squash(self, client: TelegramClient, event: events.NewMessage):
    if event.message.sticker is not None:
      matcher = await self.db.get_matcher_row(matcher="stickers") 
      if matcher != [] and self.last_event != '' and self.last_event.message.sticker is not None and self.last_rule == "squash":
        if event.message.sticker.id == self.last_event.message.sticker.id:
          await self._delete_event(client, event)
          return True

    elif event.message.message is not None:
      matcher = await self.db.get_matcher_row(matcher=event.message.message) 
      if matcher != [] and self.last_event != '' and self.last_event.message.message is not None and self.last_rule == "squash":
        if event.message.message == self.last_event.message.message:
          await self._delete_event(client, event)
          return True

    return False

  async def _process_rule(self, event: events.NewMessage, rule: str):
    if 'answer' in rule:
      self.last_event = event
      self.last_rule = rule
    
    elif 'squash' in rule:
      self.last_event = event
      self.last_rule = rule
  
  async def _process_match(self, client: TelegramClient, event: events.NewMessage):
    if await self._delete_squash(client, event):
      return None

    else:
      if event.message.sticker is not None:
        matcher = await self.db.get_matcher_row(matcher="stickers") 
      else:
        matcher = await self.db.get_matcher_row(matcher=event.message.message) 

    if "answer" in self.last_rule and await self._delete_answer(client, event):
      return None

    current_nick = await event.get_sender()
    current_nick = "@"+current_nick.username
    all_rule = await self.db.get_all_rules(nick=current_nick)
    if len(all_rule) != 0:
      await self._delete_event(client, event)

    if len(matcher) == 0:
      self.last_event = ''
      self.last_rule = ''
      return None

    rule = matcher[1]
    matcher = matcher[0]

    if rule is not None:
      await self._process_rule(event, rule)

    else:    
      await self._delete_event(client, event)
      self.last_event = ''
      self.last_rule = ''

  async def add_to_queue(self, client: TelegramClient, event: events.NewMessage):
    await self._process_match(client, event)
    await asyncio.sleep(1)
