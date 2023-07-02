import os
from lxml import etree
from edit.manipulator import XMLManipulator
from summarize.cluster import vectorizer, get_clusters
from summarize.onesentence import summarize_sentences
from summarize.tree import parse_bpmn

def run_bpmn_simplification_algorithm(diagram: str):
        
    bpmn_graph = parse_bpmn(diagram)

    print("Graph:")
    print(bpmn_graph.get_graph())
    print("\nNodes:")
    print(bpmn_graph.get_nodes())


    print("\nSubpaths\n")
    subpaths = bpmn_graph.dfs()
    raw_sentences_groups = []
    for subpath in subpaths:
        senteces = [bpmn_graph.get_nodes()[s] for s in subpath]
        raw_sentences_groups.append(senteces)
        print(senteces)
        print()
    
    first_time = True 
    for raw_sentences_group in raw_sentences_groups:
        print("\nClusters\n")

        labels = vectorizer(raw_sentences_group)
        print(labels)
        clusters = get_clusters(labels)

            
        print("\nSenteces groups\n")
        sentences_groups = []
        for cluster in clusters:
            sentences = [raw_sentences_group[i] for i in cluster]
            print(sentences)
            sentences_groups.append(sentences)

        print("\nSummarized\n")

        for sentences in sentences_groups:
            print(summarize_sentences(sentences).capitalize())

        new_task_name = summarize_sentences(sentences).capitalize()

        if first_time:
            tree = etree.parse(diagram)
            first_time = False
        else:
            tree = etree.parse(f"{diagram}.simplified")

        root = tree.getroot()
        manipulator = XMLManipulator(bpmn_process=root.xpath("bpmn:process", namespaces=root.nsmap)[0],
                                    bpmn_plane=root.xpath("bpmndi:BPMNDiagram/bpmndi:BPMNPlane", namespaces=root.nsmap)[0],
                                    namespaces=root.nsmap)
        vk_nodes = {v:k for k, v in bpmn_graph.get_nodes().items()}
        activities = [vk_nodes[sentence] for sentence in sentences]
        manipulator.substitute(activities, new_task_name)
        tree.write(f"{diagram}.simplified")


if __name__ == "__main__":
    run_bpmn_simplification_algorithm("website/models/complex.bpmn")