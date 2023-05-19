# Vladislav Grigorev
# 01.05.2023
import re  # for regular expression
dictionary = {}  # we keep al our data in dictionary
adj_list = {}  # create empty adjacency list
adj_list_directed = {}  # for directed graphs
adj_list_undirected = {}  # for undirected graphs


# input fsa data
def inputData():
    global dictionary
    with open("input.txt", "r") as f:
        for i in range(5):  # fill in fields states, alpha, initial, accepting states, and transitions
            inp = f.readline().strip()
            equal = inp.find("=")
            if inp[:equal] not in ("states", "alpha", "initial", "accepting", "trans"):
                print("E1: Input file is malformed\n")
                exit(0)

            if inp[:equal] == "states" and inp[equal + 1:len(inp)] == "[]":
                print("E1: Input file is malformed\n")
                exit(0)
            if inp[:equal] not in dictionary:
                dictionary[inp[:equal]] = []

            for ss in inp[equal + 2:len(inp) - 1].split(","):
                dictionary[inp[:equal]].append(ss)
            dictionary[inp[:equal]].sort()


# creating adjustment lists for storing our graph
def createAdjLists():
    global adj_list_undirected, adj_list, adj_list_directed
    # create adjacency lists from transitions
    for tran in dictionary["trans"]:
        a, t, b = tran.split(">")
        # add transition to adjacency list for start state a
        if a not in adj_list:
            adj_list[a] = []
        adj_list[a].append([t, b])
    # create directed and undirected adjacency lists from adjacency list
    for j in adj_list:
        # initialize directed and undirected adjacency lists for state j
        if j not in adj_list_directed:
            adj_list_directed[j] = []
        if j not in adj_list_undirected:
            adj_list_undirected[j] = []
        # for each transition from state j
        for i in adj_list[j]:
            # add destination state to directed adjacency list for state j
            adj_list_directed[j].append(i[1])
            if i[1] not in adj_list_undirected:
                adj_list_undirected[i[1]] = []
            # add destination state to undirected adjacency list for state j
            if i[1] == j:
                adj_list_undirected[j].append(i[1])
                continue
            adj_list_undirected[j].append(i[1])
            adj_list_undirected[i[1]].append(j)

    adj_list_undirected = {i: set(adj_list_undirected[i]) for i in adj_list_undirected}


"""=======================================================================
   Checking for errors:
    1. Any state name does not satisfy condition (Latin letters, numbers) - E5
    2. Any alphbet name does not satisfy conditions (Latin letters, numbers, underscore sign) - E5
    4. Any final state name is not present in the states - E1
    5. More than one initial state - E5
    6. No initial state - E4
    7. Initial state is not present in the states - E1
    8. States in transition are not present in states - E1 
    9. Letter in transition is not present in alphabet - E3
    10. FSA has disjoint state(s) - E2
==========================================================================="""


def checkErrors():
    global dictionary, adj_list

    # check for various errors in states
    def check_state_name(state_name):
        pattern = re.compile('[^a-zA-Z0-9]')
        if pattern.search(state_name):
            return True
        else:
            return False

    # check for various errors in alphabet
    def check_alphabet_name(alphabet_name):
        pattern = re.compile('[^a-zA-Z0-9_]')
        if pattern.search(alphabet_name):
            return True
        else:
            return False

    if dictionary["states"][0] == "":
        print("E1: Input file is malformed\n")
        exit(0)
    # check for invalid state names
    for state in dictionary["states"]:
        if check_state_name(state):
            print("E1: Input file is malformed\n")
            exit(0)

    # check for invalid alphabet symbols
    for alpha in dictionary["alpha"]:
        if check_alphabet_name(alpha):
            print("E1: Input file is malformed\n")
            exit(0)

    # check for undefined initial state
    if dictionary["initial"][0] == "":
        print("E2: Initial state is not defined\n")
        exit(0)

    if len(dictionary["initial"]) > 1:
        print("E1: Input file is malformed\n")
        exit(0)

    # check for undefined accepting state
    if dictionary["accepting"][0] == "":
        print(f"E3: Set of accepting states is empty\n")
        exit(0)

    for elem in dictionary["initial"]:
        if elem not in dictionary["states"] and elem != "":
            print(f"E4: A state '{elem}' is not in the set of states\n")
            exit(0)
    for elem in dictionary["accepting"]:
        if elem not in dictionary["states"] and elem != "":
            print(f"E4: A state '{elem}' is not in the set of states\n")
            exit(0)
    for elem in adj_list:
        if elem not in dictionary["states"]:
            print(f"E4: A state '{elem}' is not in the set of states\n")
            exit(0)
    for elem in adj_list:
        for state2 in adj_list[elem]:
            if state2[1] not in dictionary["states"]:
                print(f"E4: A state '{state2[1]}' is not in the set of states\n")
                exit(0)

    for elem in adj_list:
        for tr in adj_list[elem]:
            if tr[0] not in dictionary["alpha"]:
                print(f"E5: A transition '{tr[0]}' is not represented in the alphabet\n")
                exit(0)


