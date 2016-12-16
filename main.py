from yaml_parser.yaml_parser import YamlParser
from loaded_states import state_dict, intent_transitions
import collections
import io
from os import listdir
from os.path import isfile, join

YamlParser()

print(state_dict.keys())

botName = "demo_tel"

states = state_dict[botName]["states"].keys()

next_state = state_dict[botName]["states"]["init"]["transitions"]["next_state"]

id = 1
# nodes = {"init": {"id": id, "level": 1}}
nodes = collections.OrderedDict({"init": {"id": id,
                                          "level": 1,
                                          "responses": state_dict[botName]["states"]["init"]["properties"][
                                              "responses"]}})
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

    global count

    nodes[current_state]["responses"] = []
    if "responses" in properties.keys():
        for res in properties["responses"]:
            nodes[current_state]["responses"].append(res)
        count += 1

    if "text" in properties.keys():
        nodes[current_state]["responses"].append(properties["text"])
        count += 1

    if "buttons" in properties.keys():
        buttons = properties["buttons"]
        for b in buttons:
            nodes[current_state]["responses"].append(b["label"] + " ")
        count += 1

    if "checkboxes" in properties.keys():
        checkboxes = properties["checkboxes"]
        for c in checkboxes:
            nodes[current_state]["responses"].append(c["label"] + " ")
        count += 1

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
            #if state != "":
                findNextState(current_state, state)



# delete nodes and edges in vis.js javascript file
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

            # sorted_nodes = sorted(nodes.items(), key=lambda nodes: nodes[1]["level"])

            # print(sorted_nodes)

            for n in nodes:  # {id: 1, label: 'Node 1'},
                file.write("{id: %d, label: \'%s\'},\n" % (nodes[n]["id"], n))
                # file.write("{id: %d, label: \'%s\', level: %d, y: %d},\n" % (nodes[n]["id"], n, nodes[n]["level"], nodes[n]["level"]*100))
                # file.write("{id: %d, label: \'%s\', level: %d},\n" % (n[1]["id"], n[0], n[1]["level"]))
        elif "var edges" in line:
            file.write(line)
            for e in edges:
                file.write("{from: %d, to: %d, arrows: \'to\'},\n" % (e[0], e[1]))  # {from: 1, to: 3},
        else:
            file.write(line)
    file.truncate()
    file.close()


# creates JSON file for D3
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


# creates a file to be displayed by viz.js
def writeGraphVizJs(nodes, edges):
    file = open("graph_viz.txt", "w")
    file.write("digraph {\n")

    for n in nodes:
        file.write("%s [id = %s]\n" % (n, nodes[n]["id"]));
    file.write("\n");

    for e in edges:
        file.write("%s -> %s;\n" % (findNodeNameById(e[0]), findNodeNameById(e[1])))

    file.write("}")

    file.truncate()
    file.close()

    with io.open("graph_viz_node_texts.txt", "w", encoding="utf-8") as f:
        # file = open("graph_viz_node_texts.txt", "w")
        for n in nodes:
            if "responses" in nodes[n].keys():
                text = ""

                # for s in nodes[n]["responses"]:
                for i in range(len(nodes[n]["responses"])):
                    text += nodes[n]["responses"][i];
                    # if i != len(nodes[n]["responses"]) - 1:
                    # text += "\n"
                f.write("%s: \"%s\"\n" % (nodes[n]["id"], text))
        f.close()


# searches for a node by its ID
def findNodeNameById(id):
    for n in nodes:
        if nodes[n]["id"] == id:
            return n


statePositions = {}
posCount = 0


def findStatePositions():
    yaml_folder = "bots/" + botName + "/flows/"
    global statePositions
    global posCount

    for fileName in listdir(yaml_folder):
        with io.open(yaml_folder + fileName, "r", encoding="utf-8") as file:
            #print(fileName)
            file.readline()
            line = file.readline()
            lineNum = 1

            while line:
                line = file.readline()
                if not line:
                    break
                lineNum += 1
                stateRead = line.strip()[0:-1]
                stateStart = lineNum
                while line not in ['\n', '\r\n'] and line:
                    line = file.readline()
                    lineNum += 1
                    #if lineNum > 100:
                    #    break
                    #print(line)
                    #print(lineNum)
                stateEnd = lineNum
                if stateStart != stateEnd:
                    statePositions[stateRead] = [fileName, stateStart, stateEnd]
                    #print(statePositions[stateRead])
                    posCount += 1




findNextState(current_state, next_state)
clearGraph()
writeNodesAndEdges(nodes, edges)
writeNodesAndEdgesJSON(nodes, edges)
#writeGraphVizJs(nodes, edges)

print(len(nodes))
print(len(edges))
# print(state_dict[botName]["states"]["select_type_test_2"]["transitions"])
# print(state_dict[botName]["states"]["init"]["properties"]["responses"])
#print(state_dict[botName])
#print(count)
# print(nodes)
# print(edges)


findStatePositions()

for pos in statePositions:
    if pos not in nodes.keys():
        print(pos + " " + statePositions[pos][0])


for pos in statePositions:
    if pos not in nodes.keys():
        id += 1
        nodes[pos] = {"id": id, "level": 0}
        transitions = state_dict[botName]["states"][pos]["transitions"]
        properties = state_dict[botName]["states"][pos]["properties"]
        if "buttons" in properties.keys():
            for button in properties["buttons"]:
                if "next_state" in button.keys():
                    next_state = button["next_state"]
                    if next_state != "":
                        findNextState(pos, next_state)

        if "next_state" in transitions.keys():
            next_state = transitions["next_state"]
            if next_state != "":
                findNextState(pos, next_state)
        else:
            for state in transitions.values():
                findNextState(pos, state)

print(len(nodes))

def detectNodesWithoutInputs():
    noInputs = []
    inputDetected = False
    for n in nodes:
        inputDetected = False
        for e in edges:
            if e[1] == nodes[n]["id"]:
                inputDetected = True
                break;
        if not inputDetected:
            noInputs.append(n)
    print(noInputs)

detectNodesWithoutInputs()

writeGraphVizJs(nodes, edges)


