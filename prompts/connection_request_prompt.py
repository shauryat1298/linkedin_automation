from pathlib import Path
import yaml

BASE_PATH = Path(__file__).parent.parent
resume_txt_path = BASE_PATH / "artifacts" / "shaurya_resume.txt"
connection_config_path = BASE_PATH / "config" / "connection.yaml"

with open(resume_txt_path, "r") as f:
    resume_txt = f.read()
with open(connection_config_path, "r") as f:
    connection_config = yaml.safe_load(f)

def get_note_text_prompt(profile_info):

    system_prompt = f"""
    You are writing a short, personalized LinkedIn connection note to build a genuine professional relationship.
    Inputs you will receive:
    1. Person’s first name and tagline: {profile_info}
    2. Person's company: {connection_config.get("filter_company", {}).get("filter_company", "")}
    2. My resume text: {resume_txt}

    Instructions:
    1. Address the person by their first name.
    2. Determine whether the person appears to be a recruiter, talent partner, or in talent management based on their tagline.
    3. If the person is not a recruiter:
        * If the tagline mentions a role, company, domain, or achievement, reference one specific aspect that is genuinely impressive. If nothing stands out, skip this naturally.
        * Express sincere enthusiasm about learning from their experience or perspective.
    4. If the person is a recruiter or in talent management:
        * Briefly introduce me using only relevant resume details to establish credibility and relatability.
        * Do not position the message as wanting to learn from their work.
        * Focus on shared domains, interests, or alignment (if avialable) with the types of roles or teams they support.
    5. Review my resume and only incorporate details that are clearly relevant. Do not force relevance.
    6. End with a light, friendly call to action (e.g., open to connecting or staying in touch)

    Tone & constraints:
    * Conversational, warm, and professional
    * Authentic and respectful, like reaching out to a respected colleague
    * No emojis, no buzzwords, no salesy language
    * Maximum 300 characters total
    * Output only the final message text, nothing else
    """


    messages = [
    {"role": "system", "content": system_prompt},
    ]

    return messages