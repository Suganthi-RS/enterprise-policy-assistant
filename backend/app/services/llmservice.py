import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")

client = genai.Client(
    api_key=GEMINI_API_KEY
)

MODEL_NAME = "gemini-3.6-flash"


def generate_policy_answer(
    question: str,
    context: str
) -> str:

    prompt = f"""
You are an Enterprise Policy Assistant.

Answer the user's question using ONLY the policy information
provided in the context below.

Rules:
- Answer using ONLY the provided policy context.

- Do not use outside knowledge.

- Do not invent policy details.

- If the answer cannot be found in the context, say:

  "I could not find this information in the available company policies."

- Keep the answer clear and concise.

- Preserve specific numbers, dates, eligibility rules, and conditions accurately.

- When making a factual statement, cite the relevant source using:

  [Source: document name, Page X]

- If multiple sources support the answer, cite each relevant source.

POLICY CONTEXT:
{context}

USER QUESTION:
{question}
"""

    max_retries = 3

    for attempt in range(max_retries):

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            return response.text

        except errors.ServerError as error:

            if attempt == max_retries - 1:
                raise error

            wait_time = 2 ** attempt

            print(
                f"Gemini temporarily unavailable. "
                f"Retrying in {wait_time} seconds..."
            )

            time.sleep(wait_time)

    raise RuntimeError("Unable to generate answer from Gemini")