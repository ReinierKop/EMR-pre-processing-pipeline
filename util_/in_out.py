import csv
import matplotlib.pyplot as plt
import numpy as np
from operator import itemgetter
import os
import util
from pprint import pprint

def read_csv(f, delim=','):
	'''opens a csv reader object'''
	return csv.reader(open(f, 'rb'), delimiter=delim)

def write_csv(f):
	'''opens a csv writer object'''	
	return csv.writer(open(f,"wb"))

def iter_to_csv(iterator, f):
	'''writes the contents of a generator to a csv file'''
	out = write_csv(f)
	for row in iterator:
		out.writerow(row)

def get_file_name(path, extension=True):
	'''returns the base name of path, with (default) or without extension'''
	# get file name
	f = os.path.basename(path)

	# remove file extension if desired
	if not extension:
		f = f[:f.rfind('.')]
	
	return f

def dict2csv(d, f):
	'''write a dictionary to csv format file'''
	out = write_csv(f)
	if len(d) == 0: 
		return
	if type(d.values()[0]) == list:
		for k, v in d.iteritems():
			out.writerow([k] + [str(el) for el in v])
	else:
		for k, v in d.iteritems():
			out.writerow([k, v])

def pprint_to_file(f_out, obj):
	'''performs the pretty print operation to the specified file with the specified data object'''
	with open (f_out, 'w') as out:
		pprint(obj, out)

def import_data(f, record_id, target_id, train_HISes=False):
	'''imports the data and converts it to X (input) and y (output) data vectors'''
	rows = read_csv(f)

	# save column names as headers, save indices of record and target IDs
	headers = util.get_headers(rows.next())
	
	try:
		record_col = headers.index(record_id)
		target_col = headers.index(target_id)
	except:
		print 'The specified instance ID was not found as column name. Manually check input file for correct instance ID column.'
		return False, False, False

	if not train_HISes:	
		# save and split records
		print '  ...(loading)'
		records = [row[1:] for row in rows]
		print '  ...(converting to matrix)'
		# print len(records), len(records[0])
		records = np.matrix(records)
		# print records.shape
		X = records[:,0:-1] # features
		headers = headers[1:-1]
		# print X.shape
		# convert gender to binary
		# X[X=='V'] = 1
		# X[X=='M'] = 0

		# output
		y = records[:,-1] # target
		# print y.shape
		# convert negative and positive CRC cases to integers 0 and 1, respectively
		# y[y=='negative'] = 0
		# y[y=='positive'] = 1
		y=np.squeeze(np.asarray(y.astype(np.int)))
		# print y.shape

		print '  ...(converting data type)'
		X = X.astype(np.float64, copy=False)
		y = y.astype(np.float64, copy=False)
		# print X[0:5,0:5]
		return X, y, headers
	else:
		# get HIS info from database
		c = util.sql_connect().cursor()
		train_HISes_str = "','".join(train_HISes)
		q = '''SELECT patientnummer 
				FROM patienten 
				WHERE praktijkcode IN ('{}')'''.format(train_HISes_str)
		c.execute(q)
		
		# patient_list = [row for row in c]

		# save and split records
		print '  ...(loading)'
		test_records = [int(row[0]):row[1:] for row in rows]
		
		print '  ...(dividing in train/test)'
		train_records = []
		for ID in c:
			if ID in test_records:
				train_records.append(test_records.pop(ID))

		print '  ...(converting to matrix)'
		train_records = np.matrix(train_records)
		test_records = np.matrix(test_records)
	
		print '  ...(converting data type)'
		train_records = train_records.astype(np.float64, copy=False)
		test_records = test_records.astype(np.float64, copy=False)

		# print '  ...(getting train/test indices)'
		# # r = records[:,0]
		# # hoi2 = c.next()[0]
		# # b = r > hoi2
		# # print r,hoi2,b, type(b)
		# # exit()
		# train_indices = []
		# test_indices = []	

		# # records[:,0]==(c.next()[0])
		# # print train_indices
		# IDs = records[:,0].view(np.int)
		# for p in c:
		# 	if p[0] in IDs:
		# 	# print type(train_indices), type(records[:,0]==p[0])
		# 	train_indices = train_indices + (records[:,0]==(p[0]))
		# print train_indices
		# print '  ...did it'
		# # train_indices = np.logical_or( *[records[:,0]==p for p in patient_list])
		# test_indices = ~train_indices

		X_tr = train_records[:,0:-1] # features
		X_te = test_records[:,0:-1] # features
		headers = headers[1:-1]

		# output
		y_tr = train_records[:,-1] 
		y_te = train_records[:,-1] 
		y_tr=np.squeeze(np.asarray(y_tr))
		y_te=np.squeeze(np.asarray(y_te))

		return (X_tr, X_te), (y_tr, y_te), headers

def to_int(l):
	return [int(el) for el in l]

def save_results(f, titles, results, distribution_info):
	'''save algorithm results'''
	out = write_csv(f)
	out.writerow([titles[0]] + results[0].tolist()) # false pos rate for ROC
	out.writerow([titles[1]] + results[1].tolist()) # true pos rate for ROC
	out.writerow([titles[2]] + [results[2]]) # AUC value
	out.writerow([titles[3]] + ["", "Pred 0", "Pred 1"]) # confusion matrix line 1
	out.writerow(["", "Actual 0"] + results[3].tolist()[0]) # confusion matrix line 2
	out.writerow(["", "Actual 1"] + results[3].tolist()[1]) # confusion matrix line 3
	out.writerow([''])
	out.writerow(['# CRC cases', '# Instances'])
	out.writerow(distribution_info)



def save_features(f, features):
	'''writes all features to file'''
	out = write_csv(f)
	for feature in sorted(features, key=itemgetter(1), reverse=True):
		out.writerow(feature)

def save_ROC(f, curves, clear=True, random=True, title='ROC Curve'):
	if clear: plt.clf() # clear

	# make picture pretty
	plt.rc('axes', color_cycle=['r', 'g', 'b', 'y', 'c', 'm', 'k'])
	plt.xlim([-0.01, 1.01])
	plt.ylim([-0.01, 1.01])
	plt.xlabel('False Positive Rate')
	plt.ylabel('True Positive Rate')
	plt.title(title)

	# plot results
	if random: plt.plot([0, 1], [0, 1], label='Random')

	mean_x = curves[0][1]
	sum_y = np.zeros(mean_x.shape)
	sum_auc = 0

	for result in curves:
		assert(type(result[1]) == np.ndarray)
		assert(type(result[2]) == np.ndarray)

		sum_y = sum_y + result[2]
		sum_auc = sum_auc + float(result[3])

		plt.plot(result[1], result[2],
			# label=result[0] + ' (AUC = %0.2f)' % result[3], lw=1)
			label=result[0].split('.csv')[0] + ' (%0.2f)' % result[3], lw=1)

	# plt.plot(mean_x, (sum_y/float(len(curves))),
	# 	label='Mean (%0.2f)' % (sum_auc/float(len(curves))), lw=3)

	# add legend
	plt.legend(loc="lower right")

	# save to file
	plt.savefig(f)
