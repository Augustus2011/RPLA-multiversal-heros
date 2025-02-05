from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1/", #deepseek-reasoner
  api_key="",
)

completion = client.chat.completions.create(
  model="deepseek/deepseek-r1",
  messages=[
    {
      "role": "user",
      "content": "What is the meaning of life?"
    }
  ]
)
