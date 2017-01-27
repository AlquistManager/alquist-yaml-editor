from yaml_parser.yaml_parser import YamlParser
from loaded_states import state_dict, intent_transitions
import collections
import io
from os import listdir
from os.path import isfile

#YamlParser()

statePositions = {}
unreachableNodes = []
files = []
posCount = 0

botName = None
states = None

id = 1
nodes = collections.OrderedDict()
edges = []

# recursive method for graph construction
def findNextState(current_state, next_state):
    if current_state is not None and next_state in nodes.keys():
        edges.append((nodes[current_state]["id"], nodes[next_state]["id"]))
        return
    global id
    id += 1

    nodes[next_state] = {"id": id}

    if current_state is not None:
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
                findNextState(current_state, state)

# creates a file to be displayed by viz.js
def writeGraphVizJs(nodes, edges):
    file = open("graph_viz.txt", "w")
    file.write("digraph G{\n")

    #displays nodes in clusters according to yaml files
    clusterNum = 0
    for f in files:
        file.write("subgraph cluster_%d {\n" % (clusterNum))
        for n in nodes:
            if statePositions[n][0] == f:
                if n in unreachableNodes:
                    file.write("%s [id = %s, style=filled, color=red];\n" % (n, nodes[n]["id"]))
                elif n is "init":
                    file.write("%s [id = %s, style=filled, color=yellow];\n" % (n, nodes[n]["id"]))
                else:
                    file.write("%s [id = %s, style=filled, color=white];\n" % (n, nodes[n]["id"]))
        file.write("label=\"%s\";\n" % (f))
        file.write("style=filled;")
        file.write("color=lightgray;")
        file.write("}\n\n")
        clusterNum += 1


    '''
    for n in nodes:
        file.write("%s [id = %s]\n" % (n, nodes[n]["id"]));
    file.write("\n");
    '''

    #list of edges
    for e in edges:
        file.write("%s -> %s;\n" % (findNodeNameById(e[0]), findNodeNameById(e[1])))

    file.write("}")

    file.truncate()
    file.close()

# searches for a node by its ID
def findNodeNameById(id):
    for n in nodes:
        if nodes[n]["id"] == id:
            return n

# finds position of states in yaml files and saves them to statePositions
def findStatePositions():
    yaml_folder = "bots/" + botName + "/flows/"
    global statePositions
    global posCount
    global files

    for fileName in listdir(yaml_folder):
        if fileName not in files:
            files.append(fileName)
        with io.open(yaml_folder + fileName, "r", encoding="utf-8") as file:
            line = file.readline()
            lineNum = 1
            while "states" not in line:
                line = file.readline()
                lineNum += 1

            while line:
                line = file.readline()
                if not line:
                    break
                line = line.strip()
                if not line:
                    line += "\n"
                lineNum += 1
                stateRead = line.split(":")[0].strip()
                stateStart = lineNum
                while line not in ['\n', '\r\n'] and line:
                    line = file.readline().strip()
                    lineNum += 1
                    if not line:
                        line += "\n"
                stateEnd = lineNum
                if stateStart != stateEnd:
                    statePositions[stateRead] = [fileName, stateStart, stateEnd]
                    posCount += 1

# creates a file with positions of states in yaml files
def writeStatePositions(statePositions):
    with io.open("state_positions.txt", "w", encoding="utf-8") as file:
        file.write(botName + "\n")
        for state in statePositions:
            file.write("%s %s %d %d\n" % (state, statePositions[state][0], statePositions[state][1], statePositions[state][2]))
        file.close()

# finds unreachable nodes and saves them to unreachableNodes
def findUnreachableNodes():
    global unreachableNodes
    for state in statePositions:
        if state not in nodes:
            unreachableNodes.append(state)

# create a graph for chosen bot
def createGraph(bot):
    YamlParser(bot)

    statePositions.clear()
    unreachableNodes.clear()
    files.clear()

    global posCount
    posCount = 0

    global id
    id = 1
    nodes.clear()
    edges.clear()

    global botName
    botName = bot

    global states
    states = state_dict[botName]["states"].keys()

    print("Bots available: %s" % state_dict.keys())
    print("Creating graph for bot: %s" % botName)

    findNextState(None, "init")
    findStatePositions()
    findUnreachableNodes()

    # adds unreachable nodes to the graph
    for pos in statePositions:
        if pos not in nodes.keys():
            findNextState(None, pos)

    writeGraphVizJs(nodes, edges)
    writeStatePositions(statePositions)

    print("Graph nodes: %d" % len(nodes))
    print("Graph edges: %d" % len(edges))


#createGraph("test_editor")

# returns graph_viz.txt file
def getGraphFile():
    with io.open("graph_viz.txt", "r", encoding="utf-8") as file:
        data = file.read()
        file.close()
        return data

# returns state_positions.txt file
def getStatePositionsFile():
    with io.open("state_positions.txt", "r", encoding="utf-8") as file:
        data = file.read()
        file.close()
        return data

# returns requested file
def getYamlFile(filepath):
    with io.open(filepath, "r", encoding="utf-8") as file:
        if "bots/" not in filepath:
            return "Invalid Path"
        data = file.read()
        file.close()
        return data

#returns names of bot projects
def getBotNames():
    botnames = ""
    for f in listdir("bots/"):
        if not isfile("bots/" + f):
            botnames += f + ";"
    return botnames

