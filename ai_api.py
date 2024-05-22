import asyncio

from dannie import API_AI
from openai import AsyncOpenAI, DefaultAsyncHttpxClient

# client = openai.OpenAI(api_key=API_AI)

# chat = client.chat.completions.create(messages=[
#         {"role": "user",
#          "content": "Say this is a test",
#          }
#     ], model='gpt-3.5-turbo')
# print(chat)

from openai import AsyncOpenAI

ip = '45.12.30.125'

client = AsyncOpenAI(
    # This is the default and can be omitted
    http_client=DefaultAsyncHttpxClient(
        proxies=f'http://{ip}:8000',
    ),
    api_key=API_AI,
)


async def main() -> None:
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Say this is a test",
            }
        ],
        model="gpt-3.5-turbo",
    )


asyncio.run(main())
