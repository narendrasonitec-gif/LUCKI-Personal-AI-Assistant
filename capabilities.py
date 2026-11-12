"""Human-facing Lucki capability/help catalog.

This is intentionally a truthful catalog: it describes features that are
implemented or connected in this build, and separates future integrations.
"""

CAPABILITY_TEXT = """Main Lucki hoon. Main aapki help in areas mein kar sakta hoon:

• Study & learning — concepts samjhana, questions solve karna, notes, revision, examples.
• Coding — C, C++, Python, web development, debugging, project structure aur copy-paste-ready code.
• Project building — idea se planning, files/modules, features, debugging aur step-by-step development.
• Assignments — easy-language answers, reports, lab-record content aur formatting help.
• Research — current information ke liye web search layer available hone par sourced answers.
• Writing — emails, applications, captions, documentation, README aur professional text.
• PDF — student-ready PDF documents generate karna.
• PPT — presentation content aur PPTX generate karna; 16:9 ya 4:3.
• Images — local poster/layout output at HD/FHD/2K/4K sizes. True AI image synthesis needs a configured image provider.
• Screen help — jab aap bolo tab screen analyze karke uske basis par explain karna.
• PC controls — supported apps, websites aur computer actions ko execute karna.
• Tasks & notes — student workspace mein tasks manage karna.
• Voice — wake-word/voice workflow, subject to microphone, network and TTS dependencies.
• Privacy & safety — harmful, destructive, unauthorized hacking aur private/internal-secret requests ko block karna.

Main wahi action claim karta hoon jo Lucki ke connected tools ne actually kiya ho."""


def help_text():
    return CAPABILITY_TEXT
