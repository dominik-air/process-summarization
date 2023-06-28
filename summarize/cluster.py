from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans


def vectorizer(sentences):
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(sentences)
    kmeans = KMeans(n_clusters=2, random_state=0).fit(X)
    return kmeans.labels_


def bert(sentences):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    X = model.encode(sentences)
    kmeans = KMeans(n_clusters=2, random_state=0).fit(X)
    return kmeans.labels_


def get_clusters(labels):
    clusters = []
    current_cluster = []

    for i in range(len(labels) - 1):
        current_cluster.append(i)
        if labels[i] != labels[i + 1]:
            if len(current_cluster) > 1:
                clusters.append(current_cluster)
            current_cluster = []

    current_cluster.append(len(labels) - 1)
    if len(current_cluster) > 1:
        clusters.append(current_cluster)

    return clusters


if __name__ == "__main__":
    sentences1 = [
        "Confirm the order with the customer",
        "Generate an invoice for the order",
        "Prepare the order for shipment",
        "Dispatch the order",
        "Send a confirmation email to the customer with tracking details",
    ]
    sentences2 = [
        "Send an email to customer asking for complete information.",
        "Customer provides the missing information.",
        "Review the updated information.",
    ]
    sentences3 = [
        "Inform the customer that the application has been approved",
        "Prepare the loan agreement.",
        "Sign the loan agreement.",
        "Disburse the loan.",
    ]

    for sentences in [sentences1, sentences2, sentences3]:
        labels = vectorizer(sentences)
        clusters = get_clusters(labels)
        print(labels)
        print(clusters)
