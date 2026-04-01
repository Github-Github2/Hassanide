import tkinter as tk
from tkinter import filedialog
import subprocess
import google.generativeai as genai

# ----------------- FONT -----------------
FONT = ("JetBrains Mono NL", 12)

# ----------------- AI SETUP (GEMINI) -----------------
API_KEY = "AIzaSyAq3-qumMhF11jMuE76HNqALAb45JmeFgc"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def ask_ai(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Error: {e}"

# ----------------- GLOBAL LANGUAGE -----------------
current_lang = "Python"

# ----------------- SYNTAX DATA -----------------
KEYWORDS = [
    "def","class","import","from","as","if","elif","else","while","for","in",
    "try","except","finally","return","with","lambda","pass","break","continue",
    "True","False","None"
]

BUILTINS = [
    "print","len","range","input","int","str","float","list","dict","set","tuple"
]

# ----------------- SYNTAX HIGHLIGHT -----------------
def highlight(event=None):
    for tag in editor.tag_names():
        editor.tag_remove(tag, "1.0", tk.END)

    for word in KEYWORDS:
        start = "1.0"
        while True:
            start = editor.search(rf"\m{word}\M", start, stopindex=tk.END, regexp=True)
            if not start:
                break
            end = f"{start}+{len(word)}c"
            editor.tag_add("keyword", start, end)
            start = end

    for word in BUILTINS:
        start = "1.0"
        while True:
            start = editor.search(rf"\m{word}\M", start, stopindex=tk.END, regexp=True)
            if not start:
                break
            end = f"{start}+{len(word)}c"
            editor.tag_add("builtin", start, end)
            start = end

    # strings
    for quote in ['"', "'"]:
        start = "1.0"
        while True:
            start = editor.search(quote, start, stopindex=tk.END)
            if not start:
                break
            end = editor.search(quote, f"{start}+1c", stopindex=tk.END)
            if not end:
                break
            editor.tag_add("string", start, f"{end}+1c")
            start = f"{end}+1c"

    # comments
    start = "1.0"
    while True:
        start = editor.search("#", start, stopindex=tk.END)
        if not start:
            break
        end = editor.search("\n", start, stopindex=tk.END)
        if not end:
            end = tk.END
        editor.tag_add("comment", start, end)
        start = end

# ----------------- FILE FUNCTIONS -----------------
def open_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        with open(file_path, "r") as file:
            editor.delete(1.0, tk.END)
            editor.insert(tk.END, file.read())
        highlight()

def save_file():
    file_path = filedialog.asksaveasfilename()
    if file_path:
        with open(file_path, "w") as file:
            file.write(editor.get(1.0, tk.END))

# ----------------- RUN CODE -----------------
def run_code():
    code = editor.get(1.0, tk.END)
    output.delete(1.0, tk.END)

    if "#include" in code:
        lang = "C"
    elif "std::" in code or "#include <iostream>" in code:
        lang = "C++"
    elif "public class" in code:
        lang = "Java"
    else:
        lang = "Python"

    output.insert(tk.END, f"Detected Language: {lang}\n\n")

    try:
        if lang == "Python":
            with open("temp.py", "w") as f:
                f.write(code)

            result = subprocess.run(["python", "temp.py"], capture_output=True, text=True)
            output.insert(tk.END, result.stdout + result.stderr)

        elif lang == "C":
            with open("temp.c", "w") as f:
                f.write(code)

            c = subprocess.run(["gcc", "temp.c", "-o", "temp.exe"], capture_output=True, text=True)
            if c.returncode != 0:
                output.insert(tk.END, c.stderr)
                return

            r = subprocess.run(["temp.exe"], capture_output=True, text=True)
            output.insert(tk.END, r.stdout + r.stderr)

        elif lang == "C++":
            with open("temp.cpp", "w") as f:
                f.write(code)

            c = subprocess.run(["g++", "temp.cpp", "-o", "temp.exe"], capture_output=True, text=True)
            if c.returncode != 0:
                output.insert(tk.END, c.stderr)
                return

            r = subprocess.run(["temp.exe"], capture_output=True, text=True)
            output.insert(tk.END, r.stdout + r.stderr)

        elif lang == "Java":
            with open("Main.java", "w") as f:
                f.write(code)

            c = subprocess.run(["javac", "Main.java"], capture_output=True, text=True)
            if c.returncode != 0:
                output.insert(tk.END, c.stderr)
                return

            r = subprocess.run(["java", "Main"], capture_output=True, text=True)
            output.insert(tk.END, r.stdout + r.stderr)

    except Exception as e:
        output.insert(tk.END, f"Error: {e}")

# ----------------- AI FUNCTIONS -----------------
def send_ai():
    prompt = ai_input.get("1.0", tk.END)
    response = ask_ai(prompt)

    ai_output.insert(tk.END, "You: " + prompt + "\n")
    ai_output.insert(tk.END, "AI: " + response + "\n\n")

def explain_code():
    code = editor.get("1.0", tk.END)
    prompt = f"""
Explain this code clearly like a teacher.
Break it into parts and keep it simple:

{code}
"""
    response = ask_ai(prompt)
    ai_output.insert(tk.END, response + "\n\n")

def fix_code():
    code = editor.get("1.0", tk.END)
    prompt = f"Fix this code and explain the mistakes:\n{code}"

    response = ask_ai(prompt)
    ai_output.insert(tk.END, response + "\n\n")

# ----------------- EDITOR -----------------
def open_editor():
    title_frame.destroy()

    menu = tk.Menu(root)
    root.config(menu=menu)

    filemenu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="File", menu=filemenu)
    filemenu.add_command(label="Open", command=open_file)
    filemenu.add_command(label="Save", command=save_file)
    filemenu.add_command(label="Exit", command=root.quit)

    runmenu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Run", menu=runmenu)
    runmenu.add_command(label="Run Code", command=run_code)

    paned = tk.PanedWindow(root, orient=tk.VERTICAL)
    paned.pack(fill="both", expand=True)

    top = tk.PanedWindow(paned, orient=tk.HORIZONTAL)
    bottom = tk.Frame(paned)

    paned.add(top)
    paned.add(bottom)

    left = tk.Frame(top)
    right = tk.Frame(top)

    top.add(left)
    top.add(right)

    # ---- EDITOR ----
    global editor
    editor = tk.Text(left, bg="#1e1e1e", fg="white", insertbackground="white", font=FONT)
    editor.pack(fill="both", expand=True)

    editor.tag_config("keyword", foreground="#569cd6")
    editor.tag_config("string", foreground="#d69d85")
    editor.tag_config("comment", foreground="#6a9955")
    editor.tag_config("builtin", foreground="#4ec9b0")

    editor.bind("<KeyRelease>", highlight)

    # ---- AI PANEL ----
    global ai_input, ai_output

    ai_input = tk.Text(right, height=8, bg="#1e1e1e", fg="white", font=FONT)
    ai_input.pack(fill="x")

    btn_frame = tk.Frame(right, bg="#1e1e1e")
    btn_frame.pack(fill="x")

    tk.Button(btn_frame, text="Ask AI", command=send_ai).pack(side="left")
    tk.Button(btn_frame, text="Explain Code", command=explain_code).pack(side="left")
    tk.Button(btn_frame, text="Fix Code", command=fix_code).pack(side="left")

    ai_output = tk.Text(right, bg="#1e1e1e", fg="#00bfff", font=FONT)
    ai_output.pack(fill="both", expand=True)

    # ---- OUTPUT ----
    global output
    output = tk.Text(bottom, bg="#1e1e1e", fg="#00ff88", font=FONT)
    output.pack(fill="both", expand=True)

    root.bind("<F5>", lambda e: run_code())

# ----------------- UI -----------------
root = tk.Tk()
root.title("HASSANIDE IDE")
root.geometry("1000x600")

title_frame = tk.Frame(root, bg="#1e1e1e")
title_frame.pack(fill="both", expand=True)

tk.Label(title_frame, text="HASSANIDE IDE", font=("JetBrains Mono NL", 30),
         fg="white", bg="#1e1e1e").pack(pady=40)

tk.Label(title_frame, text="Code • Build • Run • AI", font=("JetBrains Mono NL", 14),
         fg="gray", bg="#1e1e1e").pack()

tk.Button(title_frame, text="START", font=("JetBrains Mono NL", 16),
          command=open_editor).pack(pady=30)

root.mainloop()