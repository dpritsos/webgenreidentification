"""

"""
import os
from vectorhandlingtools import *
import sys
sys.path.append('../../synergeticprocessing/src')
from synergeticpool import *
from experiments import *

#pool = SynergeticPool( { '192.168.1.68':(40000,'123456') }, local_workers=1, syn_listener_port=41000 )
#pool = SynergeticPool( { '192.168.1.68':(40000,'123456'), '192.168.1.65':(40000,'123456') }, local_workers=1, syn_listener_port=41000 ) 
pool = SynergeticPool( local_workers=1, syn_listener_port=41000 )
print "Registering"
#pool.register_mod( [ 'basicfiletools', 'vectorhandlingtools', 'trainevaloneclssvm', 'experiments'] )  
print "Regitered OK"
exp = SVMExperiments()

#genres = [  "wiki_pages", "product_companies", "forum", "blogs", "news" ] #academic , "forum",   
#genres = [ "blog", "eshop", "faq", "frontpage", "listing", "php", "spage"] 
genres = [ "article", "discussion", "download", "help", "linklist", "portrait", "shop"] 
#base_filepath = ["/home/dimitrios/Synergy-Crawler/saved_pages/", "../Synergy-Crawler/saved_pages/"]
#base_filepath = ["/home/dimitrios/Synergy-Crawler/Santini_corpus/", "../Synergy-Crawler/Santini_corpus/"]
base_filepath = ["/home/dimitrios/Synergy-Crawler/KI-04/", "../Synergy-Crawler/KI-04/"] 
train_tf_d = "/train_tf_dictionaries/"
train_tf_vectors = "/train_tf_vectors/"
test_tf_d = "/test_tf_dictionaries/"
test_tf_vectors = "/test_tf_vectors/"
##
train_nf_d = "/train_nf_dictionaries/"
train_nf_vectors = "/train_nf_vectors/"
test_nf_d = "/train_nf_dictionaries/"
test_nf_vectors = "/test_nf_vectors/"


exps_report = list()
#for g in genres:
#    exps_report.append( pool.dispatch(exp.tf_experiment_set1, base_filepath, train_tf_vectors, 140, test_tf_vectors, 49, g, genres, lower_case=True) )
#    print("Experiment %s VS All: Dispatched" % g)

#Simple OC-SVM with specific Experimental Variable Attributes
#nu_l = [0.07, 0.07, 0.07, 0.05, 0.05] #[0.05, 0.07, 0.05, 0.05, 0.05 ] 
#featr_l = [40, 160, 40, 70, 10] #[10, 10, 40, 10, 40 ]
#vect_format = 2
#for g, nu, featrs in zip(genres, nu_l, featr_l):
#    exps_report.append( pool.dispatch(exp.exprmt_ocsvm, nu, featrs, vect_format, base_filepath, train_nf_vectors, 2500, test_nf_vectors, 500, g, genres, lower_case=True) )
#    print("Experiment %s VS All: Dispatched" % g)


keep_term_lst = range(10, 720, 50)
for g in genres:
    exps_report.append( pool.dispatch(exp.exprmt_feature_len_variation, keep_term_lst, base_filepath, train_tf_vectors, 65, test_tf_vectors, 50, g, genres, lower_case=True) )
    print("Experiment %s VS All: Dispatched" % g)

#keep_term_lst = range(10, 670, 30)
#nu_lst = [0.05, 0.07, 0.1, 0.15, 0.2, 0.3, 0.5, 0.7, 0.8]
#kfolds_l = [37, 30, 19, 10, 41]
#resdualz_l = [21, 10, 30, 0, 40]
#for i, g in enumerate(genres):
#    exps_report.append( pool.dispatch(exp.kfold_corss_v_featr_nu, kfolds_l[i], keep_term_lst, base_filepath, train_tf_vectors, 2500 - resdualz_l[i], nu_lst, g, lower_case=True) )
#    print("Experiment %s VS All: Dispatched" % g)
    
#for g in genres:
#    exps_report.append( pool.dispatch(exp.tf_experiment_set4, base_filepath, train_tf_vectors, 2500, test_tf_vectors, 800, g, genres, freq_init=5, freq_lim=200, freq_step=10,lower_case=True, keep_terms=None) )
#    print("Experiment %s VS All: Dispatched" % g)

#keep_term_lst = range(500, 63000, 1500)
#c_lst = [1, 2, 5, 10, 50]
#kfolds = 10
#exps_report.append( pool.dispatch(exp.kfold_corss_multiclass, kfolds, keep_term_lst, c_lst, base_filepath, train_nf_vectors, 0, test_nf_vectors, 0, genres, lower_case=True) )
#print("Experiment k-fold Cross-Validation Multi-Class SVM Dispatched")

#keep_term_lst = [500, 2500, 5000, 60000] #range(500, 63000, 1500)
#c_lst = [2, 10]
#exps_report.append( pool.dispatch(exp.svm_multiclass_featrs, keep_term_lst, base_filepath, train_nf_vectors, 1000, test_nf_vectors, 500, c_lst, genres, lower_case=True ) )
##exps_report.append( pool.dispatch(exp.tf_experiment_set2, base_filepath, train_tf_vectors, 1000, test_tf_vectors, 500, genres, lower_case=True) )
#print("Experiment Multi-Class SVM Dispatched")

for exp_rep in exps_report:
    print exp_rep.value    

pool.join_all()

print "Thank you and Goodbye!"

