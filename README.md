# YG Screen Extractor

A desktop application for **KDE Plasma** that lets you select a region of the
screen and extract its text using **OCR** (optical character recognition), with
the option to copy it to the clipboard or save it as a text file.

> Project status: **alpha** — first functional **MVP** (Minimum Viable Product),
> under active development. See [CHANGELOG.md](CHANGELOG.md).

---

## About

YG Screen Extractor captures a rectangular region of the screen and uses
**Tesseract OCR** to turn the image into text. It is designed for
**KDE Plasma 6 with KWin on Wayland**, where the capture is performed by
querying the `org.kde.KWin.ScreenShot2` D-Bus API through a small native
C++/Qt6 helper.

The main flow is:

1. The native helper asks KWin for a capture of the active monitor.
2. The Qt (PySide6) interface shows a selector to crop the region.
3. Tesseract recognizes the text in the selected region.
4. The text can be copied to the clipboard (`wl-copy`) or saved to a `.txt`.

In addition to the GUI mode, there is a **quick mode** (`--quick`) intended to
be bound to a global keyboard shortcut: it captures, recognizes, and copies the
text without opening the main window.

---

## Features

- Visual selection of the region to capture.
- OCR recognition with **Tesseract**.
- Bundled languages: **Spanish (`spa`)**, **English (`eng`)**, and **`spa+eng`**.
- Copy text to the clipboard on Wayland via `wl-copy`.
- Save the recognized text as a **TXT** file.
- Quick mode `--quick` for global keyboard shortcuts.
- **Multi-monitor** support (detects the active monitor in KWin).
- Graphical interface with **Qt6 / PySide6**, integrated with the Plasma theme.
- Automatic detection of the languages installed in Tesseract.

---

## System requirements

- **Distribution:** Arch Linux or derivatives compatible with `pacman`
  (Manjaro, EndeavourOS, Garuda, CachyOS, ArcoLinux, etc.).
- **Desktop environment:** KDE Plasma 6 with **KWin**.
- **Session:** Wayland (the clipboard uses `wl-copy`).
- **Architecture:** `x86_64` (or any architecture supported by the listed
  packages).
- **Permissions:** `sudo`/root permissions are required to install into `/opt`
  and `/usr/local`.

> The installer validates the distribution and will abort on systems that are
> not Arch Linux or a derivative.

---

## Dependencies

### System dependencies

Installed with `pacman`. The installer (`install.sh`) installs them
automatically, but they are listed here for reference:

| Package              | Purpose                                                 |
| -------------------- | ------------------------------------------------------- |
| `base-devel`         | Build tools (gcc, make, etc.).                          |
| `cmake`              | Building the native C++ helper.                         |
| `qt6-base`           | Qt6 libraries (Core, Gui, DBus) for the helper.         |
| `qt6-tools`          | Provides `qdbus6` to query the active monitor.          |
| `python`             | Interpreter for the application and the virtual env.    |
| `python-pip`         | Installing Python dependencies.                         |
| `tesseract`          | OCR engine.                                             |
| `tesseract-data-eng` | English language data for Tesseract.                    |
| `tesseract-data-spa` | Spanish language data for Tesseract.                    |
| `wl-clipboard`       | Provides `wl-copy` for copying on Wayland.              |

Manual installation of all dependencies:

```bash
sudo pacman -S --needed base-devel cmake qt6-base qt6-tools python python-pip \
    tesseract tesseract-data-eng tesseract-data-spa wl-clipboard
```

### Python dependencies

Defined in `requirements.txt` and installed inside the application's virtual
environment (`/opt/yg-screen-extractor/venv`):

