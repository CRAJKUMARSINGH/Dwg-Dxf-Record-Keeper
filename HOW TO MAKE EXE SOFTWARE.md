# How to Build the Standalone EXE

This guide explains how to convert the `BridgeMaster Pro` Python codebase into a single, standalone Windows `.exe` application. This executable can be distributed to clients or engineers who do not have Python installed on their computers.

## Prerequisites

Before building the `.exe`, ensure that you are on the Windows machine where you intend to compile the software and have a working Python environment.

1. **Open PowerShell or Command Prompt**.
2. Navigate to your project directory:
   ```powershell
   cd c:\Users\Rajkumar\Downloads\Dwg-Dxf-Record-Keeper
   ```
3. **Install Dependencies**: Ensure all required packages (including the Nuitka compiler) are installed.
   ```powershell
   pip install -r requirements.txt
   ```

## The Build Process

The project uses a script called `build_exe.py` that utilizes the **Nuitka** compiler. Nuitka translates Python code into C, compiling it into a highly optimized executable, which hides your source code and improves performance.

To start the compilation, run:
```powershell
py build_exe.py
```

### What happens during the build?
1. Nuitka will scan your `main_app.py` script and track down every imported module (PySide6, ezdxf, etc.).
2. It will compile these modules. **This step is very CPU intensive and may take between 5 to 15 minutes** depending on your hardware. Please do not close the terminal while it says "Executing...".
3. It packages the `ui`, and `config` folders into the final binary.
4. It compresses the result into a single `.exe` file.

## Finding the Output

Once the terminal prints `✅ Build Successful! Check the 'dist' folder.`:
1. Go into the newly created `dist/` folder in your project directory.
2. Inside, you will find `BridgeSuitePro.exe`.
3. This is your final commercial product.

## Distribution
You can now copy `BridgeSuitePro.exe` to a USB drive or upload it to Google Drive/Dropbox. When a user double-clicks this file on any standard Windows machine, the BridgeMaster Pro GUI will launch instantly, without needing a Python installation or source code!

> **Troubleshooting Note**: Antivirus programs sometimes falsely flag compiled Python `.exe` files as suspicious (since they contain an embedded Python interpreter). If Windows Defender blocks it, simply click "More info" -> "Run anyway", or add the `dist/` folder to your Antivirus exclusions.
