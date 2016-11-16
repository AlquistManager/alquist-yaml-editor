from yaml_parser.yaml_parser import YamlParser
from loaded_states import state_dict, intent_transitions

YamlParser()

print(state_dict.keys())

botName = "demo_tel"

states = state_dict[botName]["states"].keys()

print(states)

next_state = state_dict[botName]["states"]["init"]["transitions"]["next_state"]


id = 1
nodes = {"init": {"id":id, "level":1}}
current_state = "init"
edges = []

#recursive method for graph construction
def findNextState(current_state, next_state):
    if next_state in nodes.keys():
        edges.append((nodes[current_state]["id"], nodes[next_state]["id"]))
        return
    global id
    id += 1
    nodes[next_state] = {"id":id, "level":nodes[current_state]["level"] + 1}

    edges.append((nodes[current_state]["id"], nodes[next_state]["id"]))
    current_state = next_state

    transitions = state_dict[botName]["states"][current_state]["transitions"]

    if "next_state" in transitions.keys():
        next_state = transitions["next_state"]
        if next_state != "":
            findNextState(current_state, next_state)
    else:
        for state in transitions.values():
            if state != "":
                findNextState(current_state, state)


# delete nodes and edges in javascript file
def clearGraph():
    writing = True
    file = open("graph.js", "r+")

    lines = []
    for line in file:
        lines.append(line)

    file.seek(0)

    for line in lines:
        if "var nodes" in line:
            writing = False
            file.write(line)
        elif "var edges" in line:
            writing = False
            file.write(line)
        elif writing == False and "]);" in line:
            writing = True

        if writing:
            file.write(line)

    file.truncate()
    file.close()


# writes nodes and edges of graph to javascript file
def writeNodesAndEdges(nodes, edges):
    file = open("graph.js", "r+")

    lines = []
    for line in file:
        lines.append(line)
    file.seek(0)

    for line in lines:
        if "var nodes" in line:
            file.write(line)

            for n in nodes:  # {id: 1, label: 'Node 1'},
                file.write("{id: %d, label: \'%s\', level: %d},\n" % (nodes[n]["id"], n, nodes[n]["level"]))
        elif "var edges" in line:
            file.write(line)
            for e in edges:
                file.write("{from: %d, to: %d, arrows: \'to\'},\n" % (e[0], e[1]))  # {from: 1, to: 3},
        else:
            file.write(line)
    file.truncate()
    file.close()


findNextState(current_state, next_state)
clearGraph()
writeNodesAndEdges(nodes, edges)

print(nodes)
print(edges)