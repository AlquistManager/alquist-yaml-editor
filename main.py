from yaml_parser.yaml_parser import YamlParser
from loaded_states import state_dict, intent_transitions

YamlParser()

print(state_dict.keys())

botName = "demo_tel"

states = state_dict[botName]["states"].keys()

next_state = state_dict[botName]["states"]["init"]["transitions"]["next_state"]

id = 1
nodes = {"init": {"id": id, "level": 1}}
current_state = "init"
edges = []

count = 0


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
'''
def writeNodesAndEdges(nodes, edges):
    file = open("graph.js", "r+")

    lines = []
    for line in file:
        lines.append(line)
    file.seek(0)

    for line in lines:
        if "var nodes" in line:
            file.write(line)

            #sorted_nodes = sorted(nodes.items(), key=lambda nodes: nodes[1]["level"])

            #print(sorted_nodes)

            for n in nodes:  # {id: 1, label: 'Node 1'},
                #file.write("{id: %d, label: \'%s\'},\n" % (nodes[n]["id"], n))
                file.write("{id: %d, label: \'%s\', level: %d, y: %d},\n" % (nodes[n]["id"], n, nodes[n]["level"], nodes[n]["level"]*100))
                #file.write("{id: %d, label: \'%s\', level: %d},\n" % (n[1]["id"], n[0], n[1]["level"]))
        elif "var edges" in line:
            file.write(line)
            for e in edges:
                file.write("{from: %d, to: %d, arrows: \'to\'},\n" % (e[0], e[1]))  # {from: 1, to: 3},
        else:
            file.write(line)
    file.truncate()
    file.close()
    '''

def writeNodesAndEdgesJSON(nodes, edges):
    file = open("graph.json", "w")

    file.write("{\n  \"nodes\": [\n")

    i = 0
    for n in nodes:
        i += 1
        file.write("{\"id\": \"%d\", \"name\": \"%s\", \"level\": \"%d\"}" % (nodes[n]["id"], n, nodes[n]["level"]))
        if i == len(nodes):
            file.write("\n")
        else:
            file.write(",\n")

    file.write("  ],\n\"links\": [\n")


    i = 0
    for e in edges:
        i += 1
        file.write("{\"source\": \"%d\", \"target\": \"%d\"}" % (e[0], e[1]))
        if i == len(edges):
            file.write("\n")
        else:
            file.write(",\n")

    file.write("  ]\n}")

    file.truncate()
    file.close()


findNextState(current_state, next_state)
clearGraph()
#writeNodesAndEdges(nodes, edges)
writeNodesAndEdgesJSON(nodes, edges)

print(len(nodes))
print(len(edges))
# print(nodes)
# print(edges)
