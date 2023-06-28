import re
import collections
import spacy


def create_sentence_from_common_parts(sentences, num_common_words=2):
    text = " ".join(sentences).lower()
    words = re.findall(r"\b\w+\b", text)
    common_parts = collections.Counter(words).most_common(num_common_words)
    common_words = [word for word, count in common_parts]
    return " ".join(common_words)


def get_verbs(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    return [token.lemma_ for token in doc if token.pos_ == "VERB"]


def summarize_sentences(sentences):
    common_parts = create_sentence_from_common_parts(sentences)
    verbs = [get_verbs(sentence)[0] for sentence in sentences]
    return ", ".join(verbs) + " " + common_parts


if __name__ == "__main__":
    sentences1 = [
        "Confirm the order with the customer",
        "Generate an invoice for the order",
    ]

    sentences2 = [
        "Prepare the order for shipment",
        "Dispatch the order",
        "Send a confirmation email to the customer with tracking details",
    ]

    sentences3 = [
        "Prepare the loan agreement.",
        "Sign the loan agreement.",
        "Disburse the loan.",
    ]

    for sentences in (sentences1, sentences2, sentences3):
        summary = summarize_sentences(sentences)
        print(summary.capitalize())
