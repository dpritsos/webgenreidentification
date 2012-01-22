"""

"""
import sys
sys.path.append('../../synergeticprocessing/src')
sys.path.append('../../html2vectors/src')
import numpy as np
import tables as tb
import html2tf.tables.cngrams as cng_tb
import html2tf.tables.tbtools as tbtls
from html2tf.dictionaries.tfdtools import TFDictHandler
import sklearn.svm as svm 
import scipy.sparse as sps
from trainevaloneclssvm import SVMTE 


class ResultsTable_desc(tb.IsDescription):
    kfold = tb.UInt32Col(pos=1)
    nu = tb.Float32Col(pos=2)
    feat_num = tb.UInt32Col(pos=3)
    F1 = tb.Float32Col(pos=4)
    P = tb.Float32Col(pos=5)
    R = tb.Float32Col(pos=6)
    Acc = tb.Float32Col(pos=7)
    
class MultiResultsTable_desc(tb.IsDescription):
    kfold = tb.UInt32Col(pos=1)
    C = tb.Float32Col(pos=2)
    feat_num = tb.UInt32Col(pos=3)
    Acc = tb.Float32Col(pos=7)
   

class CSVM_CrossVal(tbtls.TFTablesHandler):
    
    def __init__(self, h5file, h5f_data, h5f_res, corpus_grp, trms_type_grp):
        tbtls.TFTablesHandler.__init__(self, h5file)
        self.h5file = h5file
        self.h5f_data = h5f_data
        self.h5f_res = h5f_res
        self.corpus_grp = corpus_grp
        self.trms_type_grp = trms_type_grp
        self.genres_lst = list()
        self.kfold_chnk = dict()
        self.page_lst_tb = dict()
        self.kfold_mod = dict()
        self.gnr2clss = dict()
        self.e_arr_filters = tb.Filters(complevel=5, complib='zlib')
    
    def complementof_list(self, lst, excld_dwn_lim, excld_up_lim):
        if excld_dwn_lim == 0:
            return lst[excld_up_lim:]
        if excld_up_lim == len(lst):
            return lst[0:excld_dwn_lim]
        inv_lst = np.concatenate((lst[0:excld_dwn_lim], lst[excld_up_lim:]))
        return inv_lst
                    
    def prepare_data(self, kfolds, format):
        corpus = self.h5file.getNode('/', self.corpus_grp)
        self.genres_lst = corpus._v_attrs.genres_lst
        for i, gnr in enumerate(self.genres_lst):
            self.page_lst_tb[gnr] = self.h5file.getNode( self.corpus_grp + self.trms_type_grp + gnr, '/PageListTable' )
            self.kfold_chnk[gnr] = np.divide(len(self.page_lst_tb[gnr]),kfolds)
            self.kfold_mod[gnr] = np.divide(len(self.page_lst_tb[gnr]),kfolds)
            self.gnr2clss[gnr] = i + 1
        
        for k in range(kfolds):
            start = k*self.kfold_chnk[gnr]
            end = (k+1)*self.kfold_chnk[gnr]
            if (k+1) == kfolds:
                end = end + self.kfold_mod[gnr]
            
            training_pg_lst = list()
            training_clss_tag_lst = list()
            crossval_pg_lst = list()
            crossval_clss_tag_lst = list()
            
            for gnr in self.genres_lst:
                page_lst_tb = self.page_lst_tb[gnr].read()
                #Get the Evaluation set for this Genre and later concatenate it to the rest of the Evaluation Genres
                grn_page_lst_tb = page_lst_tb['table_name'][start:end]
                crossval_pg_lst.extend( page_lst_tb['table_name'][start:end] )
                crossval_clss_tag_lst.extend( [self.gnr2clss[gnr]]*len(grn_page_lst_tb) )
                #Get the Training set for this Genre g
                grn_trn_pg_lst = self.complementof_list( page_lst_tb['table_name'], start, end )
                training_pg_lst.extend( grn_trn_pg_lst )
                training_clss_tag_lst.extend( [self.gnr2clss[gnr]]*len(grn_trn_pg_lst) )
            
            print len(crossval_pg_lst)
            print len(crossval_clss_tag_lst), crossval_clss_tag_lst 
            print len(training_pg_lst), 
            print len(training_clss_tag_lst), training_clss_tag_lst 
            
            #Create the Training-set Dictionary - Sorted by frequency
            print "Creating Dictionary - Sorted by Frequency" 
            term_idx_d, kfold_Dictionary_TF_arr = self.TFTables2TFDict_n_TFArr(self.corpus_grp + self.trms_type_grp,\
                                                                               training_pg_lst,\
                                                                               data_type=tbtls.default_TF_3grams_dtype)
            
            #print term_idx_d.items()[0:10]
            #print kfold_Dictionary_TF_arr[0:10] 
            
            DicFreq = self.h5f_data.createTable(self.h5f_data.root, 'kfold_'+str(k)+'_Dictionary_TF_arr', kfold_Dictionary_TF_arr)
            
            print DicFreq[0:10]
            
            ###############From this line and down need to be veryfied that the reasaults are corect!#############
            
            #Create the Training-Set Array
            print "Preparing Training Set"
            training_earr_X = self.h5f_data.createEArray(self.h5f_data.root, 'kfold_'+str(k)+'_Training_X',\
                                                  tb.Float32Atom(), (0,len(term_idx_d)),\
                                                  filters=self.e_arr_filters)
            training_earr_X = self.TFTabels2EArray(training_earr_X, self.corpus_grp + self.trms_type_grp,
                                                 training_pg_lst, term_idx_d,\
                                                 data_type=np.float32)
            training_earr_Y = self.h5f_data.createArray(self.h5f_data.root, 'kfold_'+str(k)+'_Training_Y', np.array(training_clss_tag_lst))
                                                                     
            
            print training_earr_X[0:5, 10:20]
            print np.shape(training_earr_X)
            print training_earr_Y
            
            #Create the CrossVal-Set Array
            print "Preparing Cross-Validation Set"
            crossval_earr_X = self.h5f_data.createEArray(self.h5f_data.root, 'kfold_'+str(k)+'_CrossVal_X',\
                                                  tb.Float32Atom(), (0,len(term_idx_d)),\
                                                  filters=self.e_arr_filters)
            crossval_earr_X = self.TFTabels2EArray(crossval_earr_X, self.corpus_grp + self.trms_type_grp,
                                                 crossval_pg_lst, term_idx_d,\
                                                 data_type=np.float32)       
            crosval_earr_Y = self.h5f_data.createArray(self.h5f_data.root, 'kfold_'+str(k)+'_CrossVal_Y', np.array(crossval_clss_tag_lst))
            
            print crossval_earr_X[0:5, 10:20]
            print np.shape(crossval_earr_X)
            print crosval_earr_Y
            
            
    def evaluate(self, kfolds, C_lst, featr_size_lst):
        
        #Create Results table for all this CrossValidation Multi-class SVM
        print "Create Results table for all this CrossValidation Multi-class SVM"
        self.h5f_res.createTable(self.h5f_res.root, "MultiClass_CrossVal",  MultiResultsTable_desc)
        
        for k in range(kfolds):
            #Get the Training-set Dictionary - Sorted by frequency for THIS-FOLD
            print "Get Dictionary - Sorted by Frequency for this kfold:", k
            kfold_Dictionary_TF_arr = self.h5f_data.getNode(self.h5f_data.root, 'kfold_'+str(k)+'_Dictionary_TF_arr')
            
            #Get Training-set for kFold
            print "Get Training Data Array for kfold:", k
            training_earr_X = self.h5f_data.getNode(self.h5f_data.root, 'kfold_'+str(k)+'_Training_X')
            training_earr_Y = self.h5f_data.getNode(self.h5f_data.root, 'kfold_'+str(k)+'_Training_Y')
            
            #Get the Evaluation-set for kfold
            print "Get Evaluation Data Array for kfold:", k
            crossval_earr_X = self.h5f_data.getNode(self.h5f_data.root, 'kfold_'+str(k)+'_CrossVal_X')
            crossval_earr_Y = self.h5f_data.getNode(self.h5f_data.root, 'kfold_'+str(k)+'_CrossVal_Y')
            
            #Get Results table for all this CrossValidation Multi-class SVM
            print "Get Results table for all this CrossValidation Multi-class SVM"
            res_table = self.h5f_res.getNode(self.h5f_res.root, "MultiClass_CrossVal")
            
            for featrs_size in featr_size_lst: 
                ##### FIND MORE OPTICAML USE IF POSIBLE
                #Keep the amount of feature required - it will keep_at_least as many as
                feat_len = np.max(np.where(  kfold_Dictionary_TF_arr.read()['freq'] == kfold_Dictionary_TF_arr.read()['freq'][featrs_size] )[0])
                #the featrs_size keeping all the terms with same frequency the last term satisfies the featrs_size
                print "Features Size:", feat_len      
                for c in C_lst:
                    csvm = svm.SVC(C=c, kernel='linear')
                    print "FIT model"
                    #train_X = training_earr_X[:, 0:feat_len] 
                    train_Y = training_earr_Y[:]
                    train_X = np.where( training_earr_X[:, 0:feat_len] > 0, training_earr_X[:, 0:feat_len], 0)
                    train_X[ np.nonzero(train_X) ] = 1
                    print train_X  
                    csvm.fit(train_X, train_Y) 
                    print "Predict for kfold:k",k
                    #crossval_X = crossval_earr_X[:, 0:feat_len] 
                    crossval_Y = crossval_earr_Y[:]
                    crossval_X = np.where( crossval_earr_X[:, 0:feat_len] > 0, crossval_earr_X[:, 0:feat_len], 0)
                    crossval_X[ np.nonzero(crossval_X) ] = 1  
                    res_acc_score = csvm.score(crossval_X, crossval_Y)
                    
                    print "Accuracy:", res_acc_score 
                    res_table.row['kfold'] = k
                    res_table.row['C'] = c
                    res_table.row['feat_num'] = feat_len
                    res_table.row['Acc'] = res_acc_score
                    res_table.row.append()
            res_table.flush()
            
    def exec_test(self):
        self.prepare_data(10, None)
        #self.evaluate(10, [1], [30000])
        
        

