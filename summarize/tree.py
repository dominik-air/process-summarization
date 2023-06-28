import xml.etree.ElementTree as ET
from collections import defaultdict
from cluster import vectorizer, get_clusters
from onesentence import summarize_sentences

class BPMNGraph:
    def __init__(self):
        self.graph = defaultdict(list)
        self.nodes = {}

    def add_edge(self, source, target):
        self.graph[source].append(target)

    def add_node(self, id, name):
        self.nodes[id] = name

    def get_graph(self):
        return self.graph

    def get_nodes(self):
        return self.nodes
    
    def dfs(self, node=None, visited=None, path=None):
        if node is None:
            node = [n for n in self.graph.keys() if "StartEvent" in n][0]
        if visited is None:
            visited = set()
        if path is None:
            path = []

        visited.add(node)
        path.append(node)

        subpaths = []

        for neighbor in self.graph[node]:
            if neighbor not in visited:
                if len(self.graph[node]) > 1:
                    new_path = [node]
                else:
                    new_path = list(path)

                incoming_edges = sum(neighbor in self.graph[node2] for node2 in self.graph)
                if incoming_edges > 1 and len(new_path) > 2:
                    subpaths.append(new_path[1:])
                else:
                    subpaths.extend(self.dfs(neighbor, set(visited), new_path))

        return subpaths

def parse_bpmn(file):
    tree = ET.parse(file)
    root = tree.getroot()

    bpmn_graph = BPMNGraph()

    for process in root.findall('.//{*}process'):
        for element_type in ['task', 'startEvent', 'endEvent', 'exclusiveGateway', 'parallelGateway']:
            for element in process.findall(f'.//{{*}}{element_type}'):
                node_id = element.attrib['id']
                node_name = element.attrib.get('name', '')
                bpmn_graph.add_node(node_id, node_name)

        for flow in process.findall('.//{*}sequenceFlow'):
            source = flow.attrib['sourceRef']
            target = flow.attrib['targetRef']
            bpmn_graph.add_edge(source, target)

    return bpmn_graph

if __name__ == "__main__":
    
    bpmn_graph = parse_bpmn('diagram.bpmn')

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
    
    print("\nClusters\n")

    labels = vectorizer(raw_sentences_groups[0])
    print(labels)
    clusters = get_clusters(labels)
    
        
    print("\nSenteces groups\n")
    sentences_groups = []
    for cluster in clusters:
        sentences = [raw_sentences_groups[0][i] for i in cluster]
        print(sentences)
        sentences_groups.append(sentences)

    print("\nSummarized\n")

    for sentences in sentences_groups:
        print(summarize_sentences(sentences).capitalize())
