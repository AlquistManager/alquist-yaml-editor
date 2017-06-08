import collections
import os
import traceback
from os import listdir
from os.path import isfile

import io
from loaded_states import state_dict, intent_transitions
from yaml_parser.yaml_parser import YamlParser

statePositions = {}
unreachableNodes = []
transition_targets = []
files = []
posCount = 0

botName = None
botFolderName = None
states = None

id = 1
nodes = collections.OrderedDict()
edges = []


# recursive method for graph construction
def findNextState(current_state, next_state):
    # add new edge from current state to next if next state was already visited
    if current_state is not None and next_state in nodes.keys():
        edges.append((nodes[current_state]["id"], nodes[next_state]["id"]))
        return
    global id
    id += 1

    # create a new node and edge leading to it for next_state
    nodes[next_state] = {"id": id}
    if current_state is not None:
        edges.append((nodes[current_state]["id"], nodes[next_state]["id"]))

    current_state = next_state

    if 'transitions' in state_dict[botName]['states'][current_state]:
        transitions = state_dict[botName]["states"][current_state]["transitions"]
    else:
        transitions = None

    if 'properties' in state_dict[botName]['states'][current_state]:
        properties = state_dict[botName]["states"][current_state]["properties"]
    else:
        properties = None

    # get next state for buttons from properties dictionary
    if properties is not None:
        if "buttons" in properties.keys():
            for button in properties["buttons"]:
                if "next_state" in button.keys():
                    next_state = button["next_state"]
                    if next_state != "":
                        findNextState(current_state, next_state)

    # get next state from transitions dictionary
    if transitions is not None:
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

    # displays nodes in clusters according to yaml files
    clusterNum = 0
    for f in files:
        file.write("subgraph cluster_%d {\n" % (clusterNum))
        for n in nodes:
            if statePositions[n][0] == f:
                # display nodes in different colors (unreachable, intent transition targets, initial state...)
                if n in unreachableNodes and n not in transition_targets:
                    file.write("%s [id = %s, style=filled, color=red];\n" % (n, nodes[n]["id"]))
                elif n in transition_targets:
                    file.write("%s [id = %s, style=filled, color=lawngreen];\n" % (n, nodes[n]["id"]))
                elif n is "init":
                    file.write("%s [id = %s, style=filled, color=yellow];\n" % (n, nodes[n]["id"]))
                else:
                    file.write("%s [id = %s, style=filled, color=white];\n" % (n, nodes[n]["id"]))
        file.write("label=\"%s\";\n" % (f))
        file.write("style=filled;")
        file.write("color=lightgray;")
        file.write("}\n\n")
        clusterNum += 1

    # list of edges
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


# finds positions of states in yaml files and saves them to statePositions
# detects states according to indentation in files
def findStatePositions():
    yaml_folder = "bots/" + botFolderName + "/flows/"
    global statePositions
    global posCount
    global files

    # go through all flows files
    for fileName in listdir(yaml_folder):
        # skip empty files
        if os.stat(os.path.join(yaml_folder, fileName)).st_size == 0:
            continue
        if fileName not in files:
            files.append(fileName)
        with io.open(yaml_folder + fileName, "r", encoding="utf-8") as file:
            line = file.readline()
            lineNum = 1
            while "states" not in line:
                line = file.readline()
                lineNum += 1

            space_count = 0
            line = file.readline()
            lineNum += 1
            last_state = None
            while line:
                if space_count == 0:
                    # get number of spaces used in indentation and save position of first state
                    for c in line:
                        if c == ' ':
                            space_count += 1
                        else:
                            state_read = line.split(":")[0].strip()
                            if state_read == "":
                                break
                            last_state = state_read
                            state_start = lineNum
                            state_end = 0
                            statePositions[state_read] = [fileName, state_start, state_end]
                            posCount += 1
                            break
                else:
                    # lines with same indentation as in space_count contain names of states
                    space_curr = 0
                    for c in line:
                        if c == ' ':
                            space_curr += 1
                        else:
                            if space_curr == space_count:
                                state_read = line.split(":")[0].strip()
                                if state_read == "":
                                    break
                                state_start = lineNum
                                state_end = 0
                                statePositions[state_read] = [fileName, state_start, state_end]
                                posCount += 1
                                # set end of previous state to the previous line
                                if last_state is not None:
                                    statePositions[last_state][2] = lineNum - 1
                                last_state = state_read
                            break
                lineNum += 1
                line = file.readline()
            # set end of last state after loop finish
            if last_state is not None:
                statePositions[last_state][2] = lineNum - 1


