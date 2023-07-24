import copy
import os
import sys
import numpy as np
import re
import code
import tempfile
import networkx as nx
import random                   ## Import some libraries 

## Here, we implement the DMUX scheme to the best of our ability based on the description in the TCAD paper
benchmark=sys.argv[1]               ## Assumes that the script is executed with command-line arguments, and the first argument is the benchmark file.
key_size=int(sys.argv[2])           ## This assumes that the second argument represents the size of the key.
location=sys.argv[3]                ## Third argument represents the desired location for creating a directory to store output files.
print("Benchmark is "+benchmark)    ## The benchmark name is printed to the console by concatenating the string "Benchmark is " with the value of benchmark.
print("Key-size is "+str(key_size)) ## key size is printed to the console by concatenating the string "Key-size is " with the converted string representation of key_size.
os.mkdir("../data")                 ## A new directory named "data" is created using os.mkdir("../data"). This directory will be used to store output files related to the benchmark.

def GenerateKey(K):             ## Generated Random key of input length K
    nums= np.ones(K)            ## Initialize the K as a set of Ones for while length
    nums[0:(K//2)] =0           ## Make the half of the length as ZERO
    np.random.shuffle(nums)     ## Randomly shuffule them so that the key will be random with equall set of input '0' and '1'
    return nums


## The parse function reads the contents of the netlist file specified by path, extracts the file name, 
## removes the file extension, and returns the result of calling the verilog2gates function with the file 
## data and dump flag. The purpose of this function is to parse the netlist file and convert it into a circuit
## graph representation using the verilog2gates function.

def parse(path, dump=False):                       
    top = path.split('/')[-1].replace('.bench','')  ##  This extracts the file name from the path. The file extension '.bench' is removed from the file name by replacing it with an empty string.
    with open(path, 'r') as f:                      ##  The with statement is used to open the file specified by path in read mode. The file object is assigned to the variable f.
        data = f.read()                             ##  The contents of the file are read using the read() method and stored in the variable data.
    return verilog2gates(data, dump)                ##  The verilog2gates function (As line '49') is called with the data and dump arguments, and the result is returned.

## The ExtractSingleMultiOutputNodes function iterates over the nodes in the circuit graph and separates them 
## into two lists based on their out-degree and 'output' attribute. Nodes with a single output are stored in 
## F_single, and nodes with multiple outputs are stored in F_multi. The function then returns both lists.

###   c = parse('./Benchmarks/'+benchmark+'.bench', True) Just for understanding
def ExtractSingleMultiOutputNodes(G):               
    F_multi=[]                                                ## Initialize F_multi
    F_single=[]                                               ## Initialize F_single
    for n in G.nodes():                                       ## A loop iterates over all nodes in the graph G.
        out_degree=c.out_degree(n)                            ## The out-degree of the current node 'n' for the parsed netlist file of bench
        check=c.nodes[n]['output']                            ## checks if the node is marked as an output.
        if out_degree == 1:                                   ## Depending on the out-degree of the node n, it is checked if it is not an 'input' gate and if it does not have the 'output' attribute set to True. If these conditions are met, the node is appended to either the F_single or F_multi list accordingly.
            if c.nodes[n]['gate'] != "input" and not check:   
                F_single.append(n)
        elif out_degree>1:
            if c.nodes[n]['gate'] != "input" and not check:
                F_multi.append(n)
        else:                                                 ##  If the out-degree is 0 and the 'output' attribute is not set to True, a message is printed to indicate that the node has 0 outputs but is not marked as an output.
            if not check:
                print("Node "+n+" has 0 output and it is not an output")
    return F_multi, F_single                                  ## The function returns the F_multi and F_single lists.


def verilog2gates(verilog, dump):
    Dict_gates={                                    # A dictionary named Dict_gates is defined, which maps gate names to feature vectors. 
    'xor':[0,1,0,0,0,0,0,0],
    'XOR':[0,1,0,0,0,0,0,0],
    'OR':[0,0,1,0,0,0,0,0],
    'or':[0,0,1,0,0,0,0,0],
    'XNOR':[0,0,0,1,0,0,0,0],
    'xnor':[0,0,0,1,0,0,0,0],
    'and':[0,0,0,0,1,0,0,0],
    'AND':[0,0,0,0,1,0,0,0],
    'nand':[0,0,0,0,0,1,0,0],
    'buf':[0,0,0,0,0,0,0,1],
    'BUF':[0,0,0,0,0,0,0,1],
    'NAND':[0,0,0,0,0,1,0,0],
    'not':[0,0,0,0,0,0,1,0],
    'NOT':[0,0,0,0,0,0,1,0],
    'nor':[1,0,0,0,0,0,0,0],
    'NOR':[1,0,0,0,0,0,0,0],
        }
    G = nx.DiGraph()                                ## A directed graph object G is created using nx.DiGraph(). This graph will represent the circuit structure.
    ML_count=0                                      ## initialized to keep track of the number of gates processed.
    regex= "\s*(\S+)\s*=\s*(BUF|NOT)\((\S+)\)\s*"   ## defines the regular expression pattern to match lines in the Verilog input file that correspond to BUF and NOT gates.
    for output, function, net_str in re.findall(regex,verilog,flags=re.I |re.DOTALL): #  function extracts the output, function, and net_str from the Verilog file using the defined regex pattern.
        input=net_str.replace(" ","")               ## remove spacing from veriable net_str

        G.add_edge(input,output)                    ## This line adds an edge to the graph G between the input node and the output node. This represents the connection between the input and output in the circuit.
        G.nodes[output]['gate'] = function          ## This line assigns the function to the 'gate' attribute of the output node in the graph. It indicates the type of gate associated with the output node.
        G.nodes[output]['count'] = ML_count         ## This line assigns the ML_count value to the 'count' attribute of the output node in the graph. It keeps track of the number of gates processed and can be used to uniquely identify the gate.
        if dump:                                    ## If dump is true, the code enters the if block. 
            feat=Dict_gates[function]               ## retrieves the feature vector associated with the function (gate type) from the Dict_gates dictionary.
            for item in feat:                       ## 
                f_feat.write(str(item)+" ")         ## writes each item of the feature vector, converted to a string, followed by a space, to the f_feat file.
            f_feat.write("\n")                      ## writes a newline character to the f_feat file after writing all the feature vector items.
            f_cell.write(str(ML_count)+" assign for output "+output+"\n")   ##  writes the count value (ML_count) converted to a string, followed by the string "assign for output", the output node, and a newline character to the f_cell file. This line indicates the assignment of the count to the output node.
            f_count.write(str(ML_count)+"\n")       ## writes the count value (ML_count) converted to a string, followed by a newline character to the f_count file. This line records the count value in the f_count file.
        ML_count+=1                                 ## increments the ML_count variable by 1, preparing it for the next gate.
    regex= "(\S+)\s*=\s*(OR|XOR|AND|NAND|XNOR|NOR)\((.+?)\)\s*"     ## defines a regular expression pattern used to match lines in the Verilog input file that correspond to OR, XOR, AND, NAND, XNOR, and NOR gates.
    for output, function, net_str in re.findall(regex,verilog,flags=re.I | re.DOTALL):  ## 
        nets = net_str.replace(" ","").replace("\n","").replace("\t","").split(",")     ## 
        inputs = nets
        G.add_edges_from((net,output) for net in inputs)
        G.nodes[output]['gate'] = function
        G.nodes[output]['count'] = ML_count
        if dump:
            feat=Dict_gates[function]
            for item in feat:
                f_feat.write(str(item)+" ")
            f_feat.write("\n")
            f_cell.write(str(ML_count)+" assign for output "+output+"\n")
            f_count.write(str(ML_count)+"\n")
        ML_count+=1
    for n in G.nodes():
        if 'gate' not in G.nodes[n]:
            G.nodes[n]['gate'] = 'input'
    for n in G.nodes:
        G.nodes[n]['output'] = False
    out_regex = "OUTPUT\((.+?)\)\n"
    for net_str in re.findall(out_regex,verilog,flags= re.I | re.DOTALL):
        nets = net_str.replace(" ","").replace("\n","").replace("\t","").split(",")
        for net in nets:
            if net not in G:
                print("Output "+net+" is Float")
            else:
                G.nodes[net]['output'] = True
    if dump:
        for u,v in G.edges:
            if 'count' in G.nodes[u].keys() and 'count' in G.nodes[v].keys():
                f_link_train.write(str(G.nodes[u]['count'])+" "+str(G.nodes[v]['count'])+"\n")
    return G



def FindPairs(S_sel, F_single, F_multi, I_max, O_max, G, selected_g):

    F1=[]
    F2=[]
    if S_sel == "s1" or S_sel =="s2":
        F1=F_multi
        F2=F_multi
    elif S_sel == "s3":
        F1=F_multi
        F2=F_single
    else:
        F1=F_multi+F_single
        F2=F_multi+F_single
    done = False
    i=0
    f1=""
    f2=""
    g1=""
    g2=""
    while i < I_max:
        f1=random.choice(F1)
        f2 = f1
        while f2 == f1:
            f2=random.choice(F2)

        j=0
        while j< O_max:
            g1=random.choice(list(G.successors(f1)))
            g2=random.choice(list(G.successors(f2)))
            R1= nx.has_path(G,g1,f2)
            R2= nx.has_path(G,g2,f1)
            if (g1 != g2) and not R1 and not R2:
                if g1 not in selected_g and g2 not in selected_g:
                    done = True
                    break
            j=j+1
        if done:
            break
        i=i+1
    if done:
        if S_sel == "s1" or S_sel =="s4":
            G.add_edge(f2,g1)
            G.add_edge(f1,g2)
        else:
            G.add_edge(f2,g1)
    return f1, f2, g1, g2, done, G



if __name__=='__main__':
    if not os.path.exists(location):
        os.mkdir(location)
        print("Directory '% s' created" % location)
    f_feat = open(location+"/feat.txt", "w")
    f_cell = open(location+"/cell.txt", "w")
    f_count = open(location+"/count.txt", "w")
    f_link_test = open(location+"/links_test.txt", "w")
    f_link_train = open(location+"/links_train_temp.txt", "w")
    f_link_train_f = open(location+"/links_train.txt", "w")
    f_link_test_neg = open(location+"/link_test_n.txt", "w")
    c = parse('./Benchmarks/'+benchmark+'.bench', True)
    new_c = parse('./Benchmarks/'+benchmark+'.bench')
    F_multi, F_single = ExtractSingleMultiOutputNodes(c)
    #Generate the key
    K_list= GenerateKey(key_size)
    counter=key_size-1
    myDict = {}
    #choices for locking. s4 is avilable always. So it is only used when needed
    L_s= np.array(["s1", "s2", "s3"])
    selected_f1_gates=[]
    selected_f2_gates=[]
    selected_g2_gates=[]
    selected_g1_gates=[]
    selected_g=[]
    break_out=0
    while counter>=0:
        print("key search counter is "+str(counter))

        print("F single size is "+str(len(F_single)))
        print("F multi size is "+str(len(F_multi)))
        np.random.shuffle(L_s)
        fallback=True
        S_sel=""
        for s in L_s:
            if s =="s1" and counter<2:
                print("Choice is s1 but counter is less than 2")
                continue
            elif s=="s3" and len(F_multi)>1 and len(F_single)>1:
                S_sel=s
                fallback=False
                break
            elif len(F_multi)<2:

                print("Choice is "+s+" Length of multi is less than 2")
                continue
            S_sel=s
            fallback=False
            break
        if fallback:
            S_sel="s4"
        print("Chosen is "+S_sel)
        to_be_new_c = nx.DiGraph()
        done = False
        f1, f2, g1, g2, done, to_be_new_c = FindPairs(S_sel, F_single, F_multi, 10, 10, new_c, selected_g)
        if not done:
            break_out+=1
            if (break_out>=10):
                print("Tried 10 times")
                break_out=0;
                S_sel="s4"
                while not done:
                    print("Calling again with s4")
                    f1, f2, g1, g2, done, to_be_new_c = FindPairs("s4", F_single, F_multi, 10, 10, new_c, selected_g)
            else:
                continue
        if len(list(nx.simple_cycles(to_be_new_c))) !=0:
            print("There is a cycle")
            continue
        new_c = copy.deepcopy(to_be_new_c)
        selected_f1_gates.append(f1)
        selected_f2_gates.append(f2)
        if f1 in F_multi:
            F_multi.remove(f1)
        elif f1 in F_single:
            F_single.remove(f1)
        if f2 in F_multi:
            F_multi.remove(f2)
        elif f2 in F_single:
            F_single.remove(f2)
        if S_sel=="s1":
            myDict[g1] = [f1,f2,counter]
            myDict[g2] = [f2,f1,counter-1]
            counter=counter-2
            selected_g1_gates.append(g1)
            selected_g2_gates.append(g2)
            selected_g.append(g1)
            selected_g.append(g2)
            f_link_test_neg.write(str(c.nodes[f2]['count'])+" "+str(c.nodes[g1]['count'])+"\n")
            f_link_test_neg.write(str(c.nodes[f1]['count'])+" "+str(c.nodes[g2]['count'])+"\n")
            f_link_test.write(str(c.nodes[f1]['count'])+" "+str(c.nodes[g1]['count'])+"\n")
            f_link_test.write(str(c.nodes[f2]['count'])+" "+str(c.nodes[g2]['count'])+"\n")
        else:
            if S_sel=="s4":
                selected_g1_gates.append(g1)
                selected_g2_gates.append(g2)
                selected_g.append(g1)
                selected_g.append(g2)
                myDict[g1] = [f1,f2,counter]

                myDict[g2] = [f2,f1,counter]

                f_link_test_neg.write(str(c.nodes[f2]['count'])+" "+str(c.nodes[g1]['count'])+"\n")
                f_link_test_neg.write(str(c.nodes[f1]['count'])+" "+str(c.nodes[g2]['count'])+"\n")
                f_link_test.write(str(c.nodes[f1]['count'])+" "+str(c.nodes[g1]['count'])+"\n")
                f_link_test.write(str(c.nodes[f2]['count'])+" "+str(c.nodes[g2]['count'])+"\n")
            else:

                f_link_test_neg.write(str(c.nodes[f2]['count'])+" "+str(c.nodes[g1]['count'])+"\n")
                f_link_test.write(str(c.nodes[f1]['count'])+" "+str(c.nodes[g1]['count'])+"\n")
                selected_g1_gates.append(g1)
                selected_g.append(g1)
                myDict[g1] = [f1,f2,counter]
            counter=counter-1
    if len(list(nx.simple_cycles(new_c))) !=0:
        sys.exit("There is a loop in the circuit!")
    locked_file = open(location+"/"+benchmark+"_K"+str(key_size)+".bench","w")
    i=0
    locked_file.write("#key=")
    while i<key_size:
        locked_file.write(str(int(K_list[i])))
        i=i+1
    locked_file.write("\n")
    i=0
    while i<key_size:
        locked_file.write("INPUT(keyinput"+str(i)+")\n")
        i=i+1
    file1 = open("./Benchmarks/"+benchmark+".bench", 'r')
    Lines = file1.readlines()
    count = 0
    detected=0
    for line in Lines:
        count += 1
        line=line.strip()
        if any(ext+" =" in line for ext in selected_g):
            detected=detected+1
            regex= "(\S+)\s*=\s*(NOT|BUF|OR|XOR|AND|NAND|XNOR|NOR)\((.+?)\)\s*"
            for output, function, net_str in re.findall(regex,line,flags=re.I |re.DOTALL):
                if output in myDict.keys():
                    my_f1=myDict[output][0]
                    my_f2=myDict[output][1]
                    my_key=myDict[output][2]
                    line=line.replace(my_f1+",", output+"_from_mux,")
                    line=line.replace(my_f1+")", output+"_from_mux)")
                    locked_file.write(line+"\n")
                    if K_list[my_key] == 0:
                        locked_file.write(output+"_from_mux = MUX(keyinput"+str(my_key)+", "+my_f1+", "+my_f2+")\n")
                    else:

                        locked_file.write(output+"_from_mux = MUX(keyinput"+str(my_key)+", "+my_f2+", "+my_f1+")\n")
                else:
                    locked_file.write(line+"\n")
        else:
            locked_file.write(line+"\n")
    locked_file.close()
    f_feat.close()
    f_cell.close()
    f_count.close()
    f_link_test.close()
    f_link_test_neg.close()
    f_link_train.close()
    file1.close()

    with open(location+"/links_test.txt") as f_a, open(location+"/links_train_temp.txt") as f_b:
        a_lines = set(f_a.read().splitlines())
        b_lines = set(f_b.read().splitlines())
        for line in b_lines:
            if line not in a_lines:
                f_link_train_f.write(line+"\n")
    f_link_train_f.close()
    os.remove(location+"/links_train_temp.txt")
    
    ## Original repository:    https://github.com/lilasrahis/MuxLink.git 