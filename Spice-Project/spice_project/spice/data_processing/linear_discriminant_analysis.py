import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix
from directories import read_data

strains = ["2bromo", "2chloro", "2fluoro", "2iodo", "5fadb", "5fpb22", "am679", "am694"]

spice_data = {}

i = 0

files = {}

for strain in strains:
	data = read_data(strain, False)
	len1 = len(data)
	for x in data.keys():
		i += 1
		spice_data[i] = data[x]
	data = read_data(strain, True)
	len2 = len(data)
	files[strain] = len1 + len2
	for x in data.keys():
		i += 1
		spice_data[i] = data[x]
		
non_spice_data = read_data(in_saliva=True)
files["not_spice"] = len(non_spice_data)

spice_values = []
all_values = []

for i in spice_data.keys():
	df = spice_data[i]
	lst = df["z"]
	spice_values.append(lst)
	all_values.append(lst)

non_spice_values = []

for i in non_spice_data.keys():
	df = non_spice_data[i]
	lst = df["z"]
	non_spice_values.append(lst)
	all_values.append(lst)

classes = []

for key in files.keys():
	if key in strains:
		cat = "spice"
	else:
		cat = "not_spice"
	num = files[key]
	for i in range(0, num):
		classes.append(cat)

X = pd.DataFrame(all_values)
y = pd.Categorical(classes)

data_and_classes = X.copy()
data_and_classes.insert(18763, "class", classes)

class_feature_means = pd.DataFrame(columns=y.categories)
for c, rows in data_and_classes.groupby("class"):
	class_feature_means[c] = rows.mean()

within_class_scatter_matrix = np.zeros((18763, 18763))

for c, rows in data_and_classes.groupby("class"):
	rows = rows.drop(["class"], axis=1)
	s = np.zeros((18763, 18763))

	for i, row in rows.iterrows():
		x, mc = row.values.reshape(18763, 1), class_feature_means[c].values.reshape(18763, 1)
		s += (x - mc).dot((x - mc).T)

	within_class_scatter_matrix += s

feature_means = data_and_classes.mean()

between_class_scatter_matrix = np.zeros((18763, 18763))

for c in class_feature_means:
	n = len(data_and_classes.loc[data_and_classes["class"] == c].index)
	mc, m = class_feature_means[c].values.reshape(18763, 1), feature_means.values.reshape(18763, 1)
	
	between_class_scatter_matrix += n * (mc - m).dot((mc - m).T)

eigen_values, eigen_vectors = np.linalg.eig(np.linalg.inv(within_class_scatter_matrix).dot(between_class_scatter_matrix))

pairs = [(np.abs(eigen_values[i]), eigen_vectors[:, i]) for i in range(len(eigen_values))]
pairs = sorted(pairs, key=lambda x: x[0], reverse=True)

w_matrix = np.hstack((pairs[0][1].reshape(18736, 1), pairs[1][1].reshape(18736, 1))).real

X_lda = np.array(X.dot(w_matrix))

le = LabelEncoder()

y = le.fit_transform(data_and_classes["class"])

dt = DecisionTreeClassifier()

X_train, X_test, y_train, y_test = train_test_split(X_lda, y, random_state=1)


dt.fit(X_train, y_train)
y_pred = dt.predict(X_test)
print(confusion_matrix(y_test, y_pred))
