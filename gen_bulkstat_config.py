#!/usr/bin/env python3

import sys

file = "bulkstat_scheme_all.log"

schema = sys.argv[1]

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
max_len = 950

start = True

for line in bulkstat:
    line = ' '.join(line.split())
    sch = line.split(" ")[1]
    metric = line.split(" ")[2]
    
    if sch == schema and line.split(" ")[5] != "Info":        
        line_num = line_num+len(metric)
        if start == True or line_num > max_len:
            start = False
            num += 1
            line_num = 0
            if schema == "apn":
                print("\n{} schema {}Sch{} format {}Sch{},%localdate%,%localtime%,%apn%,{}".format(schema, schema, num, schema, num, metric), end = "")
            elif schema == "radius":
                print("\n{} schema {}Sch{} format {}Sch{},%localdate%,%localtime%,%ipaddr%,{}".format(schema, schema, num, schema, num, metric), end = "")
            elif schema == "radius-group":
                print("\n{} schema {}Sch{} format {}Sch{},%localdate%,%localtime%,%group%,{}".format(schema, schema, num, schema, num, metric), end = "")                
            elif schema == "saegw":
                print("\n{} schema {}Sch{} format {}Sch{},%localdate%,%localtime%,%saegw-servname%,{}".format(schema, schema, num, schema, num, metric), end = "") 
            elif schema == "card":
                print("\n{} schema {}Sch{} format {}Sch{},%localdate%,%localtime%,%card%,{}".format(schema, schema, num, schema, num, metric), end = "")                 
            elif schema == "port":
                print("\n{} schema {}Sch{} format {}Sch{},%localdate%,%localtime%,%card%-%port%,{}".format(schema, schema, num, schema, num, metric), end = "")                 

            else:            
                print("\n{} schema {}Sch{} format {}Sch{},%localdate%,%localtime%,%servname%,{}".format(schema, schema, num, schema, num, metric), end = "")
        else:
            print(",{}".format(metric), end="")
    elif schema == "disconnectReason" and "disc-reason" in line.split(" ")[2] and line.split(" ")[2] != "%disc-reason-summary%":
        '''
        input: 1849  system    %disc-reason-681%                                             Int64     0   Counter
        output:  schema disconnectReason9 format disconnectReason9,%localdate%,%localtime%,%disc-reason-400%
        '''
        line_num = line_num+len(metric)
        if start == True or line_num > max_len:
            start = False
            num += 1
            line_num = 0
            print("\nschema disconnectReason{} format disconnectReason{},%localdate%,%localtime%,%apn%{}".format(num, num, metric), end = "")
        else:
            print(",{}".format(metric), end="")        



