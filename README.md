# Alien Invasion

**POLY 1203: Foundations of Programming for Emerging Technologies**

---

Welcome to Alien Invasion! This is your game project for the rest of the semester. You'll build it step by step using **Python**, **Pygame**, and **GitHub Copilot**.

## Quick Setup

If you already have Python and VS Code installed, here's the fast version:

```bash
pip install -r requirements.txt
```

(Mac users: use `pip3` instead of `pip`.)

Verify it worked:

```bash
python -c "import pygame; print(pygame.ver)"
```

(Mac users: use `python3` instead of `python`.)

If you see a version number like `2.6.1`, you're good to go.

---

## Full Setup (First Time)

### 1. Install Python

- Go to [python.org/downloads](https://www.python.org/downloads/) and download the latest version.
- **Windows:** On the very first screen of the installer, **check the box that says "Add python.exe to PATH"** before clicking Install Now. This is the most important step. If you miss it, nothing else will work.
- **Mac:** Run the installer with default settings. On Mac, you'll use `python3` and `pip3` instead of `python` and `pip`.

Verify: open a terminal and type `python --version` (Windows) or `python3 --version` (Mac). You should see `Python 3.12.x` or similar.

### 2. Install VS Code + Copilot

- Download [VS Code](https://code.visualstudio.com/) and install it.
- Open VS Code and install three extensions (click the Extensions icon on the left sidebar):
  1. **Python** (by Microsoft)
  2. **GitHub Copilot** (by GitHub)
  3. **GitHub Copilot Chat** (by GitHub)
- Sign into GitHub when prompted. Copilot is free for students through [GitHub Education](https://education.github.com/).

### 3. Install Pygame

Open the terminal in VS Code (`Ctrl+`` on Windows, `Cmd+`` on Mac) and run:

```bash
pip install -r requirements.txt
```

(Mac: `pip3 install -r requirements.txt`)

### 4. Verify Everything

```bash
python -c "import pygame; print(pygame.ver)"
```

(Mac: `python3 -c "import pygame; print(pygame.ver)"`)

You should see a version number. You might also see "Hello from the pygame community" — that's normal.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python is not recognized` (Windows) | Uninstall Python, reinstall from python.org, and **check the PATH box** this time. |
| Opens the Microsoft Store (Windows) | Same fix — reinstall Python with the PATH checkbox. |
| `command not found` (Mac) | Use `python3` instead of `python`. |
| `pip is not recognized` | Try `python -m pip install -r requirements.txt` |
| `No module named pygame` | Run `pip install pygame` (or `pip3` on Mac). |
| Copilot won't activate | Click the person icon in VS Code's bottom-left. Sign into GitHub. If needed, activate student benefits at [education.github.com](https://education.github.com/). |

---

## Project Structure

As you build, your project will grow to look something like this:

```
alien-invasion/
├── alien_invasion.py    ← Main game file (you'll create this)
├── settings.py          ← Game settings class (you'll create this)
├── ship.py              ← Ship class (you'll create this)
├── bullet.py            ← Bullet class (you'll create this)
├── PROMPTS.md           ← Log of your Copilot prompts
├── DEVLOG.md            ← Your development journal
├── requirements.txt     ← Python dependencies
└── README.md            ← This file
```

---

## Resources

- **Chapter 12 (Copilot Edition)** — assigned via Hypothesis in Canvas
- **Homework exercises** — handed out in class or posted in Canvas
- Your instructor and Copilot Chat are your two best debugging partners. Use both.