class OCSVM_CrossVal(tbtls.TFTablesHandler):
    
    def __init__(self, h5file, h5f_data, h5f_res, corpus_grp, trms_type_grp):
        tbtls.TFTablesHandler.__init__(self, h5file)
        self.h5file = h5file
        self.h5f_data = h5f_data
        self.h5f_res = h5f_res
        self.corpus_grp = corpus_grp
        self.trms_type_grp = trms_type_grp
        self.genres_lst = list()
        self.kfold_chnk = dict()
        self.page_lst_tb = dict()
        self.kfold_mod = dict()
        self.gnr2clss = dict()
        self.e_arr_filters = tb.Filters(complevel=5, complib='zlib')
        self.ocsvm_gnr_end_bound_dct = dict() 
    
    def complementof_list(self, lst, excld_dwn_lim, excld_up_lim):
        if excld_dwn_lim == 0:
            return lst[excld_up_lim:]
        if excld_up_lim == len(lst):
            return lst[0:excld_dwn_lim]
        inv_lst = np.concatenate((lst[0:excld_dwn_lim], lst[excld_up_lim:]))
        return inv_lst
                    
    def prepare_data(self, kfolds, format):
        corpus = self.h5file.getNode('/', self.corpus_grp)
        self.genres_lst = corpus._v_attrs.genres_lst
        for i, gnr in enumerate(self.genres_lst):
            self.page_lst_tb[gnr] = self.h5file.getNode( self.corpus_grp + self.trms_type_grp + gnr, '/PageListTable' )
            self.kfold_chnk[gnr] = np.divide(len(self.page_lst_tb[gnr]),kfolds)
            self.kfold_mod[gnr] = np.divide(len(self.page_lst_tb[gnr]),kfolds)
            self.gnr2clss[gnr] = i + 1
        
        for k in range(kfolds):
            start = k*self.kfold_chnk[gnr]
            end = (k+1)*self.kfold_chnk[gnr]
            if (k+1) == kfolds:
                end = end + self.kfold_mod[gnr]
            
            training_pg_lst = list()
            training_clss_tag_lst = list()
            crossval_pg_lst = list()
            crossval_clss_tag_lst = list()
            
            for g in self.gerens_lst:
                page_lst_tb = self.page_lst_tb[g].read()
                #Get the Training set for this Genre g
                grn_trn_pg_lst = self.complementof_list( page_lst_tb['table_name'], start, end )
                training_pg_lst.extend( grn_trn_pg_lst )
                training_clss_tag_lst.extend( [self.gnr2clss[g]]*len(grn_trn_pg_lst) )
                #Get the Evaluation set for this Genre and later concatenate it to the rest of the Evaluation Genres
                grn_page_lst_tb = page_lst_tb['table_name'][start:end]
                crossval_pg_lst.extend( page_lst_tb['table_name'][start:end] )
                crossval_clss_tag_lst.extend( [self.gnr2clss[g]]*len(grn_page_lst_tb) )
                self.ocsvm_gnr_end_bound_dct[g] = end
                for gnr in self.genres_lst:
                    if gnr != g:
                        page_lst_tb = self.page_lst_tb[gnr].read()
                        grn_page_lst_tb = page_lst_tb['table_name'][:]
                        crossval_pg_lst.extend( page_lst_tb['table_name'][:] )
                        crossval_clss_tag_lst.extend( [self.gnr2clss[gnr]]*len(grn_page_lst_tb) )
                    
                print len(crossval_pg_lst)
                print len(crossval_clss_tag_lst), crossval_clss_tag_lst 
                print len(training_pg_lst), 
                print len(training_clss_tag_lst), training_clss_tag_lst 
                
                #Create the Training-set Dictionary - Sorted by frequency
                print "Creating Dictionary - Sorted by Frequency - for ", g 
                term_idx_d, kfold_Dictionary_TF_arr = self.TFTables2TFDict_n_TFArr(self.corpus_grp + self.trms_type_grp,\
                                                                                   training_pg_lst,\
                                                                                   data_type=tbtls.default_TF_3grams_dtype)
                
                #print term_idx_d.items()[0:10]
                #print kfold_Dictionary_TF_arr[0:10] 
                
                DicFreq = self.h5f_data.createTable(self.h5f_data.root, g+'_kfold_'+str(k)+'_Dictionary_TF_arr', kfold_Dictionary_TF_arr)
                
                print DicFreq[0:10]
                
                ###############From this line and down need to be veryfied that the reasaults are corect!#############
                
                #Create the Training-Set Array
                print "Preparing Training Set for", g
                training_earr_X = self.h5f_data.createEArray(self.h5f_data.root, g+'_kfold_'+str(k)+'_Training_X',\
                                                      tb.Float32Atom(), (0,len(term_idx_d)),\
                                                      filters=self.e_arr_filters)
                training_earr_X = self.TFTabels2EArray(training_earr_X, self.corpus_grp + self.trms_type_grp,
                                                     training_pg_lst, term_idx_d,\
                                                     data_type=np.float32)
                training_earr_Y = self.h5f_data.createArray(self.h5f_data.root, g+'_kfold_'+str(k)+'_Training_Y', np.array(training_clss_tag_lst))
                                                                         
                
                print training_earr_X[0:5, 10:20]
                print np.shape(training_earr_X)
                print training_earr_Y
                
                #Create the CrossVal-Set Array
                print "Preparing Cross-Validation Set for", g
                crossval_earr_X = self.h5f_data.createEArray(self.h5f_data.root, g+'_kfold_'+str(k)+'_CrossVal_X',\
                                                      tb.Float32Atom(), (0,len(term_idx_d)),\
                                                      filters=self.e_arr_filters)
                crossval_earr_X = self.TFTabels2EArray(crossval_earr_X, self.corpus_grp + self.trms_type_grp,
                                                     crossval_pg_lst, term_idx_d,\
                                                     data_type=np.float32)       
                crosval_earr_Y = self.h5f_data.createArray(self.h5f_data.root, g+'_kfold_'+str(k)+'_CrossVal_Y', np.array(crossval_clss_tag_lst))
                
                print crossval_earr_X[0:5, 10:20]
                print np.shape(crossval_earr_X)
                print crosval_earr_Y
                
            
    def evaluate(self, kfolds, nu_lst, featr_size_lst):
        
        for g in self.gerens_lst:
            #Create Results table for all this CrossValidation Multi-class SVM
            print "Create Results table for all this CrossValidation Multi-class SVM for genre:", g
            self.h5f_res.createTable(self.h5f_res.root, g+"_MultiClass_CrossVal",  MultiResultsTable_desc)
            
            for k in range(kfolds):
                #Get the Training-set Dictionary - Sorted by frequency for THIS-FOLD
                print "Get Dictionary - Sorted by Frequency for this kfold:", k
                kfold_Dictionary_TF_arr = self.h5f_data.getNode(self.h5f_data.root, g+'+kfold_'+str(k)+'_Dictionary_TF_arr')
                
                #Get Training-set for kFold
                print "Get Training Data Array for kfold & genre:", k, g
                training_earr_X = self.h5f_data.getNode(self.h5f_data.root, g+'_kfold_'+str(k)+'_Training_X')
                training_earr_Y = self.h5f_data.getNode(self.h5f_data.root, g+'_kfold_'+str(k)+'_Training_Y')
                
                #Get the Evaluation-set for kfold
                print "Get Evaluation Data Array for kfold & genre:", k, g
                crossval_earr_X = self.h5f_data.getNode(self.h5f_data.root, g+'_kfold_'+str(k)+'_CrossVal_X')
                crossval_earr_Y = self.h5f_data.getNode(self.h5f_data.root, g+'_kfold_'+str(k)+'_CrossVal_Y')
                
                #Get Results table for all this CrossValidation Multi-class SVM
                print "Get Results table for all this CrossValidation Multi-class SVM and gerne:", g
                res_table = self.h5f_res.getNode(self.h5f_res.root, g+'_MultiClass_CrossVal')
                
                for featrs_size in featr_size_lst: 
                    ##### FIND MORE OPTICAML USE IF POSIBLE
                    #Keep the amount of feature required - it will keep_at_least as many as
                    feat_len = np.max(np.where(  kfold_Dictionary_TF_arr.read()['freq'] == kfold_Dictionary_TF_arr.read()['freq'][featrs_size] )[0])
                    #the featrs_size keeping all the terms with same frequency the last term satisfies the featrs_size
                    print "Features Size:", feat_len      
                    for n in nu_lst:
                        ocsvm = svm.OneClassSVM(nu=n, kernel='linear')
                        print "FIT model"
                        #train_X = training_earr_X[:, 0:feat_len] 
                        ## No Required for this implementation train_Y = training_earr_Y[:]
                        train_X = np.where( training_earr_X[:, 0:feat_len] > 0, training_earr_X[:, 0:feat_len], 0)
                        train_X[ np.nonzero(train_X) ] = 1
                        print train_X  
                        ocsvm.fit(train_X) 
                        print "Predict for kfold:k",k
                        #crossval_X = crossval_earr_X[:, 0:feat_len] 
                        ## No Required for this implementation crossval_Y = crossval_earr_Y[:]
                        crossval_X = np.where( crossval_earr_X[:, 0:feat_len] > 0, crossval_earr_X[:, 0:feat_len], 0)
                        crossval_X[ np.nonzero(crossval_X) ] = 1
                        self.ocsvm_gnr_end_bound_dct[g]
                        res = ocsvm.predict(crossval_X[0:self.ocsvm_gnr_end_bound_dct[g]])
                        tp = len( np.where( res == 1 )[0] )
                        fn = len( np.where( res == -1 )[0] )
                        
                        res = ocsvm.predict(crossval_X[self.ocsvm_gnr_end_bound_dct[g]::])
                        tn = len( np.where( res == -1 )[0] ) 
                        fp = len( np.where( res == 1 )[0] )
                                                
                        if (tp + fp) != 0.0:
                            P = np.float(tp) / np.float( tp + fp )
                        else:
                            P = 0.0
                        if (tp + fn) != 0.0:
                            R = np.float(tp) / np.float( tp + fn )
                        else:
                            R = 0.0
                        if (P + R) != 0.0:
                            F1 = np.float( 2 * P * R ) / np.float( P + R )
                        else:
                            F1 = 0.0
                        if (tp + tn + fp + fn) !=0:
                            Acc = np.float(tp + tn) / np.float(tp + tn + fp + fn)
                        else:
                            Acc = 0.0
                        print tn, fn, tn, fp, F1, P, R, Acc
                        res_table.row['kfold'] = k
                        res_table.row['nu'] = nu
                        res_table.row['feat_num'] = feat_len
                        res_table.row['F1'] = F1
                        res_table.row['P'] = P
                        res_table.row['R'] = R
                        res_table.row['Acc'] = Acc
                        res_table.row.append()  
                        
                res_table.flush()
            
    def exec_test(self):
        self.prepare_data(10, None)
        #self.evaluate(10, [1], [30000])


