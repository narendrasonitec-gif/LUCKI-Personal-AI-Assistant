# LUCKI AI — Windows Personal Assistant

Lucki is a Python/PySide6 Windows desktop assistant. This package is an upgraded **source-code ZIP**. It is not a prebuilt Windows EXE and does not include an Android app.

## Included in this package

- PySide6 desktop interface with Lucki branding and custom icon assets.
- AI chat through a Gemini API key configured locally.
- Voice input/output and wake-word workflow (microphone, network recognition and TTS dependencies required).
- Supported Windows app launching and selected desktop controls.
- On-demand screen analysis (requires a working AI key and screen permission).
- Local conversation memory, notes and tasks.
- PDF and PowerPoint generation modules.
- Web search helper.
- Windows current-user sign-in auto-start registration.
- PyInstaller spec and Windows build script using the Lucki icon.

## Setup

1. Extract the ZIP to a permanent folder, for example `D:\LuckiAI`.
2. Install 64-bit Python 3.11 or 3.12 on the Windows build PC.
3. Open PowerShell in the extracted folder and run:
   `python -m pip install -r requirements.txt`
4. Copy `.env.example` to `.env`.
5. Put your own valid Gemini API key in `.env`. Never share this file.
6. Run `RUN_LUCKI.bat` or `python main.py`.

## Build the branded Windows EXE

On Windows, double-click `build_exe.bat`. It installs the requirements and builds an onedir package with PyInstaller.

Expected output:
`dist\Lucki\Lucki.exe`

The EXE and app window use `assets\lucki_icon.ico`. Copy the **entire** `dist\Lucki` folder to another PC, not just the EXE. Keep your private `.env` beside `Lucki.exe` if cloud AI is needed. Do not publish or send `.env`.

Python is needed on the build PC, but not normally on the destination PC for the packaged app. The destination PC still needs network access, valid API credentials, and Windows permissions for the features being used.

## Windows auto-start

When Lucki runs, it registers itself in the current Windows user's Startup Run key so it can launch after that user signs in. It does not run before Windows sign-in. Windows policies or security software may block this. To disable it, use **Task Manager → Startup apps**, or remove the `LuckiAI` entry from the current user's Run registry key.

## PC access and safety boundaries

Lucki can only control features exposed by its code and permitted by Windows. It does not have magical or unlimited access to every application, account, protected file, device, or administrator-only setting. It will not bypass passwords, UAC, security software, consent prompts, or access controls. Some actions require explicit user confirmation or manual interaction. Do not run Lucki as Administrator by default.

## Current limitations — read before relying on a feature

- This source package does not implement every item in the long-term roadmap.
- Android app and desktop/mobile synchronization are **future development**, not included as a working mobile client here.
- The local poster generator is not true prompt-to-image AI generation. A trusted image-generation provider must be connected for that.
- Voice recognition and speech output depend on microphone/audio drivers, installed packages, network availability and provider service availability.
- Browser and app automation is best-effort; app names, login state, UI changes and Windows permissions can affect results.
- Screen analysis is on-demand; review what is shared with the configured AI provider.
- This environment cannot validate Windows microphone behavior or produce/test a native Windows EXE. Build and test on a Windows PC.

## Privacy

The supplied `.env` and personal `lucki_data.json` have deliberately not been included. Lucki creates its local memory file when needed. In packaged mode, local memory is stored under `%APPDATA%\LuckiAI`. Generated documents are stored under `Documents\Lucki AI\generated`.

**API key warning:** The ZIP you uploaded contained a populated `.env` file. Treat that key as exposed because it was included in a shared archive. Revoke/regenerate it in the provider dashboard, then put the replacement only in your private local `.env`.
