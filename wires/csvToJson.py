#!/usr/bin/python3
import csv
import json

csvfile = open('wires.csv', 'r', encoding='utf-8')
jsonfile = open('wires.json', 'w', encoding='utf-8')
reader = csv.DictReader(csvfile)

fieldnames = ("AWG","Dcu","Dcu_units","Acu","Acu_units","Dw","Dw_units","Aw","Aw_units","Rho20C","Rho20C_units","Rho100C","Rho100C_units","IDC450","IDC450_units")

output = []

for each in reader:
	row = {}
	for field in fieldnames:
		row[field] = each[field]

	output.append(row)

json.dump(output, jsonfile, indent=2, sort_keys=False)

