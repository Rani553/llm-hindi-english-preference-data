"""Call Gemini or Groq the same way. Keys: GEMINI_API_KEY, GROQ_API_KEY.
ask(prompt, provider="gemini"|"groq", model=None, system=None)"""
import os, time

DEFAULTS = {"gemini": "gemini-2.0-flash", "groq": "llama-3.1-8b-instant"}


def ask(prompt, provider=None, model=None, system=None, retries=3):
    provider = provider or os.environ.get("LLM_PROVIDER", "gemini")
    model = model or DEFAULTS[provider]
    for attempt in range(retries):
        try:
            if provider == "gemini":
                from google import genai
                from google.genai import types
                client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
                cfg = types.GenerateContentConfig(system_instruction=system) if system else None
                return client.models.generate_content(model=model, contents=prompt, config=cfg).text
            from groq import Groq
            client = Groq(api_key=os.environ["GROQ_API_KEY"])
            msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
            return client.chat.completions.create(model=model, messages=msgs).choices[0].message.content
        except Exception as e:
            print(f"  API error ({e}); retrying in {5 * (attempt + 1)}s")
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("API failed after retries")
