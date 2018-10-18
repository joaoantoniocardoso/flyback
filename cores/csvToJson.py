#!/usr/bin/python3
import csv
import json

csvfile = open('thornton_cores.csv', 'r', encoding='utf-8')
jsonfile = open('thornton_cores.json', 'w', encoding='utf-8')
reader = csv.DictReader(csvfile)

fieldnames = ("Ae","Ae_units","Aw","Aw_units","le","le_units","lt","lt_units","V","V_units","AaAw","AeAw_units","Modelo")

output = []

for each in reader:
	row = {}
	for field in fieldnames:
		row[field] = each[field]

	output.append(row)

json.dump(output, jsonfile, indent=2, sort_keys=False)

