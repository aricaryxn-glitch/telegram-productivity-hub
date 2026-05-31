from app.config import get_settings


async def summarize_text(text: str) -> str:
    return await complete("Summarize this document with key points and important facts.", text)


async def generate_quiz(text: str) -> str:
    return await complete("Create 10 exam-style questions and answers from this material.", text)


async def simplify_notes(text: str) -> str:
    return await complete("Explain these notes in simple language with clear headings.", text)


async def generate_flashcards(text: str) -> str:
    return await complete("Create concise flashcards in Q/A format from this material.", text)


async def interview_questions(cv_text: str) -> str:
    return await complete("Generate role-specific interview questions and ideal answer points from this CV.", cv_text)


async def improve_resume(resume_text: str) -> str:
    return await complete("Improve this resume wording for impact, clarity, and ATS friendliness.", resume_text)


async def cover_letter(resume_text: str, job_description: str = "") -> str:
    source = f"Resume:\n{resume_text}\n\nJob description:\n{job_description}"
    return await complete("Write a strong, tailored cover letter from this information.", source)


async def linkedin_profile(resume_text: str) -> str:
    return await complete("Create LinkedIn headline, about section, experience bullets, and skills from this resume.", resume_text)


async def ats_score(resume_text: str, job_description: str = "") -> str:
    source = f"Resume:\n{resume_text}\n\nJob description:\n{job_description}"
    return await complete("Score this resume for ATS fit from 0-100 and list concrete improvements.", source)


async def translate_text(text: str, target_language: str) -> str:
    return await complete(f"Translate this text to {target_language}. Preserve meaning and formatting.", text)


async def complete(instruction: str, text: str) -> str:
    settings = get_settings()
    provider = settings.ai_provider.lower().strip()
    if provider == "auto":
        provider = "groq" if settings.groq_api_key else "openai"
    api_key = settings.groq_api_key if provider == "groq" else settings.openai_api_key
    model = settings.groq_model if provider == "groq" else settings.openai_model
    base_url = settings.groq_base_url if provider == "groq" else None

    if not api_key and provider == "groq" and settings.openai_api_key:
        provider = "openai"
        api_key = settings.openai_api_key
        model = settings.openai_model
        base_url = None
    elif not api_key and provider == "openai" and settings.groq_api_key:
        provider = "groq"
        api_key = settings.groq_api_key
        model = settings.groq_model
        base_url = settings.groq_base_url

    if not api_key:
        return "AI is not configured. Add GROQ_API_KEY or OPENAI_API_KEY to enable this feature."

    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=api_key, base_url=base_url) if base_url else AsyncOpenAI(api_key=api_key)
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": instruction},
            {"role": "user", "content": text[:120000]},
        ],
    )
    return response.choices[0].message.content or ""
