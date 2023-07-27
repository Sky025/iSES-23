# Code for matching the extracted keys from .sld binary file of the SAT Attack with the original key.
# Outputs equivalent if key matches.
# Reads the extracted keys from a csv file containing SAT Attack Logs and stores the output in a txt file

import subprocess
import csv
# csv file name
filename = "./SAT_Test.csv"
# initializing the titles and rows list
fields = []
rows = []
# reading csv file
with open(filename, 'r') as csvfile:
    # creating a csv reader object
    csvreader = csv.reader(csvfile)
    # extracting field names through first row
    fields = next(csvreader)
    # extracting each data row one by one
    for row in csvreader:
        rows.append(row)

benchmarks = ['c432','c499','c880','c1355','c1908','c2670','c3540','c5315','c6288','c7552']
key_size = ['32','64','128']
for i in range(0,1):
    for j in range(0,1):
        command = "/root/CEERI/Modified_SAT/bin/lcmp /root/CEERI/Verilog_Files/Benchmarks/"+rows[i][0]+".bench"
        command+=" /root/CEERI/Verilog_Files/Locked_Files/"+ rows[i][0]+"/"+rows[i][1]+"/"+rows[i][0]+"_K"+rows[i][1]+"_0.bench"+" key="+rows[i][2]
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            filename  = "SAT_"+rows[i][0]+"_log.txt"
            header = rows[i][0]+"_K"+rows[i][1]+"Attack"
            with open(filename, "a") as file:
                file.write(header+"\n")
                file.write(result.stdout)
                print("Output saved to "+filename)
        else:
          print("Command failed with error:", result.stderr)