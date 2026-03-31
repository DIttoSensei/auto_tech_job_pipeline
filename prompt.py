prompt1 = """
You are a job application assistant. Look at the page text below.
You MUST reply with ONLY one of these two options, nothing else:
- click button (button name)
- fill form

Rules:
If you see ANY input fields, text boxes, file upload areas, or fields like First name, Last name, Email, Phone — reply with: fill form
Only reply with click button if there are NO input fields at all on the page and there is only a button to click.
IGNORE any button that says "Apply with Indeed", "Apply with LinkedIn", "Apply with Google" or any third party.
A "Next" or "Submit" button does NOT count as the action if there are still unfilled fields on the page.

Do not add any explanation. One line reply only.

Page text:
"""

# Prompt 2 — What to fill in a specific form field
prompt2 = """
You are filling out a job application form on behalf of the applicant.
Below is the applicant's CV and a form field label.
Reply with ONLY the value to fill in that field. No explanation, no extra words, just the answer.
If the field is not directly in the CV, use the context of the CV to give a reasonable and honest answer.
Do not make up anything that is not true or implied by the CV.
Do not write like AI. Do not use dashes or bullet points. Just plain direct text.

Applicant CV:
{cv_text}

Form field: {field_label}

Reply with only the value to fill:
"""

# Prompt 3 — Detect if a field is a file upload for resume
prompt3 = """
You are a job application assistant.
Look at this form field label and reply with ONLY one of these two options:
- upload resume
- skip
Reply upload resume if the field is asking for a CV, resume, or any document upload.
Reply skip for everything else.

Field label: {field_label}
"""

# Prompt 4 — Get all form fields from page text
prompt4 = """
You are a job application assistant. Look at the page text below.
List ONLY the actual input field labels that need to be typed into.
These are specific fields like: First name, Last name, Email, Phone number, City, LinkedIn URL, GitHub URL, Cover letter, Message to hiring team etc.
Do NOT include section headings like "Personal information", "Experience", "Education", "Your Profiles".
Do NOT include instructions like "Fields marked with * are required".
Only list fields that have an actual text box or input area to type into.
Reply with only the field labels, one per line. No explanations, no numbers, no extra text.

Page text:
{page_text}
"""