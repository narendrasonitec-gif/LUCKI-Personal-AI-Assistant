# Lucki AI — Build and Install

## Build requirements
- Windows 10/11, 64-bit
- Python 3.11 or 3.12
- Internet connection for package installation

## Build
1. Extract the project to a permanent folder.
2. Create `.env` from `.env.example` and add your own API key.
3. Run `build_exe.bat`.
4. Find the result at `dist\Lucki\Lucki.exe`.

The PyInstaller spec uses `assets/lucki_icon.ico` for the EXE icon and includes the app assets. Build an onedir distribution; copy the whole `dist\Lucki` folder to another PC.

## Startup
Lucki registers itself for the current Windows user's sign-in. It cannot launch before a user signs in. Startup may be controlled by Windows policy. Manage it from Task Manager → Startup apps.

## Data locations
- Packaged conversation memory: `%APPDATA%\LuckiAI\lucki_data.json`
- Packaged generated files: `%USERPROFILE%\Documents\Lucki AI\generated`
- Private API configuration: `.env` beside the executable

## Important
Do not include `.env` in shared ZIP files, GitHub, or public releases. The EXE does not make an API key secret; keep the key private. Never assume the app can bypass Windows access controls or administrator prompts.
