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


#delete nodes and edges in javascript file
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


# writes nodes and edges of graph to a javascript file for vis.js
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
                file.write("{id: %d, label: \'%s\'},\n" % (nodes[n]["id"], n))
                #file.write("{id: %d, label: \'%s\', level: %d, y: %d},\n" % (nodes[n]["id"], n, nodes[n]["level"], nodes[n]["level"]*100))
                #file.write("{id: %d, label: \'%s\', level: %d},\n" % (n[1]["id"], n[0], n[1]["level"]))
        elif "var edges" in line:
            file.write(line)
            for e in edges:
                file.write("{from: %d, to: %d, arrows: \'to\'},\n" % (e[0], e[1]))  # {from: 1, to: 3},
        else:
            file.write(line)
    file.truncate()
    file.close()

#creates JSON file for D3
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

#creates a file to be displayed by viz.js
def writeGraphVizJs(nodes, edges):
    file = open("graph_viz.txt", "w")
    file.write("digraph {\n")

    for e in edges:
        file.write("%s -> %s;\n" % (findNodeNameById(e[0]), findNodeNameById(e[1])))

    file.write("}")

    file.truncate()
    file.close()

#searches for a node by its ID
def findNodeNameById(id):
    for n in nodes:
        if nodes[n]["id"] == id:
            return n



findNextState(current_state, next_state)
clearGraph()
writeNodesAndEdges(nodes, edges)
writeNodesAndEdgesJSON(nodes, edges)
writeGraphVizJs(nodes, edges)

print(len(nodes))
print(len(edges))
#print(state_dict[botName]["states"]["select_type_test_2"]["transitions"])
# print(nodes)
# print(edges)