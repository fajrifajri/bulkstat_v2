#!/usr/bin/env python3

import re
import sys
import os

#bulkstat_dir = "/home/afajri/bulkstat/"
#bulkstat_file = "mme-private-lte_bulkstats_20201217_221605_EST_5_5.csv"
bulkstat_file = sys.argv[1]

pushgateway_ip = "127.0.0.1"
sch_to_metric_file  = open("bulkstat_sch_to_metric.csv")
sch_to_metric = sch_to_metric_file.readlines()
sch_to_metric_file.close()

bulkstat_schema_file = open("bulkstat_scheme.csv")
bulkstat_schema = bulkstat_schema_file.readlines()
bulkstat_schema_file.close()

bulkstat_data_file = open(bulkstat_file)
bulkstat_data = bulkstat_data_file.readlines()
bulkstat_data_file.close()

host = bulkstat_file.split("_")[0]
temp_file = "temp_file.txt"
output_file = open(temp_file, "w+")

schema_to_metric  = {}
bulkstat_config = {}
output = {}

def load_sch_to_mtric():
    for schema in sch_to_metric:
        schema_name = schema.split(",")[0].strip()
        metric_name = schema.split(",")[1].strip()
        schema_to_metric.setdefault(schema_name, metric_name)

def load_bulkstat_schema():
    """
    input:
    system       disconnectReason3        No          disconnectReason3,MME,%localdate%,%localtime%,%disc-reason-100%,%disc-reason-101%,%disc-reason-102%,%disc-reason-103%,%disc-reason-104%,%disc-reason-105%,%disc-reason-106%,%disc-reason-107%,%disc-reason-108%,%disc-reason-109%,%disc-reason-110%,%disc-reason-111%,%disc-reason-112%,%disc-reason-113%,%disc-reason-114%,%disc-reason-115%,%disc-reason-116%,%disc-reason-117%,%disc-reason-118%,%disc-reason-119%,%disc-reason-120%,%disc-reason-121%,%disc-reason-122%,%disc-reason-123%,%disc-reason-124%,%disc-reason-125%,%disc-reason-126%,%disc-reason-127%,%disc-reason-128%,%disc-reason-129%,%disc-reason-130%,%disc-reason-131%,%disc-reason-132%,%disc-reason-133%,%disc-reason-134%,%disc-reason-135%,%disc-reason-136%,%disc-reason-137%,%disc-reason-138%,%disc-reason-139%,%disc-reason-140%,%disc-reason-141%,%disc-reason-142%,%disc-reason-143%,%disc-reason-144%,%disc-reason-145%,%disc-reason-146%,%disc-reason-147%,%disc-reason-148%,%disc-reason-149%
    output:
    'disconnectReason8': {4: '%disc-reason-350%', 5: '%disc-reason-351%', 6: '%disc-reason-352%', 7: '%disc-reason-353%', 8: '%disc-reason-354%', 9: '%disc-reason-355%',
    """
    for line in bulkstat_schema:
        line = line.strip()
        line = re.sub('\s+',' ', line)
        bulkstat_config_line = line.split(" ")[3].split(",")
        for number,cfg in enumerate(bulkstat_config_line):
            if number == 0:
                bulkstat_config.setdefault(cfg, {})
            if number>3:
                bulkstat_config[bulkstat_config_line[0]].setdefault(number, cfg)

def load_bulkstat_data():
        """
                disconnectReason8,20201217,183214,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,91,0,0,12,0,0,110,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1
                mmeSch56,20201217,221500,s1-mme,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
                radius-groupSch4,20201218,174640,%servname%,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
        """
        for line in bulkstat_data:
            line = line.strip()
            bulkstat_data_line = line.split(",")
            schema_match = re.search(r"(^.*)Sch",line)
            temp_output = {}
            if schema_match:
                schema = schema_match.group(1)
            for number, data in enumerate(bulkstat_data_line):                
                if schema not in output:
                   output.setdefault(schema, {})
                if number == 0:
                    key = data
                

                #handle disconnect_reason
                if "disconnect" in key:
                    if key in bulkstat_config and number > 2 and data != "0":                                              
                        config = bulkstat_config[key][number].replace("%","")
                        metric = schema_to_metric[config]
                        output_file.write("disconnectReason {{reason=\"{}\"}} {}\n".format(metric.replace("-","_"), data)) 
                elif key == "ippoolSch1":
                    '''
                    Special condition to handle IP Pool
                    ippoolSch1,20201218,182500,pool-3669,0,0,0,244,10.66.0.11
                    '''                    
                    if number == 3:
                        groupname = bulkstat_data_line[3]
                    elif number > 3:
                        if data != '0' and data != "" and data.isnumeric():
                            config = bulkstat_config[key][number].replace("%","")
                            output_file.write("ippool {{poolname=\"{}\", metric=\"{}\"}} {}\n".format(groupname.replace("-","_"), config.replace("-","_"), data)) 

                elif key == "ippoolSch2":
                    '''
                    Special condition to handle IP Pool group
                    ippoolSch2,20201218,182500,0,0,0,0,0,0,0,0
                    '''                
                    if(bulkstat_data_line[3] != "0"):
                        if number == 3:
                            groupname = bulkstat_data_line[3]
                        elif number > 3:
                            if data != '0' and data != "" and data.isnumeric():
                                config = bulkstat_config[key][number].replace("%","")
                                output_file.write("ippool_group {poolname = \"{}\", metric = \"{}\"} {}\n".format(groupname.replace("-","_"), config.replace("-","_"), data)) 
                                            
                else:
                    if number ==3:
                        identifier = data
                    elif number > 3:
                        if data != '0' and data != "" and data.isnumeric():
                            config = bulkstat_config[key][number].replace("%","").split("-")
                            string_output = "{} {{id=\"{}\"".format(schema.replace("-","_"), identifier.replace("-","_"))
                            for num,met in enumerate(config):
                                string_output = string_output + ", metric{}=\"{}\"".format(num, met)
                            string_output = string_output + "}} {}\n".format(data)
                            output_file.write(string_output)
                            


def gen_pushgw_format():
    '''
    cmd = 'cat tempfile.txt |  curl --data-binary @- http://' + pushgateway +'/metrics/job/bulkstat/node/' +node
    os.system(cmd)
    '''
    output_file.close()

    command = "/bin/cat " + temp_file + "|  curl --data-binary @- http://" + pushgateway_ip + ":9091/metrics/job/bulkstat/node/" + host
    print(command)
    os.system(command)

    
  

if __name__ == "__main__":
    load_sch_to_mtric()
    load_bulkstat_schema()
    load_bulkstat_data()
    gen_pushgw_format()
    #print(output)
 