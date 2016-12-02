from yaml_parser.yaml_parser import YamlParser
from loaded_states import state_dict, intent_transitions
import sys

YamlParser()

botName = "demo_tel"
wantedNode = "init"


if len(sys.argv) > 2:
    botName = sys.argv[1]
    wantedNode = sys.argv[2]

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

wantedId = nodes[wantedNode]["id"]

previous = []
next = []
for e in edges:
    if e[1] == wantedId:
        previous.append(e[1])
        for n in nodes:
            if nodes[n]["id"] == e[1]:
                previous.append(nodes[n]["id"])
                break
    if e[0] == wantedId:
        next.append(e[0])
        for n in nodes:
            if nodes[n]["id"] == e[0]:
                next.append(nodes[n]["id"])
                break

print(wantedId)
print(previous)
print(next)