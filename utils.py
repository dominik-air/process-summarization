import os


def get_process_files() -> list[str]:
    files = []
    for file in os.listdir("processes"):
        if file.endswith(".txt"):
            files.append(f"processes/{file}")
    return files


def format_summary(process_filename: str, summary: str) -> str:
    formatted = f"Process filename: {process_filename.split('/')[1]}\n"
    formatted += summary + "\n"
    formatted += "-"*100
    return formatted
