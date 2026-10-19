import os
import subprocess
import ollama

MODEL = "qwen2.5:7b"

# --- Verktygsimplementationer ---

def read_file(path: str) -> str:
    try:
        with open(os.path.expanduser(path), encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Fel: {e}"


def write_file(path: str, content: str) -> str:
    try:
        with open(os.path.expanduser(path), "w", encoding="utf-8") as f:
            f.write(content)
        return f"Filen {path} sparad."
    except Exception as e:
        return f"Fel: {e}"


def run_command(command: str) -> str:
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        return output or "(inget utdata)"
    except subprocess.TimeoutExpired:
        return "Fel: Kommandot tog för lång tid (>30s)"
    except Exception as e:
        return f"Fel: {e}"


def search_code(pattern: str, directory: str = ".", file_pattern: str = "*.py") -> str:
    try:
        result = subprocess.run(
            ["grep", "-r", "-n", pattern, directory, f"--include={file_pattern}"],
            capture_output=True, text=True, timeout=10,
        )
        return result.stdout or f"Inga träffar för '{pattern}' i {directory}"
    except Exception as e:
        return f"Fel: {e}"


def list_files(directory: str = ".") -> str:
    try:
        result = subprocess.run(
            ["find", directory, "-maxdepth", "2", "-type", "f"],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout or "Inga filer hittades"
    except Exception as e:
        return f"Fel: {e}"


# --- Verktygsregister ---

TOOL_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "run_command": run_command,
    "search_code": search_code,
    "list_files": list_files,
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Läs innehållet i en fil.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Sökväg till filen."}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Skriv innehåll till en fil.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Sökväg till filen."},
                    "content": {"type": "string", "description": "Innehållet att skriva."},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Kör ett shell-kommando och returnera utdata.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Kommandot att köra."}
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_code",
            "description": "Sök efter ett mönster i kodfiler med grep.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Mönstret att söka efter."},
                    "directory": {"type": "string", "description": "Katalog att söka i (standard: .)."},
                    "file_pattern": {"type": "string", "description": "Filmönster t.ex. *.py (standard: *.py)."},
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Lista filer i en katalog.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "Katalogen att lista (standard: .)."}
                },
                "required": [],
            },
        },
    },
]


# --- Agentic loop ---

SYSTEM_PROMPT = (
    "Du är en hjälpsam kodassistent med tillgång till verktyg för att "
    "läsa/skriva filer, köra kommandon och söka i kod. "
    "Använd verktygen när det behövs för att ge korrekta svar."
)


def run_agent(user_message: str, history: list | None = None, system_prompt: str | None = None) -> tuple[str, list]:
    """Kör agenten och returnera (svar, uppdaterad_historik)."""
    system = system_prompt or SYSTEM_PROMPT
    messages = list(history) if history else [{"role": "system", "content": system}]
    messages.append({"role": "user", "content": user_message})

    while True:
        response = ollama.chat(model=MODEL, messages=messages, tools=TOOLS)
        msg = response.message
        messages.append(msg)

        if not msg.tool_calls:
            return msg.content or "", messages

        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            args = tool_call.function.arguments or {}
            func = TOOL_FUNCTIONS.get(name)
            result = func(**args) if func else f"Okänt verktyg: {name}"
            messages.append({"role": "tool", "content": result})


if __name__ == "__main__":
    print(f"Assistent ({MODEL}) — skriv 'avsluta' för att stänga\n")
    history: list = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        try:
            fraga = input("Du: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHejdå!")
            break

        if fraga.lower() in ("avsluta", "exit", "quit"):
            print("Hejdå!")
            break

        if not fraga:
            continue

        svar, history = run_agent(fraga, history)
        print(f"\nAssistent: {svar}\n")