# creates a file with positions of states in yaml files
def writeStatePositions(statePositions):
    with io.open("state_positions.txt", "w", encoding="utf-8") as file:
        file.write(botName + "\n")
        for state in statePositions:
            file.write(
                "%s %s %d %d\n" % (state, statePositions[state][0], statePositions[state][1], statePositions[state][2]))
        file.close()


# finds unreachable nodes and saves them to unreachableNodes array
def findUnreachableNodes():
    global unreachableNodes
    for state in statePositions:
        if state not in nodes:
            unreachableNodes.append(state)


# create a graph for chosen bot
def createGraph(bot):
    statePositions.clear()
    unreachableNodes.clear()
    files.clear()

    global posCount
    posCount = 0

    global id
    id = 1
    nodes.clear()
    edges.clear()

    # try to parse yaml files into state_dict ant intent_transitions
    try:
        YamlParser(bot)
    except:
        writeGraphVizJs(nodes, edges)
        if len(nodes) > 0:
            writeStatePositions(statePositions)
        flow_files = listdir("bots/" + bot + "/flows")
        if len(flow_files) == 0:
            print("No yaml files.")
            return "No yaml files."
        else:
            print("Error parsing yaml file.")
            stack_trace = traceback.format_exc()
            print(str(stack_trace))
            return str(stack_trace)

    global botName
    botName = bot.lower()

    global botFolderName
    botFolderName = bot

    global states
    states = state_dict[botName]["states"].keys()

    print("Bots available: %s" % state_dict.keys())
    print("Creating graph for bot: %s" % botName)

    try:
        findNextState(None, "init")
    except:
        if len(nodes) > 0:
            writeStatePositions(statePositions)
        flow_files = listdir("bots/" + bot + "/flows")
        if len(flow_files) == 0:
            print("No yaml files.")
            return "No yaml files."
        else:
            print("Error parsing yaml file.")
            stack_trace = traceback.format_exc()
            print(str(stack_trace))
            return str(stack_trace)

    findIntentTransitions(bot)
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

    return "ok"


# find intent transitions targets for chosen bot
def findIntentTransitions(botname):
    botname = botname.lower()
    transition_targets.clear()
    for transition in intent_transitions[botname]:
        transition_targets.append(intent_transitions[botname][transition])


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
def getYamlFile(request_data):
    request_data = request_data.split(":")
    botName = request_data[0]
    filename = request_data[1]
    folder = request_data[2]
    filepath = os.path.join("bots", botName, folder, filename)

    with io.open(filepath, "r", encoding="utf-8") as file:
        data = file.read()
        file.close()
        return data


# returns names of bot projects
def getBotNames():
    botnames = ""
    for f in listdir("bots/"):
        if not isfile("bots/" + f):
            botnames += f + ";"
    return botnames


# returns yaml file names in project in HTML list to be used by FileTree javascript library
def getYamlNamesHtml(projectname):
    folders = listdir(os.path.join("bots", projectname))
    fileHtml = "<ul><li data-jstree='{\"opened\":true}'>" + projectname + "<ul>"
    for folder in folders:
        if not os.path.isdir(os.path.join("bots", projectname, folder)):
            continue
        if folder == "logs":
            opened = "false"
        else:
            opened = "true"
        fileHtml += "<li data-jstree='{\"opened\":" + opened + "}'>" + folder + "<ul>"
        files = listdir(os.path.join("bots", projectname, folder))
        for f in files:
            if f == "__pycache__":
                continue
            fileHtml += "<li>" + f + "</li>"
        fileHtml += "</ul></li>"
    fileHtml += "</ul></li></ul>"
    return fileHtml


# returns string containing yaml file names of a certain project, file names are separated by ';'
def getYamlNames(projectname):
    files = listdir("bots/" + projectname + "/flows")
    if os.path.isdir(os.path.join("bots", projectname, "states")):
        files = files + listdir("bots/" + projectname + "/states")
    for f in files:
        if f == "__pycache__":
            files.remove(f)
            break
    return ";".join(files)
