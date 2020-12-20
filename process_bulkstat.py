#!/usr/bin/env python3

import re
import sys
import os


bulkstat_file = sys.argv[1]

pushgateway_ip = "127.0.0.1"
sch_to_metric_file  = open("bulkstat_sch_to_metric.csv")
sch_to_metric = sch_to_metric_file.readlines()
sch_to_metric_file.close()

bulkstat_schema_config = open("bulkstat_config.cfg")
bulkstat_schema = bulkstat_schema_config.readlines()
bulkstat_schema_config.close()

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
    """
    this function is to generate mapping between disconnect reason number and disconnect reason readable value
    this is based on 
    the mapping is:
        disc-reason-0,Unknown
        disc-reason-1,Admin-disconnect
        disc-reason-2,Remote-disconnect
        disc-reason-3,Local-disconnect
        disc-reason-4,No-resource
    """
    for schema in sch_to_metric:
        schema_name = schema.split(",")[0].strip()
        metric_name = schema.split(",")[1].strip()
        schema_to_metric.setdefault(schema_name, metric_name)

def load_bulkstat_schema():
    """
    This function is to load bulkstat schema data.
    bulkstat schema data is an output of "show config bulkstat"

    input:
    card schema cardSch9 format cardSch9,%localdate%,%localtime%,%card%,%cpu0-vpputil-txpkts-5minave%,%cpu0-vpputil-rxpkts-15minave%,%cpu0-vpputil-txpkts-15minave%,%cpu0-vpp-rx-pkts%,%cpu0-vpp-tx-pkts%,%cpu0-vpp-rx-bytes%,%cpu0-vpp-tx-bytes%,%cpu0-vpp-rx-miss%,%cpu0-vpp-rx-err%,%cpu0-vpp-tx-err%,%cpu0-vpp-rx-nombuf%,%cpu0-vpp-rx-size-0-63%,%cpu0-vpp-rx-size-64%,%cpu0-vpp-rx-size-65-127%,%cpu0-vpp-rx-size-128-255%,%cpu0-vpp-rx-size-256-511%,%cpu0-vpp-rx-size-512-1023%,%cpu0-vpp-rx-size-1024-1518%,%cpu0-vpp-rx-size-1519-max%,%cpu0-vpp-tx-size-64%,%cpu0-vpp-tx-size-65-127%,%cpu0-vpp-tx-size-128-255%,%cpu0-vpp-tx-size-256-511%,%cpu0-vpp-tx-size-512-1023%,%cpu0-vpp-tx-size-1024-1518%,%cpu0-vpp-tx-size-1519-max%,%cpu0-vpp-sw-rx-pkts%,%cpu0-vpp-sw-tx-pkts%,%cpu0-vpp-sw-rx-bytes%,%cpu0-vpp-sw-tx-bytes%,%cpu0-vpp-sw-rx-ip4%,%cpu0-vpp-sw-rx-ip6%,%cpu0-vpp-sw-rx-drops%,%cpu1-vpputil-now%,%cpu1-vpputil-5minave%,%cpu1-vpputil-15minave%,%cpu1-vpputil-rxbytes-5secave%,%cpu1-vpputil-txbytes-5secave%,%cpu1-vpputil-rxbytes-5minave%,%cpu1-vpputil-txbytes-5minave%
    schema disconnectReason1 format disconnectReason1,%localdate%,%localtime%,%apn%%disc-reason-0%,%disc-reason-1%,%disc-reason-2%,%disc-reason-3%,%disc-reason-4%,%disc-reason-5%,%disc-reason-6%,%disc-reason-7%,%disc-reason-8%,%disc-reason-9%,%disc-reason-10%,%disc-reason-11%,%disc-reason-12%,%disc-reason-13%,%disc-reason-14%,%disc-reason-15%,%disc-reason-16%,%disc-reason-17%,%disc-reason-18%,%disc-reason-19%,%disc-reason-20%,%disc-reason-21%,%disc-reason-22%,%disc-reason-23%,%disc-reason-24%,%disc-reason-25%,%disc-reason-26%,%disc-reason-27%,%disc-reason-28%,%disc-reason-29%,%disc-reason-30%,%disc-reason-31%,%disc-reason-32%,%disc-reason-33%,%disc-reason-34%,%disc-reason-35%,%disc-reason-36%,%disc-reason-37%,%disc-reason-38%,%disc-reason-39%,%disc-reason-40%,%disc-reason-41%,%disc-reason-42%,%disc-reason-43%,%disc-reason-44%,%disc-reason-45%,%disc-reason-46%,%disc-reason-47%,%disc-reason-48%,%disc-reason-49%,%disc-reason-50%,%disc-reason-51%,%disc-reason-52%,%disc-reason-53%,%disc-reason-54%,%disc-reason-55%,%disc-reason-56%,%disc-reason-57%,%disc-reason-58%,%disc-reason-59%
      

    output as a dictionoary
    'disconnectReason8': {4: '%disc-reason-350%', 5: '%disc-reason-351%', 6: '%disc-reason-352%', 7: '%disc-reason-353%', 8: '%disc-reason-354%', 9: '%disc-reason-355%',

    """
    for line in bulkstat_schema:
        line = line.strip()
        if "schema" in line:
            line = re.sub('\s+',' ', line)
            bulkstat_line = False        
            if line.split(" ")[0] == "schema":
                location = 3
                start = 2
                bulkstat_line = True
            elif line.split(" ")[1] == "schema":
                location = 4
                start = 3
                bulkstat_line = True
            if (bulkstat_line):
                bulkstat_config_line = line.split(" ")[location].split(",")
                for number,cfg in enumerate(bulkstat_config_line):
                    if number == 0:
                        bulkstat_config.setdefault(cfg, {})
                    if number>start:
                        bulkstat_config[bulkstat_config_line[0]].setdefault(number, cfg)


