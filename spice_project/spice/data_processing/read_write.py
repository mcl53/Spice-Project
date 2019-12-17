import pandas as pd
import os
import re
import numpy as np

path_to_examples = "data/spice/examples"
strains = ["5fadb", "am679", "am694"]


def read_in_data(filepath):
	"""
	Reads an individual file and returns the output as a pandas DataFrame
	:param filepath: the path to the file to read
	:return: pandas DataFrame containing data in the correct shape
	"""
	try:
		data = pd.read_csv(filepath, index_col=False)
		assert data.shape == (18763, 3)
		
	except FileNotFoundError as e:
		print(type(e))
		print("File " + filepath + " does not exist")
		return
	
	except AssertionError as e:
		print(type(e))
		print("Data in file " + filepath + " is not the correct shape, " + str(data.shape) + " attempting to convert")
		data = convert_to_xyz(filepath)
	
	finally:
		return data


def write_data(filepath, data):
	"""
	Writes data in the correct format to the desired directory and will not write if data is not in the correct format
	:param filepath: the path to the desired file output directory
	:param data: pandas DataFrame containing z data in a 2x2 matrix
	:return: None
	"""
	try:
		assert data.shape == (18763, 3)
	
	except AssertionError as e:
		print(type(e))
		print("Data in DataFrame is not the correct shape. Actual shape was" + str(data.shape))
		
	else:
		data.to_csv(filepath, header=False, index=False)


def read_example_data(path):
	"""
	Reads in data from csv files in the examples directory
	:param path: path to example data. Intended to be the path_to_examples variable
	:return: dataframes: a dictionary of dataframes read from each csv file in the examples directory
	"""
	files = []
	regex = "[a-zA-Z0-9_]\\.csv"
	for r, d, f in os.walk(path):
		for file in f:
			match = re.search(regex, file)
			if match is not None:
				files.append(file)
	
	files.sort()
	dataframes = {}
	count = 0
	for file in files:
		strain = strains[count]
		count += 1
		filepath = os.path.join(path, strain, file)
		dataframes[count] = read_in_data(filepath)
		
	print(dataframes)
	return dataframes


def convert_to_xyz(filepath):
	"""
	Converts a file from the grid format to xyz columns
	:param filepath: path of the file to convert
	:return: Converted dataframe
	"""
	df = pd.read_csv(filepath, index_col=[0])
	if 598.5 in df.index:
		df = df.drop(598.5, axis=0)

	for col in df:
		index = 0
		for i in df[col]:
			if np.isnan(i):
				df[col].iloc[index] = 0
			index += 1
	
	cols = df.columns
	rows = df.index
	rows, cols = np.meshgrid(rows, cols)
	for i in range(len(cols)):
		for j in range(len(cols[i])):
			cols[i][j] = int(cols[i][j])
	
	xyz_df = pd.DataFrame({'x':cols.flatten(), 'y':rows.flatten().flatten(), 'z':df.values.T.flatten()})
	xyz_df.to_csv(filepath, index=False)
	return xyz_df


if __name__ == "__main__":
	# read_example_data(path_to_examples)
	convert_to_xyz("/Users/matt/Documents_(hard_drive)/repositories/Spice-Project/spice_project/spice/data/not_spice/non_saliva/Indazole_5_ug_4_point_5nm_500 cleaned3.csv")
