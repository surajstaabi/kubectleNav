# KubectleNav

A cross-platform (Windows/Linux) GUI tool to view Kubernetes pod/container logs using `kubectl` and Tkinter.

## Features
- Select namespace, pod, and container interactively
- View and follow logs in real time
- Set number of log lines to show
- Clear and stop logs
- Simple, fast, and easy to use

---

## Prerequisites
- **Python 3.7+**
- **kubectl** (configured and accessible in your PATH)
- Access to a Kubernetes cluster

---

## Installation

### 1. Clone the repository

---

> **Tip:** On Ubuntu/Linux, it is recommended to use a Python virtual environment to avoid dependency conflicts:
> ```sh
> python3 -m venv venv
> source venv/bin/activate
> ```

### 2. Install dependencies

#### On **Linux** (Ubuntu/Debian):
```sh
sudo apt update
sudo apt install python3 python3-tk
```

#### On **Windows**:
- Download and install [Python 3.x](https://www.python.org/downloads/). Ensure you check "Add Python to PATH" during installation.
- Tkinter is included by default with Python on Windows. No extra steps needed.

#### (Optional) Using pip (all platforms):
```sh
pip install tk
```

---

## Usage

### Run the application
```sh
python main.py
```

- The GUI will open. Select the namespace, pod, and container to view logs.
- Set the number of lines and whether to follow logs live.
- Click **Show Logs** to start viewing.

---

## Building an Executable (Optional)

You can build a standalone executable using PyInstaller (Linux only, script provided):

1. Install PyInstaller:
   ```sh
   pip install pyinstaller
   ```
2. Run the build script:
   ```sh
   ./build_executable.sh
   ```
   - Enter a version number when prompted.
   - The executable will be created in the `dist/` folder.

---

## Troubleshooting
- If you get an error about `tkinter` not found:
  - On Linux: Install with `sudo apt install python3-tk`
  - On Windows: Ensure you installed Python from python.org (Tkinter is included)
- Ensure `kubectl` is installed and configured to access your cluster.

---

## License
MIT

---

## Credits
Made by mochiron-desu 