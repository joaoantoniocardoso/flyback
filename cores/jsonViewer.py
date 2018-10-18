#!/usr/bin/python3
import json

with open("thornton_cores.json", 'r') as f:
    cores = json.load(f)

for c in cores:
    print(c)

