#Code for performing SAT Attacks on c432,c499,c880,c1355,c1908,c2670,c3540,c5315,c6288,and c7552 of key sizes 32,64,128
#This also stores the output in a file named SAT_<benchmark>_log.txt

import subprocess
benchmarks = ['c432','c499','c880','c1355','c1908','c2670','c3540','c5315','c6288','c7552'] 
key_size = ['32','64','128']

for i in range(0,10): #Loop for all benchmarks 
    for j in range(0,3): #Loop for all sizes
        bk = benchmarks[i]
        ks = key_size[j]
        command = "/root/CEERI/Modified_SAT/bin/sld /root/CEERI/Verilog_Files/Locked_Files/"
        command+= bk+"/"+ks+"/"+bk+"_K"+ks+"_0.bench"+" /root/CEERI/Verilog_Files/Benchmarks/"+bk+".bench" #Define the command depending upon path
        result = subprocess.run(command, shell=True, capture_output=True, text=True) #Call Subprocess
        #print(result)
        if result.returncode == 0:
            filename  = "SAT_"+benchmarks[i]+"_log.txt" #Define file name for logs
            header = benchmarks[i]+"_K"+key_size[j]+"_Attack"+"\n"
            with open(filename, "a") as file: #Write to file
                file.write(header+"\n")
                file.write(result.stdout+"\n\n")
                print("Output saved to "+filename)
        else:
          print("Command failed with error:", result.stderr)