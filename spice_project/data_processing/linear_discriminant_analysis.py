try:
	from .directories import read_data, read_all_spice_data, read_all_non_spice_data
	from .read_write import read_in_data
except ImportError:
	from directories import read_data, read_all_spice_data, read_all_non_spice_data
	from read_write import read_in_data

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix
import pickle
import os
from flask import current_app as app


def create_new_lda_model(*acc_test_file_nums):
	
	spice_data, files = read_all_spice_data()
	non_spice_data, non_spice_files = read_all_non_spice_data()
	
	all_values = list(x for x in spice_data.values())
	all_values.extend(list(x for x in non_spice_data.values()))
	
	files.update(non_spice_files)
	
	classes = []
	
	for key in files.keys():
		if key != "not_spice":
			cat = "spice"
		else:
			cat = "not_spice"
		num = files[key]
		for i in range(0, num):
			classes.append(cat)
	
	# Removing certain pieces of data if doing a model accuracy test
	
	if acc_test_file_nums:
		file_nums_to_exclude = [x for x in acc_test_file_nums]
		file_nums_to_exclude.sort(reverse=True)
		for i in file_nums_to_exclude:
			del all_values[i]
			del classes[i]
	
	# Removing all zero values from data to allow for matrix inversion below
	
	zero_values = np.array([])
	for i in range(len(all_values)):
		zeros = []
		for j in range(len(all_values[i])):
			if all_values[i][j] == 0:
				zeros.append(j)
		zero_values = np.append(zero_values, zeros)
	
	zero_values = np.unique(zero_values)
	
	for i in zero_values:
		for j in all_values:
			del j[i]
	
	max_length = 0
	for i in all_values:
		if len(i) > max_length:
			max_length = len(i)
	
	X = pd.DataFrame(all_values)
	y = pd.Categorical(classes)
	
	data_and_classes = X.copy()
	data_and_classes.insert(max_length, "class", classes)
	
	class_feature_means = pd.DataFrame(columns=y.categories)
	for c, rows in data_and_classes.groupby("class"):
		class_feature_means[c] = rows.mean()
	
	within_class_scatter_matrix = np.zeros((max_length, max_length))
	
	for c, rows in data_and_classes.groupby("class"):
		rows = rows.drop(["class"], axis=1)
		s = np.zeros((max_length, max_length))
		
		for i, row in rows.iterrows():
			x, mc = row.values.reshape(max_length, 1), class_feature_means[c].values.reshape(max_length, 1)
			s += (x - mc).dot((x - mc).T)
		
		within_class_scatter_matrix += s
	
	feature_means = data_and_classes.mean()
	
	between_class_scatter_matrix = np.zeros((max_length, max_length))
	
	for c in class_feature_means:
		n = len(data_and_classes.loc[data_and_classes["class"] == c].index)
		mc, m = class_feature_means[c].values.reshape(max_length, 1), feature_means.values.reshape(max_length, 1)
		
		between_class_scatter_matrix += n * (mc - m).dot((mc - m).T)
	
	eigen_values, eigen_vectors = np.linalg.eig(
		np.linalg.inv(within_class_scatter_matrix).dot(between_class_scatter_matrix))
	pairs = [(np.abs(eigen_values[i]), eigen_vectors[:, i]) for i in range(len(eigen_values))]
	pairs = sorted(pairs, key=lambda x: x[0], reverse=True)
	
	eigen_sum = sum(x[0] for x in pairs)
	significant_data_points = []
	for i, value in enumerate(pairs):
		contribution = value[0] / eigen_sum * 100
		if contribution > 1:
			significant_data_points.append(value[1].reshape(max_length, 1))
	
	w_matrix = np.hstack(tuple(significant_data_points)).real
	
	X_lda = np.array(X.dot(w_matrix))
	
	zero_values = np.array(zero_values)
	np.savetxt("./zeros.txt", zero_values)
	np.savetxt("./w_matrix.txt", w_matrix)
	
	le = LabelEncoder()
	
	y = le.fit_transform(data_and_classes["class"])
	
	dt = DecisionTreeClassifier()
	
	dt.fit(X_lda, y)
	pickle.dump(dt, open("./model.p", "wb"))


def predict_data_using_lda(filepath):
	
	new_data = read_in_data(filepath)["z"]
	
	path_to_w_matrix = "./w_matrix.txt"
	path_to_zeros = "./zeros.txt"
	path_to_model = "./model.p"
	
	w_matrix = np.loadtxt(path_to_w_matrix)
	zeros = np.loadtxt(path_to_zeros)
	
	for i in zeros:
		del new_data[i]
	
	X_lda = np.array(new_data.dot(w_matrix)).reshape(1, -1)
	
	model = pickle.load(open(path_to_model, "rb"))
	
	prediction = model.predict(X_lda)
	if prediction[0] == 1:
		return True
	else:
		return False


if __name__ == "__main__":
	# create_new_lda_model()
	
	is_spice = predict_data_using_lda("../data/not_spice/saliva/saliva after cigar with exodus xyz.csv")
	print(is_spice)
