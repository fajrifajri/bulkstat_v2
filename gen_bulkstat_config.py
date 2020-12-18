file = "bulkstat_scheme_all.log"
number = 20
schema = "mme"

'''
13    card      %cpu0-cpuused-user%                                           Float     0   Gauge
14    card      %cpu0-cpuused-sys%                                            Float     0   Gauge
15    card      %cpu0-cpuused-io%                                             Float     0   Gaug
'''

bulkstat_file = open(file)
bulkstat = bulkstat_file.readlines()
bulkstat_file.close()

num = 0
line_num = 0
for line in bulkstat:
    line = ' '.join(line.split())
    sch = line.split(" ")[1]
    metric = line.split(" ")[2]
    
    if sch == schema and line.split(" ")[5] != "Info":
        if line_num % number == 0:
            num += 1
            print("{} schema {}Sch{} format {}Sch{},%localdate%,%localtime%,%servname%,{}".format(schema, schema, num, schema, num, metric), end = ",")
        elif (line_num+1)%20 == 0:
            print("{}".format(metric))
        else:
            print("{}".format(metric), end=",")
        line_num +=1

