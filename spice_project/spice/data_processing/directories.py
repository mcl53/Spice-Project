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

	
if __name__=="__main__":
	df = read_data("5fpb22", False)
