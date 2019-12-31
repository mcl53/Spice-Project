from read_write import read_in_data
from directories import read_data, read_all_spice_data, read_all_non_spice_data
import numpy as np
	
	
def create_new_mean_and_sd_model(*acc_test_file_nums):
	
	spice_data, files = read_all_spice_data()
	non_spice_data, non_spice_files = read_all_non_spice_data()
	
	spice_values = list(x for x in spice_data.values())
	non_spice_values = list(x for x in non_spice_data.values())
	
	if acc_test_file_nums:
		file_nums_to_exclude = [x for x in acc_test_file_nums]
		file_nums_to_exclude.sort(reverse=True)
		for i in file_nums_to_exclude:
			
			"""Data is stored in separate variables for spice and non spice data, so treating spice data as
			0 to len(spice_data) and non spice data as len(spice_data) + 1 to end"""
			
			if i < len(spice_data):
				del spice_data[i]
			else:
				del non_spice_data[i - len(spice_data)]
	
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
	
	spice_means = np.array(spice_means)
	spice_sds = np.array(spice_sds)
	non_spice_means = np.array(non_spice_means)
	non_spice_sds = np.array(non_spice_sds)
	
	np.savetxt("./spice_means.txt", spice_means)
	np.savetxt("./spice_sds.txt", spice_sds)
	np.savetxt("./non_spice_means.txt", non_spice_means)
	np.savetxt("./non_spice_sds.txt", non_spice_sds)


def predict_data_using_mean_and_sd(filepath):
	
	test_data = read_in_data(filepath)["z"]
	
	spice_means = np.loadtxt("./spice_means.txt")
	spice_sds = np.loadtxt("./spice_sds.txt")
	non_spice_means = np.loadtxt("./non_spice_means.txt")
	non_spice_sds = np.loadtxt("./non_spice_sds.txt")
	
	x = 0
	spice_total = 0
	non_spice_total = 0
	for i in test_data:
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


if __name__ == "__main__":
	create_new_mean_and_sd_model()
	is_spice = predict_data_using_mean_and_sd("../data/spice/non_saliva/2bromo/2bromo degraded xyz data.csv")
	print(is_spice)
