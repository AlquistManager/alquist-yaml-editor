from yaml_parser.yaml_parser import YamlParser
from loaded_states import state_dict, intent_transitions
import sys

YamlParser()

botName = "demo_tel"

if len(sys.argv) > 1:
    botName = sys.argv[1]

next_state = state_dict[botName]["states"]["init"]["transitions"]["next_state"]

id = 1
nodes = {"init": {"id": id, "level": 1}}
current_state = "init"
edges = []

# recursive method for graph construction
def findNextState(current_state, next_state):
    if next_state in nodes.keys():
        edges.append((nodes[current_state]["id"], nodes[next_state]["id"]))
        return
    global id
    id += 1
    level = nodes[current_state]["level"] + 1

    nodes[next_state] = {"id": id, "level": level}

    edges.append((nodes[current_state]["id"], nodes[next_state]["id"]))

    current_state = next_state

    transitions = state_dict[botName]["states"][current_state]["transitions"]
    properties = state_dict[botName]["states"][current_state]["properties"]

    if "buttons" in properties.keys():
        for button in properties["buttons"]:
            if "next_state" in button.keys():
                next_state = button["next_state"]
                if next_state != "":
                        findNextState(current_state, next_state)

    if "next_state" in transitions.keys():
        next_state = transitions["next_state"]
        if next_state != "":
            findNextState(current_state, next_state)
    else:
        for state in transitions.values():
            if state != "":
                findNextState(current_state, state)


findNextState(current_state, next_state)
print("states count: %d" % len(nodes))
print("transitions count: %d" % len(edges))
