import aiofiles

from conf import *


async def get_matchers() -> list:
  return [line.strip('\n') for line in open(MATCHERS_PATH, 'r').readlines()]


async def append(matcher: str) -> None:
  if matcher != "" and matcher != " ":
    matcher = matcher.lower()
    matchers = await get_matchers()
    matchers = set(matchers)
    matchers.add(matcher)
    matchers = "\n".join(matchers)

    f = await aiofiles.open(MATCHERS_PATH, "w")
    await f.write(matchers)
    await  f.close()


async def append_many(matchers: list) -> None:
  for matcher in matchers:
    await append(matcher)


async def delete(matcher: str) -> None:
  truncated = []
  matcher = matcher.lower()
  for line in await get_matchers():
      if line != matcher:
          truncated.append(f"{line}\n")
  
  f = await aiofiles.open(MATCHERS_PATH, 'w')
  await f.writelines(truncated)


async def delete_many(matchers: list) -> None:
  for matcher in matchers:
    await delete(matcher)


async def is_match(message: str) -> bool:
  message = message.lower()
  matchers = await get_matchers()
  return any(ele in message for ele in matchers)
