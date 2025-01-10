from typing import Iterable

from disnake import Message



def has_any(content: str, words: Iterable) -> bool:
    return any(word in content for word in words)



async def bot_validate(content: str, m: Message):
    if content.startswith("hodný bot") or "good bot" in content:
        await m.add_reaction("🙂")
    if content.startswith("zlý bot") or has_any(content, ["bad bot", "naser si bote", "si naser bote"]):
        await m.add_reaction("😢")
