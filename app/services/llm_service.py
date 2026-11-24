
import json
import time
import urllib.request


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma2:2b"


class LLMService:
    def __init__(self):
        self.model_name = MODEL_NAME

    def build_prompt(self, query, documents):
        contexts = []

        for index, doc in enumerate(documents, start=1):
            title = doc.get("title", "Unknown")
            uri = doc.get("uri", "")
            text = doc.get("text", "")

            # Limiter la taille du contexte pour Gemma 2B
            context = text[:1200]

            contexts.append(
                f"[SOURCE {index}]\n"
                f"Occupation: {title}\n"
                f"ESCO URI: {uri}\n"
                f"Content: {context}"
            )

        context_block = "\n\n".join(contexts)

        
        prompt = f"""
You are PathForge AI, a career guidance assistant.

Your task is to recommend suitable occupations using
the student's profile and the retrieved ESCO documents.

IMPORTANT: Treat these as TWO DIFFERENT information sources:

A. STUDENT PROFILE
Contains skills and experiences claimed by the student.
Do not assume the student has skills they did not mention.

B. ESCO DOCUMENTS
Contain occupation descriptions and required skills.
Do not attribute information to ESCO unless it is
explicitly supported by the provided ESCO text.

STRICT RULES:
1. Recommend occupations found in the supplied ESCO documents.
2. Distinguish student skills from occupation requirements.
3. Never claim that ESCO mentions a specific tool
   unless that tool appears explicitly in the ESCO context.
4. Do not invent qualifications, skills or work experience.
5. Explain the match using evidence from both inputs.
6. Cite ESCO occupation facts using [SOURCE 1], [SOURCE 2], etc.
7. Do not cite ESCO for information coming only from the student.
8. If a specific skill or tool is absent from ESCO,
   do not present it as an ESCO requirement.
9. If the evidence is insufficient, acknowledge uncertainty.
10. Answer in English, in no more than 100 words.
11. Mention at most 5 ESCO skills relevant to the profile.
12. Do not reproduce long lists of ESCO skills.
13. Finish with one practical recommendation.

STUDENT PROFILE:
{query}

ESCO DOCUMENTS:
{context_block}

RESPONSE STRUCTURE:
Recommended occupation: [occupation name]
Why it matches: [2 short sentences]
Relevant ESCO skills: [maximum 5 skills]
Recommendation: [1 short sentence]

ANSWER:
"""
        return prompt.strip()


    def generate(self, query, documents):
        if not isinstance(query, str) or not query.strip():
            raise ValueError("The query cannot be empty.")

        if not documents:
            raise ValueError("No ESCO documents were provided.")

        prompt = self.build_prompt(query, documents)

        payload = json.dumps({
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0,
                "num_predict": 180,
                "num_ctx": 4096
            }
        }).encode("utf-8")

        request = urllib.request.Request(
            OLLAMA_URL,
            data=payload,
            headers={
                "Content-Type": "application/json"
            },
            method="POST"
        )

        start = time.perf_counter()

        with urllib.request.urlopen(
            request,
            timeout=240
        ) as response:
            result = json.load(response)

        generation_ms = (
            time.perf_counter() - start
        ) * 1000

        return {
            "model": result.get("model", self.model_name),
            "response": result.get("response", "").strip(),
            "generation_ms": round(generation_ms, 2),
            "prompt_eval_count": result.get("prompt_eval_count"),
            "eval_count": result.get("eval_count"),
            "done_reason": result.get("done_reason"),
            "prompt_eval_count": result.get("prompt_eval_count"),
            "prompt_eval_ms": round(
                result.get("prompt_eval_duration", 0) / 1_000_000, 2
            ),
            "eval_ms": round(
                result.get("eval_duration", 0) / 1_000_000, 2
            )
        }