if __name__=='__main__':
    
    exp = SVMExperiments_with_tables()
    kfolds = 10
    nu_lst = [0.2, 0.8]
    featr_size_lst = [1000]
    #crp_tftb_h5 = tb.openFile('/home/dimitrios/Synergy-Crawler/Santinis_7-web_genre/Santini_corpus.h5', 'r')
    crp_tftb_h5 = tb.openFile('/home/dimitrios/Synergy-Crawler/Automated_Crawled_Corpus/ACC.h5', 'r')
    #crp_crssvl_data = tb.openFile('/home/dimitrios/Synergy-Crawler/Santinis_7-web_genre/CSVM_CrossVal_Data.h5', 'w')
    crp_crssvl_data = tb.openFile('/home/dimitrios/Synergy-Crawler/Automated_Crawled_Corpus/CSVM_CrossVal_Data.h5', 'w')
    #crp_crssvl_res = tb.openFile('/home/dimitrios/Synergy-Crawler/Santinis_7-web_genre/CSVM_CrossVal_Results.h5', 'w')
    crp_crssvl_res = tb.openFile('/home/dimitrios/Synergy-Crawler/Automated_Crawled_Corpus/CSVM_CrossVal_Results.h5', 'w')
    #genres = [ "blog", "eshop", "faq", "frontpage", "listing", "php", "spage"]
    
    csvm_crossval = CSVM_CrossVal(crp_tftb_h5, crp_crssvl_data, crp_crssvl_res, "/Automated_Crawled_Corpus", "/trigrams/")
    csvm_crossval.exec_test()
    
    crp_tftb_h5.close() 
    crp_crssvl_data.close()
    crp_crssvl_res.close()

    
    
    
    
    
    
    
    
    
    
    

