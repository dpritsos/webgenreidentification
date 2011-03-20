"""

"""
import os
from generatevectors import HTML2TF, HTML2NF
import sys
sys.path.append('../../synergeticprocessing/src')
from synergeticpool import SynergeticPool

#pool = SynergeticPool( { '192.168.1.65':(40000,'123456'), '192.168.1.68':(40000,'123456') }, local_workers=1, syn_listener_port=41000 ) 
pool = SynergeticPool( local_workers=1, syn_listener_port=41000 )
print "Registering"
#pool.register_mod( ['html2vector', 'vectorhandlingtools', 'generatevectors'] )  
print "Regitered OK"

#genres = [ "blogs", "news", "wiki_pages", "product_companies", "forum" ] #academic ,  
#genres = [ "blog", "eshop", "faq", "frontpage", "listing", "php", "spage"]
genres = [ "article", "discussion", "download", "help", "linklist", "portrait", "shop"] 
#base_filepath = ["/home/dimitrios/Documents/Synergy-Crawler/saved_pages", "../Documents/Synergy-Crawler/saved_pages"]
#base_filepath = ["/home/dimitrios/Documents/Synergy-Crawler/Santini_corpus", "../Documents/Synergy-Crawler/Santini_corpus"]
base_filepath = ["/home/dimitrios/Documents/Synergy-Crawler/KI-04", "../Documents/Synergy-Crawler/KI-04"]  

html2tf = HTML2TF()
html2nf = HTML2NF(n=3)

#if filepath and not os.path.isdir((filepath + "corpus_dictionaries/")):
#    os.mkdir((filepath + "corpus_dictionaries/"))
          
resaults = list()
for g in genres:
    #Training Vectors file paths
    train_filepath = str( "/" + g + "/html_pages/")
    train_tfv_file = str( "/" + g + "/train_tf_vectors/" + g + ".tfvl" )
    train_tfd_file = str( "/" + g + "/train_tf_dictionaries/" + g + ".tfd" )
    train_err_file = str( "/" + g + "/" + g + ".train.lst.err")
    #Testing Vectors file paths
    test_filepath = str( "/" + g + "/test_only_html_pages/")
    test_tfv_file = str( "/" + g + "/test_tf_vectors/" + g + ".tfvl" )
    test_tfd_file = str( "/" + g + "/test_tf_dictionaries/" + g + ".tfd" )
    test_err_file = str( "/" + g + "/" + g + ".test.lst.err")
    resaults.append( pool.dispatch(\
    html2tf.html2tfv_n_tfd, base_filepath, train_filepath, train_tfv_file, train_tfd_file, train_err_file, load_encoding='ascii', save_encoding='utf-8', error_handling='replace', low_mem='True' \
                     ) )
    resaults.append( pool.dispatch(\
    html2tf.html2tfv_n_tfd, base_filepath, test_filepath, test_tfv_file, test_tfd_file, test_err_file, load_encoding='ascii', save_encoding='utf-8', error_handling='replace', low_mem='True' \
                     ) )
    
for res in resaults:
    print res.value

for g in genres:
    #Training Vectors file paths
    train_filepath = str( "/" + g + "/html_pages/")
    train_tfv_file = str( "/" + g + "/train_nf_vectors/" + g + ".nfvl" )
    train_tfd_file = str( "/" + g + "/train_nf_dictionaries/" + g + ".nfd" )
    train_err_file = str( "/" + g + "/" + g + ".train.lst.err")
    #Testing Vectors file paths
    test_filepath = str( "/" + g + "/test_only_html_pages/")
    test_tfv_file = str( "/" + g + "/test_nf_vectors/" + g + ".nfvl" )
    test_tfd_file = str( "/" + g + "/test_nf_dictionaries/" + g + ".nfd" )
    test_err_file = str( "/" + g + "/" + g + ".test.lst.err")
    resaults.append( pool.dispatch(\
    html2nf.html2nfv_n_nfd, base_filepath, train_filepath, train_tfv_file, train_tfd_file, train_err_file, load_encoding='ascii', save_encoding='utf-8', error_handling='replace', low_mem='True' \
                     ) )
    resaults.append( pool.dispatch(\
    html2nf.html2nfv_n_nfd, base_filepath, test_filepath, test_tfv_file, test_tfd_file, test_err_file, load_encoding='ascii', save_encoding='utf-8', error_handling='replace', low_mem='True' \
                     ) )
       
for res in resaults:
    print res.value


pool.join_all()

print "Thank you and Goodbye!"

