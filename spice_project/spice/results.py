from data_processing.read_write import read_in_data
from data_processing.directories import read_data
import numpy as np


def generate_results(filepath):
	new_data = read_in_data(filepath)
	return new_data
	
	
def mean_and_sd(data_in):
	strains = ["2bromo", "2chloro", "2fluoro", "2iodo", "5fadb", "5fpb22", "am679", "am694"]
	
	spice_data = {}
	i = 0
	
	for strain in strains:
		data = read_data(strain, False)
		for x in data.keys():
			i += 1
			spice_data[i] = data[x]
		data = read_data(strain, True)
		for x in data.keys():
			i += 1
			spice_data[i] = data[x]
	
	non_spice_data = read_data(in_saliva=True)
	
	spice_values = []
	
	for i in spice_data.keys():
		df = spice_data[i]
		lst = df["z"]
		spice_values.append(lst)

	non_spice_values = []
	
	for i in non_spice_data.keys():
		df = non_spice_data[i]
		lst = df["z"]
		non_spice_values.append(lst)
	
	spice_means = []
	spice_sds = []
	for i in range(len(spice_values[0])):
		values = []
		for j in spice_values:
			values.append(j[i])
		spice_means.append(np.average(values))
		spice_sds.append(np.std(values))
	
	non_spice_means = []
	non_spice_sds = []
	for i in range(len(non_spice_values[0])):
		values = []
		for j in non_spice_values:
			values.append(j[i])
		non_spice_means.append(np.average(values))
		non_spice_sds.append(np.std(values))
	
	x = 0
	spice_total = 0
	non_spice_total = 0
	for i in data_in["z"]:
		spice_mean = spice_means[x]
		non_spice_mean = non_spice_means[x]
		spice_sd = spice_sds[x]
		non_spice_sd = non_spice_sds[x]
		
		spice_add = abs(spice_mean - i) / spice_sd
		non_spice_add = abs(non_spice_mean - i) / non_spice_sd
		
		if not np.isnan(spice_add):
			spice_total += spice_add
		if not np.isnan(non_spice_add):
			non_spice_total += non_spice_add
			
		x += 1
		
	print(non_spice_total, spice_total)
	is_spice = non_spice_total > spice_total
	return is_spice
