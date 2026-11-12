LUCKI AI — UPDATED SOURCE PACKAGE
=================================

Is ZIP mein Lucki ka cleaned aur updated source code hai. Yeh ready-made EXE nahi hai.
Windows par build_exe.bat chala kar branded Lucki.exe banaya ja sakta hai.

IMPORTANT UPDATES
- Startup registry path fix kiya gaya; Lucki current Windows user ke sign-in par start ho sakta hai.
- Packaged EXE ke liye Lucki custom icon spec mein set hai.
- Packaged mode mein chat memory AppData mein aur generated files Documents\Lucki AI mein save honge.
- Duplicate nested project aur Python bytecode hata diya gaya.
- Private .env aur personal chat/profile data ZIP se hata diye gaye.
- .env.example diya gaya hai; isse copy karke apni private .env file banao.

SETUP
1. ZIP ko D:\LuckiAI jaise permanent folder mein extract karo.
2. Windows par Python 3.11/3.12 install karo.
3. Folder mein terminal kholkar: python -m pip install -r requirements.txt
4. .env.example ko copy karke .env naam do.
5. Apni valid Gemini API key .env mein daalo.
6. RUN_LUCKI.bat ya python main.py chalao.

EXE
- Windows par build_exe.bat chalao.
- Output: dist\Lucki\Lucki.exe
- Dusre PC par poora dist\Lucki folder copy karo, sirf EXE nahi.
- EXE aur app window mein Lucki ka icon configured hai.

AUTO START
Lucki run hone par current Windows account ke Startup mein register hota hai.
Yeh Windows sign-in ke baad start hota hai, boot screen par ya sign-in se pehle nahi.
Task Manager > Startup apps se disable kar sakte ho.

PC ACCESS
Lucki supported apps aur controls operate kar sakta hai, lekin Windows passwords,
administrator prompts, protected folders, security settings ya consent ko bypass nahi karega.
Har app/action har PC par guaranteed nahi hota. Administrator mode default mein use mat karo.

NOT INCLUDED YET
- Android app aur desktop/mobile sync abhi future development hai.
- True AI image generation ke liye image provider connect karna baaki hai.
- Har possible PC action ka unrestricted control available nahi hai.
- Windows par actual EXE build aur microphone testing zaroori hai.

API KEY SECURITY
Tumhari uploaded ZIP mein .env ke andar API key thi. Safety ke liye provider dashboard
mein us key ko revoke/regenerate karo. Nayi key sirf apni private local .env mein rakho.
