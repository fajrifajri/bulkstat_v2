#!/usr/bin/env python3

import re

bulkstat_dir = "/home/afajri/bulkstat/"
bulkstat_file = "mme-private-lte_bulkstats_20201217_204437_EST_5_5.csv"

sch_to_metric_file  = open("bulkstat_sch_to_metric.csv")
sch_to_metric = sch_to_metric_file.readlines()
sch_to_metric_file.close()

bulkstat_schema_file = open("bulkstat_scheme.csv")
bulkstat_schema = bulkstat_schema_file.readlines()
bulkstat_schema_file.close()

bulkstat_data_file = open(bulkstat_dir + bulkstat_file)
bulkstat_data = bulkstat_data_file.readlines()
bulkstat_data_file.close()

schema_to_metric = {}
output = {}
bulkstat_config = {}

host = bulkstat_file.split("_")[0]

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
        """
        for line in bulkstat_data:
                line = line.strip()
                bulkstat_data_line = line.split(",")
                for number, data in enumerate(bulkstat_data_line):
                        if number == 0:
                                key = data
                        #handle disconnect_reason
                        if "disconnectReason" in key:
                                output.setdefault("disconnectReason",{})
                                if key in bulkstat_config and number > 2 and data != "0":
                                        data = int(data)
                                        config = bulkstat_config[key][number].replace("%","")
                                        metric = schema_to_metric[config]
                                        output["disconnectReason"].setdefault(metric, data)


if __name__ == "__main__":
        load_sch_to_mtric()
        load_bulkstat_schema()
        load_bulkstat_data()
        print(output)