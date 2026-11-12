import re
from ai import ask_ai
from memory import remember, add_note, add_task

def local_student_command(text):
    m=re.match(r'(remember|yaad rakho)\s+(.+?)\s+(is|hai)\s+(.+)',text,re.I)
    if m:
        remember(m.group(2).strip(),m.group(4).strip()); return 'Okay, I will remember that.'
    low=text.lower()
    if low.startswith(('add task ','todo ')):
        title=re.sub(r'^(add task|todo)\s+','',text,flags=re.I).strip()
        if title: add_task(title); return f'Task added: {title}'
    if low.startswith(('add note ','note ')):
        body=re.sub(r'^(add note|note)\s+','',text,flags=re.I).strip()
        if body: add_note('Voice Note',body); return 'Note saved.'
    return None