| Package       | Required version      | Purpose                              |
| ------------- | --------------------- | ------------------------------------ |
| `PySide6`     | `>=6.8,<7`            | Qt6 graphical interface.             |
| `Pillow`      | `>=11,<13`            | Image handling and cropping.         |
| `pytesseract` | `>=0.3.13,<0.4`       | Bridge between Python and Tesseract. |

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/YosefGemini/YG-Screen-Extractor.git yg-screen-extractor
   cd yg-screen-extractor
   ```

2. Run the installer:

   ```bash
   ./install.sh
   ```

   If the script does not have execute permissions:

   ```bash
   chmod +x install.sh uninstall.sh
   ./install.sh
   ```

The installer performs the following steps:

1. Verifies that the required source files are present.
2. Checks that the system is Arch Linux or a derivative.
3. Installs the system dependencies with `pacman`.
4. Verifies the Tesseract `eng` and `spa` languages.
5. Copies the code to `/opt/yg-screen-extractor`.
6. Creates a virtual environment and installs `requirements.txt`.
7. Builds and installs the native C++ helper with CMake.
8. Installs the launcher and the `.desktop` file for the application menu.

### Installation paths

| Item                          | Path                                                        |
| ----------------------------- | ----------------------------------------------------------- |
| Application directory         | `/opt/yg-screen-extractor`                                  |
| Python virtual environment    | `/opt/yg-screen-extractor/venv`                             |
| Launcher                      | `/usr/local/bin/yg-screen-extractor`                        |
| C++ capture helper            | `/usr/local/bin/yg-screen-extractor-capture-helper`         |
| Desktop entry (`.desktop`)    | `/usr/local/share/applications/yg-screen-extractor.desktop` |
| Temporary capture             | `~/capture.png`                                             |

---

## KDE Plasma shortcut

Quick mode lets you launch the capture and copy the text with a key combination.
To configure it:

1. Open **System Settings**.
2. Go to **Shortcuts** → **Custom Shortcuts**.
3. Click **Edit** → **New** → **Global Shortcut** → **Command/URL**.
4. On the **Action** tab, set the name to `YG Screen Extractor` and the command
   to:

   ```bash
   /usr/local/bin/yg-screen-extractor --quick
   ```

5. On the **Trigger** tab, click **Add** and press the desired key combination
   (for example `Meta+Shift+O`).
6. Click **Apply**.

When you press the shortcut, the application captures the active monitor, shows
the region selector, and copies the recognized text to the clipboard.

> Note: quick mode uses the `spa+eng` language. Both Tesseract language data
> files must be installed.

---

## Usage

**From the application menu:** search for *YG Screen Extractor* in the launcher.

**From the terminal (windowed mode):**

```bash
yg-screen-extractor
```

**Quick mode (capture, recognize, and copy):**

```bash
yg-screen-extractor --quick
```

In the main window you can choose the recognition language, capture the region,
and then **copy** the result, **save it as TXT**, or **clear** it.

---

## Uninstallation

Run the uninstall script:

```bash
./uninstall.sh
```

The script asks for confirmation and removes:

- The launcher `/usr/local/bin/yg-screen-extractor`.
- The helper `/usr/local/bin/yg-screen-extractor-capture-helper`.
- The associated `.desktop` files.
- The `/opt/yg-screen-extractor` directory (code and virtual environment).

It does **not** remove the system packages installed with `pacman`, nor your
captures or personal KDE shortcuts.

---

## Project structure

```text
.
├── install.sh                  # Main installer
├── uninstall.sh                # Uninstall script
├── requirements.txt            # Python dependencies
├── pyproject.toml              # Project metadata and configuration
├── CHANGELOG.md                # Changelog
├── LICENSE                     # GPL-3.0-or-later license
├── .gitignore                  # Files excluded from Git
├── src/
│   └── screen_extractor/
│       ├── main.py             # Entry point (--quick / GUI)
│       ├── app.py              # Qt application lifecycle
│       ├── config.py           # Paths and central configuration
│       ├── capture/            # Integration with the capture helper
│       ├── services/           # OCR and clipboard
│       ├── shortcuts/          # Future KDE shortcut integration
│       └── ui/                 # Main window and region selector
├── capture-helper/             # Native C++/Qt6 helper (CMake)
│   ├── main.cpp
│   └── CMakeLists.txt
├── packaging/                  # Launcher and .desktop file
└── tests/                      # Manual OCR and capture tests
```

---

## Troubleshooting

**`No se encontró el helper` / capture fails**
Check that the helper is installed:

```bash
ls -l /usr/local/bin/yg-screen-extractor-capture-helper
```

If it does not exist, run `./install.sh` again.

**`No se pudo conectar con la API de capturas de KWin`**
Make sure you are in a **KDE Plasma session with KWin** (not another environment
or an X11 session without KWin). Verify the D-Bus connection:

```bash
qdbus6 org.kde.KWin /KWin org.kde.KWin.activeOutputName
```

**`No se encontró wl-copy`**
The clipboard requires `wl-clipboard` on Wayland:

```bash
sudo pacman -S wl-clipboard
```

**Languages are missing from the interface**
Install the required language data and reopen the application:

```bash
sudo pacman -S tesseract-data-eng tesseract-data-spa
```

**The detected monitor does not match**
Quick mode queries the active monitor in KWin. Make sure the cursor is on the
desired monitor when you trigger the capture.

---

## Contributing

Contributions are welcome. Open an *issue* or send a *pull request* describing
the proposed change.

---

## License

This project is distributed under the **GNU General Public License v3.0 or
later** (`GPL-3.0-or-later`). See the [LICENSE](LICENSE) file for the full text.

This license is compatible with the dependencies used: the **Qt6 / PySide6**
libraries are dynamically linked under **LGPL-3.0**, while **Pillow** (MIT-CMU),
**pytesseract**, and **Tesseract** (Apache-2.0) use permissive licenses.
