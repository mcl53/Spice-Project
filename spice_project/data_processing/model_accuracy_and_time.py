try:
	from .mean_and_sd import *
	from .principal_component_analysis import *
	from .linear_discriminant_analysis import *
except ImportError:
	import mean_and_sd
	import principal_component_analysis
	import linear_discriminant_analysis
import time
import os
import re
from random import randint
import json
from flask import jsonify


def get_files():
	
	count = 0
	files = []
	
	regex = "[a-zA-Z0-9_]\\.csv"
	for r, d, f in os.walk("../data"):
		for file in f:
			rel_dir = os.path.relpath(r, "../data")
			rel_file = os.path.join(rel_dir, file)
			match = re.search(regex, file)
			if match is not None:
				count += 1
				files.append(rel_file)
	
	# Only need to return the count for the number of spice files as total - spice = non_spice
	spice_file_num = 0
	for r, d, f in os.walk("../data/spice"):
		for file in f:
			match = re.search(regex, file)
			if match is not None:
				spice_file_num += 1
	
	return files, spice_file_num


def run_modelling_tests():

	files, spice_file_num = get_files()
	
	results = {}
	
	# Choose the number of files to emit from each test model. There will be an 80/20 train/test split
	no_of_files = len(files)
	no_per_run = no_of_files // 5
	lst_of_nums = list(x for x in range(0, no_of_files))
	
	# Remove the file numbers we want to remove from each run so the aren't emitted more than once over the whole test
	
	emitted_files = []
	
	for i in range(5):

		if i == 4:
			emitted_files.append(lst_of_nums)
			break
		
		lst_for_run = []
		for j in range(no_per_run):
			num = lst_of_nums.pop(randint(0, len(lst_of_nums) - 1))
			lst_for_run.append(num)
		emitted_files.append(lst_for_run)
	
	# Firstly mean and sd
	mean_and_sd_model_times = []
	mean_and_sd_pred_times = []
	mean_and_sd_pred_acc = []
	for i in emitted_files:
		i.sort(reverse=True)
		time_start = time.time()
	
		mean_and_sd.create_new_mean_and_sd_model(*i)
		time_after_mean_and_sd_model = time.time()
		mean_and_sd_model = time_after_mean_and_sd_model - time_start
		mean_and_sd_model_times.append(mean_and_sd_model)
		
		for j in i:
			
			file = os.path.join("../data", files[j - 1])
			
			time_before_pred = time.time()
			pred = mean_and_sd.predict_data_using_mean_and_sd(file)
			time_after_pred = time.time()
			mean_and_sd_pred = time_after_pred - time_before_pred
			mean_and_sd_pred_times.append(mean_and_sd_pred)
			
			if j < spice_file_num:
				if pred:
					# Spice file was predicted as spice
					mean_and_sd_pred_acc.append(1)
				else:
					# Non spice file was predicted as spice
					mean_and_sd_pred_acc.append(0)
			else:
				if pred:
					# Spice file was predicted as non spice
					mean_and_sd_pred_acc.append(0)
				else:
					# Non spice file was predicted as non spice
					mean_and_sd_pred_acc.append(1)
	
	ave_mean_and_sd_model_time = round(sum(mean_and_sd_model_times) / len(mean_and_sd_model_times), 3)
	ave_mean_and_sd_pred_time = round(sum(mean_and_sd_pred_times) / len(mean_and_sd_pred_times), 3)
	mean_and_sd_pred_acc = round(sum(mean_and_sd_pred_acc) / len(mean_and_sd_pred_acc) * 100, 3)
	
	mean_and_sd_dict = {"model_time": ave_mean_and_sd_model_time, "pred_time": ave_mean_and_sd_pred_time, "acc": mean_and_sd_pred_acc}
	results["mean_and_sd"] = mean_and_sd_dict
	
	print(f"Average mean and sd model creation time: {ave_mean_and_sd_model_time}s")
	print(f"Average mean and sd prediction time: {ave_mean_and_sd_pred_time}s")
	print(f"Mean and sd prediction accuracy: {mean_and_sd_pred_acc}%")
	
	# Now PCA
	pca_model_times = []
	pca_pred_times = []
	pca_pred_acc = []
	for i in emitted_files:
		i.sort(reverse=True)
		time_start = time.time()
		
		principal_component_analysis.create_new_pca_model(*i)
		time_after_pca_model = time.time()
		pca_model = time_after_pca_model - time_start
		pca_model_times.append(pca_model)
		
		for j in i:
			
			file = os.path.join("../data", files[j - 1])
			
			time_before_pred = time.time()
			pred = principal_component_analysis.predict_data_using_pca(file)
			time_after_pred = time.time()
			pca_pred = time_after_pred - time_before_pred
			pca_pred_times.append(pca_pred)
			
			if j < spice_file_num:
				if pred:
					# Spice file was predicted as spice
					pca_pred_acc.append(1)
				else:
					# Non spice file was predicted as spice
					pca_pred_acc.append(0)
			else:
				if pred:
					# Spice file was predicted as non spice
					pca_pred_acc.append(0)
				else:
					# Non spice file was predicted as non spice
					pca_pred_acc.append(1)
	
	ave_pca_model_time = round(sum(pca_model_times) / len(pca_model_times), 3)
	ave_pca_pred_time = round(sum(pca_pred_times) / len(pca_pred_times), 3)
	pca_pred_acc = round(sum(pca_pred_acc) / len(pca_pred_acc) * 100, 3)
	
	pca_dict = {"model_time": ave_pca_model_time, "pred_time": ave_pca_pred_time, "acc": pca_pred_acc}
	results["pca"] = pca_dict
	
	print(f"Average PCA model creation time: {ave_pca_model_time}s")
	print(f"Average PCA prediction time: {ave_pca_pred_time}s")
	print(f"PCA prediction accuracy: {pca_pred_acc}%")
	
	# LDA
	lda_model_times = []
	lda_pred_times = []
	lda_pred_acc = []
	for i in emitted_files:
		i.sort(reverse=True)
		time_start = time.time()

		linear_discriminant_analysis.create_new_lda_model(*i)
		time_after_lda_model = time.time()
		lda_model = time_after_lda_model - time_start
		lda_model_times.append(lda_model)

		for j in i:

			file = os.path.join("../data", files[j - 1])

			time_before_pred = time.time()
			pred = linear_discriminant_analysis.predict_data_using_lda(file)
			time_after_pred = time.time()
			lda_pred = time_after_pred - time_before_pred
			lda_pred_times.append(lda_pred)

			if j < spice_file_num:
				if pred:
					# Spice file was predicted as spice
					lda_pred_acc.append(1)
				else:
					# Non spice file was predicted as spice
					lda_pred_acc.append(0)
			else:
				if pred:
					# Spice file was predicted as non spice
					lda_pred_acc.append(0)
				else:
					# Non spice file was predicted as non spice
					lda_pred_acc.append(1)

	ave_lda_model_time = round(sum(lda_model_times) / len(lda_model_times), 3)
	ave_lda_pred_time = round(sum(lda_pred_times) / len(lda_pred_times), 3)
	lda_pred_acc = sum(lda_pred_acc) / len(lda_pred_acc) * 100
	
	lda_dict = {"model_time": ave_lda_model_time, "pred_time": ave_lda_pred_time, "acc": lda_pred_acc}
	results["lda"] = lda_dict
	
	print(f"Average LDA model creation time: {ave_lda_model_time}s")
	print(f"Average LDA prediction time: {ave_lda_pred_time}s")
	print(f"LDA prediction accuracy: {lda_pred_acc}%")
	
	results = json.dumps(results)
	print(results)
	
	with open("model_test_data.json", "w") as f:
		json.dump(str(results), f)


if __name__ == "__main__":
	run_modelling_tests()
