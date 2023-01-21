import os
import aiosqlite


class MatchersDriver:
  def __init__(self, db_pass):
    self.db_pass = db_pass
  
  async def _connect(self):
    if os.path.isfile(self.db_pass):
      db = await aiosqlite.connect(self.db_pass)
    else:
      db = await aiosqlite.connect(self.db_pass)
      await db.execute("CREATE TABLE matchers(matcher, rule)")
      await db.commit()
    return db
  
  async def _disconnect(self, db):
    await db.commit()
    await db.close()

  async def get_all_rules(self, nick: str) -> list:
    db = await self._connect()
    res = await db.execute(f"SELECT rule FROM matchers WHERE rule = 'all {nick}'")
    res = await res.fetchall()
    await self._disconnect(db)

    if len(res) == 0:
      return res
    else:
      return res[0][0]

  async def get_matchers(self) -> list:
    db = await self._connect()
    res = await db.execute("SELECT * FROM matchers")
    res = await res.fetchall()
    res = ["=>".join(m) if None not in m else list(filter(None, m))[0] for m in res]
    await self._disconnect(db)
    return res

  async def get_matcher_row(self, matcher) -> tuple:
    matcher = matcher.lower()
    db = await self._connect()
    res = await db.execute(f"SELECT matcher FROM matchers")
    res = await res.fetchall()

    match = None
    for s in res:
      s = s[0]
      if s is not None and s in matcher:
        match = s
        break
    
    if match is None:
      return []

    res = await db.execute(f"SELECT * FROM matchers WHERE matcher = '{match}'")
    res = await res.fetchall()
    await self._disconnect(db)
    return res[0]

  async def append(self, matcher: str) -> None:
    db = await self._connect()
    if " rule==" in matcher:
      matcher = matcher.split(" rule==")
      rule = "'"+matcher[1]+"'"
      matcher = "'"+matcher[0]+"'"
    else:
      matcher = "'"+matcher+"'"
      rule = 'NULL'

    matcher = matcher.lower()
    rule = rule.lower()
    await db.execute(f"""
        INSERT INTO matchers VALUES
            ({matcher}, {rule})
    """)
    await self._disconnect(db)

  async def append_many(self, matchers: list) -> None:
    for matcher in matchers:
      await self.append(matcher)

  async def delete(self, matcher: str) -> None:
    db = await self._connect()

    if " rule==" in matcher:
      matcher = matcher.split(" rule==")
      rule = matcher[1]
      matcher = matcher[0]
    else:
      matcher = matcher
      rule = 'NULL'

    if matcher != 'NULL':
      matcher = matcher.lower()
      await db.execute(f"""
        DELETE FROM matchers WHERE matcher='{matcher}';
      """)
    elif rule != 'NULL':
      rule = rule.lower()
      await db.execute(f"""
        DELETE FROM matchers WHERE rule='{rule}';
      """)

    await self._disconnect(db)

  async def delete_many(self, matchers: list) -> None:
    for matcher in matchers:
      await self.delete(matcher)
