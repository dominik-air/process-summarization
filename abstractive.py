from transformers import pipeline
from utils import get_process_files, format_summary


if __name__ == "__main__":
    files = get_process_files()
    texts = []
    for filename in files:
        with open(filename) as f:
            text = "".join(s.strip() for s in f.readlines())
            texts.append(text)
    summarizer = pipeline("summarization", model="knkarthick/MEETING_SUMMARY")
    summaries = [out["summary_text"] for out in summarizer(texts)]
    for filename, summary in zip(files, summaries):
        print(format_summary(filename, summary))
