import json

def parse_logos():
    logos_dict = {}
    with open('logos_plain_text.txt') as f:
        line = f.readline()
        count = 0
        while line:
            str_parts = line.split('"')
            name = str_parts[3]
            src = str_parts[1]
            logos_dict[name] = src
            line = f.readline()
    return logos_dict

def export_dict(dict):
    j = json.dumps(dict)
    f = open("logos_dict.json","w")
    f.write(j)
    f.close()

# d = parse_logos()
# export_dict(d)