def load_bulkstat_data():
    """
    this function is to:
        (1) load bulkstat data
        (2) correlate bulkstat data with config
        (3) generate PushGateway Temporary config file
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
                work to do: adding group name in the label
                '''                    
                if number == 3:
                    groupname = bulkstat_data_line[3]
                elif number > 3:
                    if data != '0' and data != "" and data.isnumeric():
                        config = bulkstat_config[key][number].replace("%","")
                        output_file.write("ippool {{poolname=\"{}\", metric=\"{}\"}} {}\n".format(groupname.replace("-","_"), config.replace("-","_"), data))                                        
            else:
                if number ==3:
                    identifier = data
                elif number > 3:
                    if data != '0' and data != "" and data.isnumeric():
                        #print("{} - {} - {}".format(key, number, bulkstat_config[key][number]))                                               
                        config = bulkstat_config[key][number].replace("%","").split("-")                        
                        string_output = "{} {{id=\"{}\"".format(schema.replace("-","_"), identifier.replace("-","_"))
                        for num,met in enumerate(config):
                            string_output = string_output + ", metric{}=\"{}\"".format(num, met)
                        string_output = string_output + "}} {}\n".format(data)
                        output_file.write(string_output)
                            


def gen_pushgw_format():
    '''
    This function is to load pushgateway config file into pushgateway
    cmd = 'cat tempfile.txt |  curl --data-binary @- http://' + pushgateway +'/metrics/job/bulkstat/node/' +node
    os.system(cmd)
    '''
    output_file.close()

    command = "/bin/cat " + temp_file + "|  curl --data-binary @- http://" + pushgateway_ip + ":9091/metrics/job/plte/node/" + host
    os.system(command)

    
  

if __name__ == "__main__":
    load_sch_to_mtric()
    load_bulkstat_schema()
    load_bulkstat_data()
    gen_pushgw_format()
    #print(output)
 