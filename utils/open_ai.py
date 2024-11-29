import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class OpenAIClient():
    def __init__(self):
        self.client = OpenAI(
            organization=os.getenv('OPEN_AI_ORGANIZATION_ID'),
            project=os.getenv('OPEN_AI_PROJECT_ID'),
            api_key=os.getenv('OPEN_AI_TOKEN')
        )

    def generate_text(self, prompt):
        try:
            response = self.client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": prompt,
                }],
                model="gpt-4o-mini",
            )

            result = response.choices[0].message.content
        except Exception as e:
            print(f"Error: {e}")
            result = None

        return result


# if __name__ == "__main__":
#     client = OpenAIClient()
#     print(client.generate_text("What is 2 + 2?"))
