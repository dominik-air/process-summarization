from lxml import etree

def replace_tasks(file, task_ids, new_task_id, new_task_name):
    tree = etree.parse(file)
    root = tree.getroot()

    tasks_to_remove = []
    shapes_to_remove = []
    for task_id in task_ids:
        task = root.xpath(f'//bpmn:task[@id="{task_id}"]', namespaces=root.nsmap)
        shape = root.xpath(f'//bpmndi:BPMNShape[@bpmnElement="{task_id}"]', namespaces=root.nsmap)
        if task:
            tasks_to_remove.append(task[0])
        if shape:
            shapes_to_remove.append(shape[0])

    if not tasks_to_remove:
        print("No tasks found with the provided ids")
        return

    new_task = etree.SubElement(root.find('.//bpmn:process', namespaces=root.nsmap), 
                                "{http://www.omg.org/spec/BPMN/20100524/MODEL}task")
    new_task.attrib["id"] = new_task_id
    new_task.attrib["name"] = new_task_name

    first_task = tasks_to_remove[0]
    last_task = tasks_to_remove[-1]

    for seq_flow in root.xpath(f'//bpmn:sequenceFlow[@targetRef="{first_task.attrib["id"]}"]', 
                               namespaces=root.nsmap):
        seq_flow.attrib["targetRef"] = new_task_id
        incoming = etree.SubElement(new_task, 
                                    "{http://www.omg.org/spec/BPMN/20100524/MODEL}incoming")
        incoming.text = seq_flow.attrib["id"]

    for seq_flow in root.xpath(f'//bpmn:sequenceFlow[@sourceRef="{last_task.attrib["id"]}"]', 
                               namespaces=root.nsmap):
        seq_flow.attrib["sourceRef"] = new_task_id
        outgoing = etree.SubElement(new_task, 
                                    "{http://www.omg.org/spec/BPMN/20100524/MODEL}outgoing")
        outgoing.text = seq_flow.attrib["id"]

    new_shape = etree.SubElement(root.find('.//bpmndi:BPMNPlane', namespaces=root.nsmap), 
                                 "{http://www.omg.org/spec/BPMN/20100524/BPMNDI}BPMNShape")
    new_shape.attrib["id"] = new_task_id + "_di"
    new_shape.attrib["bpmnElement"] = new_task_id

    if shapes_to_remove:
        first_shape = shapes_to_remove[0]
        bounds = first_shape.find('.//dc:Bounds', namespaces=root.nsmap)
        if bounds is not None:
            new_bounds = etree.SubElement(new_shape, "{http://www.omg.org/spec/DD/20100524/DC}Bounds")
            new_bounds.attrib.update(bounds.attrib)

    for old_task in tasks_to_remove:
        root.find('.//bpmn:process', namespaces=root.nsmap).remove(old_task)
    for old_shape in shapes_to_remove:
        root.find('.//bpmndi:BPMNPlane', namespaces=root.nsmap).remove(old_shape)

    return etree

if __name__ == "__main__":
    file = "diagram.bpmn"
    task_ids = ["Activity_1jvqjoz", "Activity_07h45eb", "Activity_1708mpc"]
    new_task_id = "Activity69XD"
    new_task_name = "Confirm, generate, prepare the order."

    tree = replace_tasks(file, task_ids, new_task_id, new_task_name)
    tree.write("replaced.bpmn")
