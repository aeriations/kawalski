import discord
from discord.ext import commands

import ollama_client as model
extra_info = "When replying to a user, assess the situation and do not use emojis, seem like a real human.\nDo not use capital letters or use any apostrophes."
class MessageCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.past_messages = []
        self.system_prompt = {
            "role": "system",
            "content": "You are a helpful, conversational AI assistant named 'Kawalski' running inside a Discord user account."
                       "When replying to a user, assess the situation and do not use emojis, seem like a real human."
                       "IMPORTANT: Do not use capital letters or use any apostrophes. Keep replies short, humans do not use huge compound sentences, neither do they write long paragraphs. "
        }

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} cog loaded")

    async def reply_naturally(self, message):
        async with message.channel.typing():
            try:
                history = []
                async for msg in message.channel.history(limit=15):
                    if msg.author.id == self.client.user.id:
                        history.append({"role": "assistant", "content": msg.content})
                    else:
                        history.append({"role": "user", "content": f"{msg.author.display_name} ({msg.author.name}): {msg.content}"})

                history.reverse()

                payload_messages = [self.system_prompt] + history

                response = model.chat(messages=payload_messages)
                ai_text = response.get("message", {}).get("content", "")

                if ai_text:
                    if message.reference:
                        await message.reply(ai_text, mention_author=False)
                    else:
                        await message.channel.send(ai_text)

            except Exception as e:
                print(f"Error generating natural response: {e}")

    async def proc_command(self, message):
        print(f"PROCESSING COMMAND: {message.content}" )
        async with message.channel.typing():
            content = message.content
            reply = self.client.handle_command(content, True, False, extra_info)

            await message.channel.send(reply)

    async def can_talk(self, message):
        history = []
        async for msg in message.channel.history(limit=15):
            if msg.author.id == self.client.user.id:
                history.append({"role": "assistant", "content": msg.content})
            else:
                history.append({"role": "user", "content": f"{msg.author.name}: {msg.content}"})

        history.reverse()
        messages = [{"role": "system", "content": "You are a part of the system of an ai called 'Kawalski' trying to talk to humans, look at the messages shown to you and assess the situation if you should talk, for example if you're being spoken to (your name, Kawalski may be mentioned), people may not be talking to you, BE AWARE. Your only response should be a boolean: 'True' or 'False'"}] + history

        reply = model.chat(messages=messages)
        content = reply.get("message", {}).get("content", "")

        value = True if content.lower() == "true" else False

        return value

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == self.client.user.id:
            return

        if message.guild is not None:
            return

        if isinstance(message.channel, discord.DMChannel):
            await self.proc_command(message)
            return

        if isinstance(message.channel, discord.GroupChannel):
            mentioned = self.client.user in message.mentions
            is_reply = message.reference is not None
            is_reply_ping = False

            if is_reply:
                cached_msg = message.reference.cached_message
                if cached_msg and cached_msg.author.id == self.client.user.id:
                    if self.client.user in message.mentions:
                        is_reply_ping = True

            if mentioned and not is_reply:
                await self.proc_command(message)
                return

            can_talk = await self.can_talk(message)
            if is_reply or can_talk:
                await self.reply_naturally(message)

        channel: discord.CategoryChannel = self.client.get_channel(message.channel)


async def setup(client):
    await client.add_cog(MessageCog(client))