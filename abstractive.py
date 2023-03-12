from transformers import pipeline

if __name__ == "__main__":
    files = (
        "processes/GivingWaystoImprove.txt",
        "processes/MakingPositiveStatements.txt",
        "processes/ProvidingEffectiveFeedback.txt",
    )
    texts = []
    for filename in files:
        with open(filename) as f:
            text = "".join(s.strip() for s in f.readlines())
            texts.append(text)
    summarizer = pipeline("summarization", model="knkarthick/MEETING_SUMMARY")
    summaries = [out["summary_text"] for out in summarizer(texts)]
    for summary in summaries:
        print(summary)
        print("-" * 80)
