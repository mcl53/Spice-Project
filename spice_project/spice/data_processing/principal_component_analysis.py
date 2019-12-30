import pandas as pd
from sklearn import preprocessing
from sklearn.decomposition import PCA
from read_write import read_in_data
from directories import read_data
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix


def Do_PCA(filepath):
    
    test_data = read_in_data(filepath)["z"]
    print(test_data)

    strains = ["2bromo", "2chloro", "2fluoro", "2iodo", "5fadb", "5fpb22", "am679", "am694"]

    spice_data = {}

    files = {}

    for strain in strains:
        len_before = len(spice_data)
        saliva_data = read_data(strain, True)
        for key in saliva_data.keys():
            spice_data[key + len_before] = saliva_data[key]

        non_saliva_data = read_data(strain, False)
        for key in non_saliva_data.keys():
            spice_data[key + len_before + len(saliva_data)] = non_saliva_data[key]
        files[strain] = len(spice_data) - len_before

    non_spice_data = read_data(in_saliva=True)
    non_spice_non_saliva = read_data(in_saliva=False)
    non_spice_data.update(non_spice_non_saliva)
    files["not_spice"] = len(non_spice_data)

    all_values = list(x["z"] for x in spice_data.values())
    all_values.extend(list(x["z"] for x in non_spice_data.values()))

    scaled_data = preprocessing.scale(all_values)
    scaled_test = preprocessing.scale(test_data)
    pca = PCA(n_components=0.95, svd_solver="full")
    pca.fit(scaled_data)
    X_transform = pca.transform(scaled_data)
    
    test_data = pca.transform(scaled_test.reshape(1, -1))

    classes = []

    for key in files.keys():
        if key in strains:
            cat = "spice"
        else:
            cat = "not_spice"
        num = files[key]
        for i in range(0, num):
            classes.append(cat)

    X = pd.DataFrame(X_transform)

    data_and_classes = X.copy()
    data_and_classes.insert(6, "class", classes)

    le = LabelEncoder()
    y = le.fit_transform(data_and_classes["class"])
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=1)
    
    dt = DecisionTreeClassifier()
    dt.fit(X, y)
    
    y_pred = dt.predict(X_test)
    print(confusion_matrix(y_test, y_pred))
    
    print(dt.predict(test_data))
    

if __name__ == "__main__":
    Do_PCA("../data/spice/non_saliva/2bromo/2bromo degraded xyz data.csv")
