# 🌊 Boomi Flow & Data Inspector

A high-performance diagnostic tool for Boomi developers. This application transforms flat, monochrome `.log` files into an interactive, color-coded execution trace, making it easy to identify performance bottlenecks and inspect raw data payloads.

## 🛠️ Architectural Rationale

To build a tool that effectively "visualizes" a wall of text, we treat the log file as a **stream of structured data** rather than just a flat document.

1.  **The "Sieve" (Regex):** We use a high-precision Regular Expression to isolate **Metadata** (Timestamps/Log Levels) from **Business Data** (Shape Names/Messages). It identifies ISO-8601 timestamps and recognizes multi-line noise (like JSON/XML) as continuation data.
2.  **The "Assembler" (Parsing Loop):** Standard parsers fail on multi-line payloads. Our loop detects lines that lack a timestamp and automatically appends them to the previous shape, keeping the payload "attached" to its context.
3.  **Vectorized Durations:** Boomi logs only record the "Start Time" of a shape. We use **Pandas Vectorization** to calculate the time difference between steps instantly, identifying exactly where a process is hanging.
4.  **Agnostic Classifier:** The tool categorizes rows into functional types:
    * 🟢 **Start/Entry:** New shape execution.
    * 🔵 **Data In:** Documents found or received (e.g., API responses).
    * 🟠 **Logic/Filter:** Decisions, stops, or cache misses.
    * 🔴 **Error:** Failures or exceptions.

---

## 🚀 Installation & Setup

### 1. Install Python & Pip
Ensure you have Python 3.10 or higher installed.

* **macOS:** Open Terminal and run `brew install python` or download from [python.org](https://www.python.org/).
* **Windows:** Download from [python.org](https://www.python.org/). **CRITICAL:** Check the box **"Add Python to PATH"** during installation.

### 2. Set Up Virtual Environment (`.venv`)
Open your terminal or command prompt in the project folder and run the following:

#### **macOS / Linux:**
```bash
# Create the environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install dependencies
pip install streamlit pandas python-dateutil
```
