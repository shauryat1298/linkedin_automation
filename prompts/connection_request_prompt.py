



def get_note_text_prompt(profile_name):

    system_prompt = f"""
    Craft a warm, personalized LinkedIn connection request from a experienced, enthusiastic data scientist. Use the provided profile information to create a genuine, friendly message that:

    1. Addresses the person by first name
    2. References a specific aspect of their work, role, or company that's truly impressive
    3. Draws a brief, authentic connection between their expertise and the sender's interests or goals
    4. Expresses sincere enthusiasm about the potential to learn from them
    5. Ends with a light, friendly call to action

    Keep the tone conversational yet professional. Aim for warmth and authenticity, as if reaching out to a respected colleague. Limit the message to 300 characters.
    Profile info: {profile_name}

    Example structure (adapt creatively):
    Hi [Name],
Loved your work on [specific project/achievement] at [Company]. I’m a data scientist interested in [related aspect] and would be glad to connect and learn from your experience.
    """


    messages = [
    {"role": "system", "content": system_prompt},
    ]

    return messages