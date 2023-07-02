import string
import random
from typing import Iterable, List, Dict
from lxml import etree


def generate_random_string(length: int) -> str:
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choices(characters, k=length))


def calculate_new_task_bounds(bounds: List[Dict[str, str]]) -> Dict[str, str]:
    keys = ['x', 'y', 'width', 'height']
    middle_values = {}

    for key in keys:
        total = sum(int(dic[key]) for dic in bounds)
        avg = total / len(bounds)
        middle_values[key] = str(int(avg))

    return middle_values

class XMLManipulator:

    def __init__(self, bpmn_process, bpmn_plane, namespaces) -> None:
        self.bpmn_process = bpmn_process
        self.bpmn_plane = bpmn_plane
        self.namespaces = namespaces

    def get_incoming_sequence_flow(self, task_id: str) -> str:
        return self.bpmn_process.xpath(f"bpmn:task[@id='{task_id}']/bpmn:incoming", namespaces=self.namespaces)[0].text

    def get_outgoing_sequence_flow(self, task_id: str) -> str:
        return self.bpmn_process.xpath(f"bpmn:task[@id='{task_id}']/bpmn:outgoing", namespaces=self.namespaces)[0].text

    def substitute(self, merged_tasks: Iterable[str], task_name: str) -> None:
        # get the left most and right most tasks' sequence flows
        left_sF = self.get_incoming_sequence_flow(task_id=merged_tasks[0])
        right_sF = self.get_outgoing_sequence_flow(task_id=merged_tasks[-1])
        # remove merged tasks from bpmn:process
        children_to_be_removed = []
        for child in self.bpmn_process.iter():
            if "task" in child.tag and child.attrib["id"] in merged_tasks:
                children_to_be_removed.append(child)
        
        sFs_to_be_removed = []
        for child in children_to_be_removed:
            incoming = self.get_incoming_sequence_flow(task_id=child.attrib["id"])
            if incoming not in [left_sF, right_sF]:
                sFs_to_be_removed.append(incoming)
            outgoing = self.get_outgoing_sequence_flow(task_id=child.attrib["id"])
            if outgoing not in [left_sF, right_sF]:
                sFs_to_be_removed.append(outgoing)
            self.bpmn_process.remove(child)
        # remove hanging sequence flows
        children_to_be_removed = []
        for child in self.bpmn_process.iter():
            if "sequenceFlow" in child.tag and child.attrib["id"] in sFs_to_be_removed:
                children_to_be_removed.append(child)
        for child in children_to_be_removed:
            self.bpmn_process.remove(child)
        # remove merged tasks from bpmndi:BPMNPlane
        children_to_be_removed = []
        harvested_bounds = []
        for child in self.bpmn_plane.iter():
            if "BPMNShape" in child.tag and child.attrib["bpmnElement"] in merged_tasks:
                children_to_be_removed.append(child)
                harvested_bounds.append(child.xpath("dc:Bounds", namespaces=self.namespaces)[0].attrib)
        
        for child in children_to_be_removed:
            self.bpmn_plane.remove(child)

        # remove hanging sFs from bpmndi:BPMNPlane
        children_to_be_removed = []
        for child in self.bpmn_plane.iter():
            if "BPMNEdge" in child.tag and child.attrib["bpmnElement"] in sFs_to_be_removed:
                children_to_be_removed.append(child)
        
        for child in children_to_be_removed:
            self.bpmn_plane.remove(child)
        
        # add new task
        new_task = etree.SubElement(self.bpmn_process, f"{{{self.namespaces['bpmn']}}}task", nsmap=self.namespaces)
        new_task.attrib["id"] = f"Activity_{generate_random_string(length=6)}"
        new_task.attrib["name"] = task_name
        incoming = etree.SubElement(new_task, f"{{{self.namespaces['bpmn']}}}incoming", nsmap=self.namespaces)
        incoming.text = left_sF
        outgoing = etree.SubElement(new_task, f"{{{self.namespaces['bpmn']}}}outgoing", nsmap=self.namespaces)
        outgoing.text = right_sF

        sf_left = self.bpmn_process.xpath(f"bpmn:sequenceFlow[@id='{left_sF}']", namespaces=self.namespaces)[0]
        sf_left.attrib["targetRef"] = new_task.attrib["id"]

        sf_right = self.bpmn_process.xpath(f"bpmn:sequenceFlow[@id='{right_sF}']", namespaces=self.namespaces)[0]
        sf_right.attrib["sourceRef"] = new_task.attrib["id"]
        

        # add bpmndi:BPMNShape for the new task
        bounds = calculate_new_task_bounds(harvested_bounds)
        attribs = {"id": new_task.attrib["id"]+"_di", "bpmnElement": new_task.attrib["id"]}
        BPMNShape = etree.SubElement(self.bpmn_plane,  f"{{{self.namespaces['bpmndi']}}}BPMNShape", attrib=attribs, nsmap=self.namespaces)
        etree.SubElement(BPMNShape, f"{{{self.namespaces['dc']}}}Bounds", attrib=bounds, nsmap=self.namespaces)
        etree.SubElement(BPMNShape, f"{{{self.namespaces['bpmndi']}}}BPMNLabel", nsmap=self.namespaces)

        # update bpmndi:BPMNEdges
        left_edge = self.bpmn_plane.xpath(f"bpmndi:BPMNEdge[@bpmnElement='{left_sF}']", namespaces=self.namespaces)[0]
        left_waypoint =left_edge.xpath("di:waypoint", namespaces=self.namespaces)[-1]
        left_waypoint.attrib["x"] = bounds["x"]

        right_edge = self.bpmn_plane.xpath(f"bpmndi:BPMNEdge[@bpmnElement='{right_sF}']", namespaces=self.namespaces)[0]
        right_waypoint = right_edge.xpath("di:waypoint", namespaces=self.namespaces)[0]
        right_waypoint.attrib["x"] = str(int(bounds["x"]) + int(bounds["width"]))





if __name__ == "__main__":


    tree = etree.parse("simple.bpmn")

    root = tree.getroot()
    manipulator = XMLManipulator(bpmn_process=root.xpath("bpmn:process", namespaces=root.nsmap)[0],
                                bpmn_plane=root.xpath("bpmndi:BPMNDiagram/bpmndi:BPMNPlane", namespaces=root.nsmap)[0],
                                namespaces=root.nsmap)
    manipulator.substitute(["Activity_0m4dehc", "Activity_06j4hty", "Activity_15yx4fq"], "ABCxd")
    tree.write("replace.bpmn")