"""============== DFS ====================================
Define a depth-first search function for undirected graphs
    We check for the disjoint states.
==========================================================="""


def dfs(now, visited):
    global adj_list_undirected, comp
    visited[now] = comp  # mark current node as visited
    # visit all neighbors that haven't been visited yet
    if now in adj_list_undirected:
        for neighbor in adj_list_undirected[now]:
            if not visited[neighbor]:
                dfs(neighbor, visited)


"""============== DFS 2 ===================================
Define a depth-first search function for undirected graphs
    We check whether some states are not reachable from the initial state.
==========================================================="""


def dfsDirected(now, t, visited):
    global adj_list_directed, comp
    if now == t:
        return True
    visited[now] = True  # mark current node as visited
    # visit all neighbors that haven't been visited yet
    if now in adj_list_directed:
        for neighbor in adj_list_directed[now]:
            if not visited[neighbor]:
                if dfsDirected(neighbor, t, visited):
                    return True
    return False


inputData()
createAdjLists()
checkErrors()

visited = {i: False for i in dictionary["states"]}  # create list to track visited nodes
comp = 1
# start DFS from every unvisited node
for i in dictionary["states"]:
    if not visited[i]:
        dfs(i, visited)
        comp += 1
for i in visited:
    if visited[i] > 1:
        print("E6: Some states are disjoint\n")
        exit(0)

visited = {i: False for i in dictionary["states"]}  # create list to track visited nodes
init = dictionary["initial"][0]
# start DFS from every unvisited node
# for i in dictionary["states"]:
#     if not dfsDirected(init, i, visited):
#         print(f"E1: Input file is malformed\n")
#         exit(0)

for i in adj_list:
    adj_list[i].sort()
    for j in range(len(adj_list[i]) - 1):
        if adj_list[i][j][0] == adj_list[i][j + 1][0]:
            print(f"E7: FSA is nondeterministic\n")
            exit(0)


def initial_settings():
    init_regex = [[''] * len(dictionary["states"]) for i in range(len(dictionary["states"]))]

    for i in range(len(dictionary["states"])):
        state = dictionary["states"][i]

        for j in range(len(dictionary["states"])):
            new_state = dictionary["states"][j]
            regex = ""
            for transition in dictionary["trans"]:
                trans_info = transition.split('>')
                if trans_info[2] == new_state and trans_info[0] == state:
                    regex += trans_info[1] + "|"
            if state == new_state:
                regex += "eps"
            if regex == "":
                regex = "{}"
            if regex[-1] == "|":
                regex = regex[0:len(regex) - 1]
            init_regex[i][j] = regex
    return init_regex


"""============== FSA->regex ====================================
Translates given FSA to regular expression
==========================================================="""


def FSA2RegEx():
    final_indexes = []
    for i in range(len(dictionary["states"])):
        state = dictionary["states"][i]
        if state in dictionary["accepting"]:
            final_indexes.append(i)
    regex = initial_settings()

    for k in range(len(dictionary["states"])):
        new_regex = [[0] * len(dictionary["states"]) for i in range(len(dictionary["states"]))]
        for i in range(len(dictionary["states"])):
            for j in range(len(dictionary["states"])):
                new_regex[i][j] = "("
                new_regex[i][j] += regex[i][k]
                new_regex[i][j] += ")("
                new_regex[i][j] += regex[k][k]
                new_regex[i][j] += ")*("
                new_regex[i][j] += regex[k][j]
                new_regex[i][j] += ")|("
                new_regex[i][j] += regex[i][j]
                new_regex[i][j] += ")"
        regex = new_regex

    result_new_regex = ''

    for i in range(len(final_indexes)):
        result_new_regex += "(" + regex[0][final_indexes[i]] + ")|"

    answer = ""
    if result_new_regex == '':
        answer += "{}"
    else:
        answer += str(result_new_regex[0:-1])
    print("" + answer + "\n")  # write out result


FSA2RegEx()  # printing answer

