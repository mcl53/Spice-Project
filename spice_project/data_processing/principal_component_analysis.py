import pandas as pd
from sklearn import preprocessing
from sklearn.decomposition import PCA
from read_write import read_in_data
from directories import read_all_spice_data, read_all_non_spice_data
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
import pickle


def create_new_pca_model(*acc_test_file_nums):
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

    if acc_test_file_nums:
        file_nums_to_exclude = [x for x in acc_test_file_nums]
        file_nums_to_exclude.sort(reverse=True)
        for i in file_nums_to_exclude:
            del all_values[i]
            del classes[i]

    scaled_data = preprocessing.scale(all_values)
    pca = PCA(n_components=0.95, svd_solver="full")
    pca.fit(scaled_data)
    X_transform = pca.transform(scaled_data)

    pickle.dump(pca, open("./pca_transform.p", "wb"))

    X = pd.DataFrame(X_transform)

    data_and_classes = X.copy()
    data_and_classes.insert(6, "class", classes)

    le = LabelEncoder()
    y = le.fit_transform(data_and_classes["class"])
    
    dt = DecisionTreeClassifier()
    dt.fit(X, y)
    pickle.dump(dt, open("./pca_model.p", "wb"))
    
    
def predict_data_using_pca(filepath):
    
    test_data = read_in_data(filepath)["z"]
    
    pca = pickle.load(open("pca_transform.p", "rb"))
    model = pickle.load(open("pca_model.p", "rb"))

    scaled_test = preprocessing.scale(test_data)
    X_pca = pca.transform(scaled_test.reshape(1, -1))

    prediction = model.predict(X_pca)
    if prediction[0] == 1:
        return True
    else:
        return False
    

if __name__ == "__main__":
    create_new_pca_model()
    is_spice = predict_data_using_pca("../data/spice/non_saliva/2bromo/2bromo degraded xyz data.csv")
    print(is_spice)
