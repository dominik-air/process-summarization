import spacy
from spacy.tokens import Doc
from spacy.tokens.span import Span
from utils import get_process_files, format_summary

def create_frequency_table(doc: Doc) -> dict[str, int]:
    frequency_table = dict()
    for token in doc:
        if token.is_stop or token.is_punct:
            continue
        word = token.lemma_
        if word in frequency_table:
            frequency_table[word] += 1
        else:
            frequency_table[word] = 1
    return frequency_table


def calculate_sentence_scores(
    sentences: list[Span], frequency_table: dict[str, int]
) -> list[float]:
    sentence_scores = [0] * len(sentences)
    for i, sentence in enumerate(sentences):
        non_stop_word_count = 0
        for word in sentence:
            if word.lemma_ in frequency_table:
                sentence_scores[i] += frequency_table[word.lemma_]
                non_stop_word_count += 1

        sentence_scores[i] /= non_stop_word_count
    return sentence_scores


def calculate_average_score(sentence_scores: list[float]) -> float:
    return sum(sentence_scores) / len(sentence_scores)


def get_summary(
    sentences: list[Span], sentence_scores: list[float], threshold: float
) -> str:
    summary = ""
    for i, sentence in enumerate(sentences):
        if sentence_scores[i] >= threshold:
            summary += " " + str(sentence)
    return summary.strip()


def run_extractive_algorithm(text: str) -> str:
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    frequency_table = create_frequency_table(doc)
    sentences = list(doc.sents)
    sentence_scores = calculate_sentence_scores(sentences, frequency_table)
    threshold = calculate_average_score(sentence_scores)
    return get_summary(sentences, sentence_scores, threshold)


if __name__ == "__main__":
    files = get_process_files()
    for filename in files:
        with open(filename) as f:
            text = "".join(s.strip() for s in f.readlines())
        summary = run_extractive_algorithm(text)
        print(format_summary(filename, summary))
