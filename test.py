metric = "tau-imsi-sgw-change-failures"

def convert_dash_to_nested(metric_with_dash):
    def nested_dict(new_dict, string):
        new_dict.setdefault(string, {})
        return(new_dict[string])
    metric_with_dict = current = {}
    metric_with_dash = metric_with_dash.split("-")
    # res = [{a: {b: c}} for (a, b, c) in zip(test_list1, test_list2, test_list3)] 
    metric_with_dash.insert(0,"output")
    for string in metric_with_dash:
        current[string] = {}
        current = current[string]
    
    return metric_with_dict


print(convert_dash_to_nested(metric))