from read_write import read_in_data
import os
import re

# Variables for data locations

data_root = "../data"
not_spice = "not_spice"
spice = "spice"
saliva = "saliva"
non_saliva = "non_saliva"
examples = "examples"
strains = ["2bromo", "2chloro", "2fluoro", "2iodo", "5fadb", "5fpb22", "am679", "am694"]


def read_data(strain=None, in_saliva=True):
	try:
		assert strain in strains or strain is None
	except AssertionError:
		print("Strain is not recognised")
		return
	
	if in_saliva:
		sal_dir = saliva
	else:
		sal_dir = non_saliva
	
	if strain is None:
		spice_dir = not_spice
		path = os.path.join(data_root, spice_dir, sal_dir)
	else:
		spice_dir = spice
		path = os.path.join(data_root, spice_dir, sal_dir, strain)
	
	files = []
	regex = "[a-zA-Z0-9_]\\.csv"
	for r, d, f in os.walk(path):
		for file in f:
			match = re.search(regex, file)
			if match is not None:
				files.append(file)
	
	paths = []
	for file in files:
		paths.append(os.path.join(path, file))
	
	dataframes = {}
	count = 0
	
	for path in paths:
		count += 1
		data = read_in_data(path)
		dataframes[count] = data
	
	return dataframes


def read_all_spice_data():
	
	spice_data = {}
	files = {}
	i = 0
	
	for strain in strains:
		len_before = len(spice_data)
		data = read_data(strain, False)
		for x in data.keys():
			i += 1
			spice_data[i] = data[x]["z"]
		data = read_data(strain, True)
		for x in data.keys():
			i += 1
			spice_data[i] = data[x]["z"]
		files[strain] = len(spice_data) - len_before
	
	return spice_data, files


def read_all_non_spice_data():
	non_spice_data = read_data(in_saliva=True)
	non_spice_non_saliva = read_data(in_saliva=False)
	
	length = len(non_spice_data)
	
	for i, data in enumerate(non_spice_non_saliva.values()):
		non_spice_data[length + i + 1] = data
	
	for i in non_spice_data.keys():
		non_spice_data[i] = non_spice_data[i]["z"]
	
	files = {"not_spice": len(non_spice_data)}
		
	return non_spice_data, files

	
if __name__ == "__main__":
	# df = read_data("5fpb22", False)
	data, files = read_all_non_spice_data()
	print(len(data), len(files))
	print(data)
