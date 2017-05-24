import json, os
import warnings
import numpy as np
import sys
from matplotlib import pyplot as plt
from sklearn import svm
from sklearn import preprocessing
from sklearn.neural_network import MLPClassifier
from sklearn.externals import joblib
from sample import Sample

warnings.filterwarnings("ignore", category=DeprecationWarning)

class Data:
    """Common class for a list of instances of the class Samples

    Attributes:
        name: name of the data as a string
        samples: a list of samples as instances of class Sample
        casedisgene: a list of lists [[case,gene]] containing each case in samples and the respective disease causing gene
    """


    def __init__(self, samples=[], casedisgene=[]):
        #self.name = name
        self.samples = list(samples)
        self.casedisgene = casedisgene


    def load(self, path):
        """ loads the samples attribute with the information of the json files in the same directory as instances of the class Samples"""
        print('loading data')
        for file_name in os.listdir(path):
            if file_name.endswith(".json") and file_name != '34159.json' and file_name != '40536.json':
                file_name = os.path.join(path, file_name)
                vectors = {}
                with open(file_name, encoding='utf-8', errors='ignore') as json_data:
                    data = json.load(json_data)
                    pathogene = '?'
                    #gene_omimID='?'
                    if len(data['genomicData']) > 0:
                        if 'Gene Name' in data['genomicData'][0]['Test Information']:
                            pathogene = data['genomicData'][0]['Test Information']['Gene Name']
                            if pathogene == 'MLL2':
                                pathogene = 'KMT2D'
                            elif pathogene == 'MLL':
                                pathogene = 'KMT2A'
                            elif pathogene == 'B3GALTL':
                                pathogene = 'B3GLTC'
                            elif pathogene == 'CASKIN1':
                                pathogene = 'KIAA1306'
                            #gene_omimID=data['genomicData'][0]['Test Information']['Gene Name']
                    case = data['case_id']
                    for entry in data['geneList']:
                        gscore = 0    # gestalt score
                        if 'gestalt_score' in entry:# and entry['gestalt_score']>0: #sometimes negative; mistake by FDNA?
                            gscore = entry['gestalt_score']
                        fscore = 0    # feature score
                        if 'feature_score' in entry:    # and entry['feature_score']>0:  #sometimes negative; mistake by FDNA?
                            fscore = entry['feature_score']
                        vscore = 0 # variant score
                        if 'cadd_phred_score' in entry:
                            vscore = entry['cadd_phred_score']
                        pscore = 0 # phenomizer score
                        if 'pheno_score' in entry:
                            pscore = entry['pheno_score']
                        bscore=0 # boqa score
                        if 'boqa_score' in entry:
                            bscore = entry['boqa_score']
                        gene = entry['gene_symbol']
                        patho = 0 # pathogenicity, will serve as class label, 1 is pathogenic mutation; 0 is neutral variant
                        if gene == pathogene:
                            patho = 1
                        if pathogene != '?': # and (gscore!=0 or fscore!=0 or vscore!=0 or pscore!=0 or bscore!=0): #nullvectors not allowed
                            if case + gene in vectors: # if a gene appears several times in the gene List of a case onnly its highest values will be assigned to its Sample
                                smpl = vectors[case + gene]
                                if gscore > smpl.gestalt:
                                    smpl.gestalt = gscore
                                if fscore > smpl.feature:
                                    smpl.feature = fscore
                                if vscore > smpl.cadd_phred:
                                    smpl.cadd_phred = vscore
                                if pscore > smpl.phenomizer:
                                    smpl.phenomizer = pscore
                                if bscore > smpl.boqa:
                                    smpl.boqa = bscore
                            if case + gene not in vectors:
                                vectors[case+gene] = Sample(case = case, gene = gene, gestalt = gscore, feature = fscore, cadd_phred = vscore, phenomizer = pscore, boqa = bscore, pathogenicity = patho)
                for vector in vectors:
                    self.samples.append(vectors[vector])    # loads samples with instances of the class Sample
        casedisgene = []
        cases = []
        for smpl in self.samples:
            if smpl.pathogenicity == 1:
                casedisgene.append([smpl.case, smpl.gene])
                cases.append(smpl.case)
        for smpl in self.samples:
            if smpl.case not in cases:
                cases.append(smpl.case)
                casedisgene.append([smpl.case, 'healthy?'])
        self.casedisgene = casedisgene

    def load2(self, path):
        """ loads the samples attribute with the information of the json files in the same directory as instances of the class Samples"""
        print('loading data')
        for file_name in os.listdir():
            if file_name.endswith(".json") and file_name != '34159.json' and file_name != '40536.json':
                file_name = os.path.join(path, file_name)
                vectors = {}
                with open(file_name, encoding='utf-8', errors='ignore') as json_data:
                    data = json.load(json_data)
                    pathogene = '?'
                    # gene_omimID='?'
                    if len(data['genomicData']) > 0:
                        if 'Gene Name' in data['genomicData'][0]['Test Information']:
                            pathogene = data['genomicData'][0]['Test Information']['Gene Name']
                            if pathogene == 'MLL2':
                                pathogene = 'KMT2D'
                            elif pathogene == 'MLL':
                                pathogene = 'KMT2A'
                            elif pathogene == 'B3GALTL':
                                pathogene = 'B3GLTC'
                            elif pathogene == 'CASKIN1':
                                pathogene = 'KIAA1306'
                            #gene_omimID=data['genomicData'][0]['Test Information']['Gene Name']
                    case = data['case_id']
                    for entry in data['geneList']:
                        if 'feature_score' in entry or 'pheno_score' in entry or 'boqa_score' in entry or 'cadd_phred_score' in entry :
                            gscore = 0    # gestalt score
    #                        if 'gestalt_score' in entry:# and entry['gestalt_score']>0: #sometimes negative; mistake by FDNA?
    #                            gscore=entry['gestalt_score']
                            fscore = 0 #feature score
                            if 'feature_score' in entry:#  and entry['feature_score']>0:  #sometimes negative; mistake by FDNA?
                                fscore = entry['feature_score']
                            vscore = 0 #variant score
                            if 'cadd_phred_score' in entry:
                                vscore = entry['cadd_phred_score']
                            pscore = 0 #phenomizer score
                            if 'pheno_score' in entry:
                                pscore = entry['pheno_score']
                            bscore = 0 #boqa score
                            if 'boqa_score' in entry:
                                bscore = entry['boqa_score']
                            gene = entry['gene_symbol']
                            patho = 0 #pathogenicity, will serve as class label, 1 is pathogenic mutation; 0 is neutral variant
                            if gene == pathogene:
                                patho = 1
                            if pathogene != '?':# and (gscore!=0 or fscore!=0 or vscore!=0 or pscore!=0 or bscore!=0): #nullvectors not allowed
                                if case+gene in vectors: # if a gene appears several times in the gene List of a case onnly its highest values will be assigned to its Sample
                                    smpl=vectors[case + gene]
                                    if gscore > smpl.gestalt:
                                        smpl.gestalt = gscore
                                    if fscore > smpl.feature:
                                        smpl.feature = fscore
                                    if vscore > smpl.cadd_phred:
                                        smpl.cadd_phred = vscore
                                    if pscore > smpl.phenomizer:
                                        smpl.phenomizer = pscore
                                    if bscore > smpl.boqa:
                                        smpl.boqa = bscore
                                if case + gene not in vectors:
                                    vectors[case + gene] = Sample(case = case, gene = gene, gestalt = gscore, feature = fscore, cadd_phred = vscore, phenomizer = pscore, boqa = bscore, pathogenicity = patho)
                for vector in vectors:
                    self.samples.append(vectors[vector]) #loads samples with instances ofthe class Sample
        casedisgene = []
        cases = []
        for smpl in self.samples:
            if smpl.pathogenicity == 1:
                casedisgene.append([smpl.case, smpl.gene])
                cases.append(smpl.case)
        for smpl in self.samples:
            if smpl.case not in cases:
                cases.append(smpl.case)
                casedisgene.append([smpl.case, 'healthy?'])
        self.casedisgene = casedisgene

    def filter_gestalt(self):
        new_samples = []
        for smpl in self.samples:
            if smpl.feature != 0 or smpl.cadd_phred != 0 or smpl.phenomizer != 0 or smpl.boqa != 0:
                new_samples.append(smpl)
        self.samples = new_samples

    def filter_cadd(self):
        new_samples = []
        for smpl in self.samples:
            if smpl.feature != 0 or smpl.gestalt != 0 or smpl.phenomizer != 0 or smpl.boqa != 0:
                new_samples.append(smpl)
        self.samples = new_samples

    def filter_cadd_gestalt(self):
        new_samples=[]
        for smpl in self.samples:
            if smpl.feature!=0 or smpl.phenomizer!=0 or smpl.boqa!=0:
                new_samples.append(smpl)
        self.samples = new_samples

    def threshold(self, value, score='gestalt'):
        for smpl in self.samples:
            if getattr(smpl, score)<value:
                setattr(smpl, score, 0)



    def numhit(self, num):
        """ filters self.samples for only those samples that have num scores featuring
        values higher than 0, self.samples will be adjusted accordingly"""

        newsamples = []
        for smpl in self.samples:
            num_scores = 0
            if smpl.gestalt != 0:
                num_scores += 1
            if smpl.feature != 0:
                num_scores += 1
            if smpl.cadd_phred > 0:
                num_scores += 1
            if smpl.phenomizer > 0:
                num_scores += 1
            if smpl.boqa > 0:
                num_scores += 1
            if num_scores >= num:
                newsamples.append(smpl)
        self.samples = []
        self.samples = newsamples

    def bucketize_data(self):
        """A function to prepare 10x cross validation

        It returns a list of len 10. each list (bucket) will contain case IDs. All case
        IDs featuring a pathogenic mutation in the same gene will be in the same bucket.
        The size of the buckets will be as similar as possible
        """

        print('creating 10 buckets - same gene same bucket')
        self.casedisgene.sort()
        buckets = []
        for i in range(10):
            buckets.append([])
        allgenes = []    # a list that will contain the names of all genes that have a pathogenic entry in allscores
        numgenes = []    # a list that will contain the frequencies by which these genes are pathogentically altered in the data, the indices are corresponding with allgenes
        for entry in self.casedisgene:
            case = entry[0]
            gene = entry[1]
            # if a gene is not yet assigned to allgenes, an entry will be created, at it
            # will get the frequency 1 in numgenes
            if gene not in allgenes:
                allgenes.append(gene)
                numgenes.append(1)
            elif gene in allgenes:    #if a gene is in allgenes already...
                x = 0    # index of that gene
                for i in allgenes:
                    if i == gene:
                        # ...its index in mungenes will be determined and this index will be
                        # increased by 1 (frequency + 1)
                        numgenes[x] += 1
                    x += 1

        for gene in allgenes:
            # minbucket is the minimal number of IDs in a bucket its initial size is the number
            # of cases in the data divideb by 10 plus 2
            minbucket = len(self.casedisgene) / 10 + 2
            for bucket in buckets:
                minbucket = min(len(bucket),minbucket) #minbucket is adjusted to the length of the smallest bucket
            for bucket in buckets:
                if len(bucket) == minbucket: #(one of) the smallest bucket(s) is selected
                    for entry in self.casedisgene:
                        case = entry[0]
                        dgene = entry[1]
                        if dgene == gene:
                            bucket.append(case) #all the case IDs with a pathogenic mutation in a certain gene are added to this bucket
                    break
        #print(buckets)
        return buckets

    def classify_10xSVM(self, C=1):
        """ a 10x validation SVM classification of all samples in the instance of Data. The samples' pedia
        atrribute will be adjusted accordingly. """
        buckets = self.bucketize_data()
        print('10 x cross validation')
        bn = 1    #bucket number

        # 10x cross validation, data will be split according to the ID entries in each bucket,
        # that were created by bucketize_data()
        for bucket in buckets:
            print('computing results for bucket ' + str(bn))
            X = []
            y = []
            for smpl in self.samples:
                # only the data will be used for training that are of cases that are NOT in the topical bucket
                if smpl.case not in bucket:
                    X.append([smpl.gestalt, smpl.feature, smpl.cadd_phred,smpl.phenomizer, smpl.boqa])    #feature vector
                    y.append(smpl.pathogenicity)    #class labels

            X = np.array(X)    #the clf function needs np arrays
            scaler = preprocessing.MinMaxScaler().fit(X)
            X = scaler.transform(X)    #data is scaled to values between 1 and 0 using minmax scaler
            y = np.array(y)    #the clf function needs np arrays

            # the classifier is balanced because class 0 exceeds class 1 by far,
            # (only one pathogenic mutation per case, but several hundred genes per case)
            clf = svm.SVC(kernel='poly', C=C, degree=2, probability=False, class_weight='balanced')
            clf.fit(X, y)

            for smpl in self.samples:
                # only those samples are tested with the classifier that ARE in the bucket
                if smpl.case in bucket:
                    smpl.pedia = float(clf.decision_function(scaler.transform(np.array([smpl.gestalt, smpl.feature , smpl.cadd_phred, smpl.phenomizer, smpl.boqa]))))
            bn += 1

    def save_SVM(self, C=1):
        """ saves the classifier so that it can be reloaded and quickly used for other purposes"""
        print('loading data')
        X = []
        y = []
        for smpl in self.samples:
            X.append([smpl.gestalt, smpl.feature, smpl.cadd_phred, smpl.phenomizer, smpl.boqa])
            y.append([smpl.pathogenicity])
        X = np.array(X)
        scaler = preprocessing.MinMaxScaler().fit(X)
        X = scaler.transform(X)
        y = np.array(y)
        print('training classifier')
        clf = svm.SVC(kernel='poly', C=C, degree=2, probability=False, class_weight='balanced')
        clf.fit(X, y)
        print('saving classifier')
        joblib.dump(clf, 'pedia_classifier.pkl', compress=9)
        print('saving scaler')
        joblib.dump(scaler, 'pedia_scaler.pkl', compress=9)
        print('done saving')


    def classify_10xSVM_extom(self):
        """ a 10x validation SVM classification of all samples in the instance of Data. The samples' pedia atrribute will be adjusted accordingly. """
        buckets = self.bucketize_data()
        print('10 x cross validation')
        bn = 1    # bucket number
        for bucket in buckets: #10x cross validation, data will be split according to the ID entries in each bucket, that were created by bucketize_data()
            print('computing results for bucket ' + str(bn))
            X = []
            y = []
            for smpl in self.samples:
                if smpl.case not in bucket: #only the data will be used for training that are of cases that are NOT in the topical bucket
                    X.append([smpl.feature,smpl.cadd_phred, smpl.phenomizer, smpl.boqa]) #feature vector
                    y.append(smpl.pathogenicity) #class labels

            X = np.array(X) #the clf function needs np arrays
            scaler = preprocessing.MinMaxScaler().fit(X)
            X = scaler.transform(X) #data is scaled to values between 1 and 0 using minmax scaler
            y = np.array(y)#the clf function needs np arrays

            clf = svm.SVC(kernel='poly', C=1, degree=2, probability=False, class_weight='balanced') #the classifier is balanced because class 0 exceeds class 1 by far, (only one pathogenic mutation per case,but several hundred genes per case)
            clf.fit(X, y)

            for smpl in self.samples:
                if smpl.case in bucket: #only those samples are tested with the classifier that ARE in the bucket
                    smpl.extom = float(clf.decision_function(scaler.transform(np.array([smpl.feature, smpl.cadd_phred, smpl.phenomizer, smpl.boqa]))))
            bn += 1

    def classify_10xSVM_sgt(self): #sgt: specific gene testing
        """ a 10x validation SVM classification of all samples in the instance of Data. The samples' pedia atrribute will be adjusted accordingly. """
        buckets = self.bucketize_data()
        print('10 x cross validation')
        bn = 1 #bucket number
        for bucket in buckets: #10x cross validation, data will be split according to the ID entries in each bucket, that were created by bucketize_data()
            print('computing results for bucket ' + str(bn))
            X = []
            y = []
            for smpl in self.samples:
                if smpl.case not in bucket: #only the data will be used for training that are of cases that are NOT in the topical bucket
                    X.append([smpl.feature,smpl.gestalt, smpl.phenomizer, smpl.boqa]) #feature vector
                    y.append(smpl.pathogenicity) #class labels

            X = np.array(X) #the clf function needs np arrays
            scaler = preprocessing.MinMaxScaler().fit(X)
            X = scaler.transform(X) #data is scaled to values between 1 and 0 using minmax scaler
            y = np.array(y)#the clf function needs np arrays

            clf = svm.SVC(kernel = 'poly', C=1, degree=2, probability=False, class_weight='balanced') #the classifier is balanced because class 0 exceeds class 1 by far, (only one pathogenic mutation per case,but several hundred genes per case)
            clf.fit(X, y)

            for smpl in self.samples:
                if smpl.case in bucket: #only those samples are tested with the classifier that ARE in the bucket
                    smpl.extom = float(clf.decision_function(scaler.transform(np.array([smpl.feature, smpl.gestalt, smpl.phenomizer, smpl.boqa]))))
            bn += 1

    def classify_10xSVM_sympt(self): #sgt: specific gene testing
        """ a 10x validation SVM classification of all samples in the instance of Data. The samples' pedia atrribute will be adjusted accordingly. """
        buckets = self.bucketize_data()
        print('10 x cross validation')
        bn = 1 #bucket number
        for bucket in buckets: #10x cross validation, data will be split according to the ID entries in each bucket, that were created by bucketize_data()
            print('computing results for bucket ' + str(bn))
            X = []
            y = []
            for smpl in self.samples:
                if smpl.case not in bucket: #only the data will be used for training that are of cases that are NOT in the topical bucket
                    X.append([smpl.feature,smpl.phenomizer, smpl.boqa]) #feature vector
                    y.append(smpl.pathogenicity) #class labels

            X = np.array(X) #the clf function needs np arrays
            scaler = preprocessing.MinMaxScaler().fit(X)
            X = scaler.transform(X) #data is scaled to values between 1 and 0 using minmax scaler
            y = np.array(y)#the clf function needs np arrays

            clf = svm.SVC(kernel='poly', C=1, degree=2, probability=False, class_weight='balanced') #the classifier is balanced because class 0 exceeds class 1 by far, (only one pathogenic mutation per case,but several hundred genes per case)
            clf.fit(X, y)

            for smpl in self.samples:
                if smpl.case in bucket: #only those samples are tested with the classifier that ARE in the bucket
                    smpl.extom = float(clf.decision_function(scaler.transform(np.array([smpl.feature, smpl.phenomizer, smpl.boqa]))))
            bn += 1

    def classify_10xMLP(self):
        """ a 10x validation SVM classification of all samples in the instance of Data. The samples' pedia atrribute will be adjusted accordingly. """
        buckets = self.bucketize_data()
        print('10 x cross validation')
        bn = 1 #bucket number
        for bucket in buckets: #10x cross validation, data will be split according to the ID entries in each bucket, that were created by bucketize_data()
            print('computing results for bucket ' + str(bn))
            X = []
            y = []
            for smpl in self.samples:
                if smpl.case not in bucket: #only the data will be used for training that are of cases that are NOT in the topical bucket
                    X.append([smpl.gestalt, smpl.feature, smpl.cadd_phred, smpl.phenomizer, smpl.boqa]) #feature vector
                    y.append(smpl.pathogenicity) #class labels

            X=np.array(X) #the clf function needs np arrays
            scaler = preprocessing.MinMaxScaler().fit(X)
            X=scaler.transform(X) #data is scaled to values between 1 and 0 using minmax scaler
            y=np.array(y)#the clf function needs np arrays

            clf = MLPClassifier(hidden_layer_sizes=(4, 3), max_iter=10, alpha=1e-4,
                    solver='sgd', verbose=10, tol=1e-4, random_state=1,
                    learning_rate_init=.1)
            clf.fit(X,y)

            for smpl in self.samples:
                if smpl.case in bucket: #only those samples are tested with the classifier that ARE in the bucket
                    smpl.pedia = float(clf.predict(scaler.transform(np.array([smpl.gestalt, smpl.feature , smpl.cadd_phred, smpl.phenomizer, smpl.boqa]))))
            bn+=1


    def classify_real(self, training_data):
        """ SVM classification of all samples in the instance of Data against a given training
        data set that is also an instance of class Data """

        print('classification')
        X = []
        y = []
        for smpl in training_data.samples:
            X.append([smpl.gestalt, smpl.feature, smpl.cadd_phred, smpl.phenomizer, smpl.boqa]) #feature vector
            y.append(smpl.pathogenicity)     # class labels

        X = np.array(X)     # the clf function needs np arrays
        scaler = preprocessing.MinMaxScaler().fit(X)
        X = scaler.transform(X)    # data is scaled to values between 1 and 0 using minmax scaler
        y = np.array(y)    # the clf function needs np arrays

        # the classifier is balanced because class 0 exceeds class 1 by far,
        # (only one pathogenic mutation per case,but several hundred genes per case)
        clf = svm.SVC(kernel='poly', C=1, degree=2, probability=False, class_weight='balanced')
        clf.fit(X, y)

        for smpl in self.samples:
                smpl.pedia = float(clf.decision_function(scaler.transform(np.array([smpl.gestalt, smpl.feature, smpl.cadd_phred, smpl.phenomizer, smpl.boqa]))))


    def manhattan(self, ID='all', score='pedia'):
        """ Displays the information in Data as a manhattan plot. If the optional variable ID is set to a string matching a case ID, only the results of this case will be displayed."""
        genepos={}
        chr_sizes=[249250621, 243199373, 198022430, 191154276, 180915260, 171115067, 159138663, 146364022, 141213431, 135534747, 135006516, 133851895, 115169878, 107349540, 102531392, 90354753, 81195210, 78077248, 59128983, 63025520, 48129895, 51304566, 155270560, 59373566, 16571]
        for line in open('allgenepositions.txt'):
            fields = line[:-1].split('\t')
            nm = fields[0]
            chro = fields[1]
            pos = fields[2]
            name = fields[3]
            if name not in genepos:
                genepos[name]=[chro,pos]
        sanos = []
        sanos2 = []
        pathos = []
        s_pos = []
        s_pos2 = []
        p_pos = []
        names = []
        names_x = []
        names_y = []
        for smpl in self.samples:
            if smpl.case==ID or ID=='all':
                if smpl.gene not in genepos and smpl.pathogenicity == 1:
                    print(smpl.gene)
                if smpl.gene in genepos:
                    chrom=genepos[smpl.gene][0][3:]
                    if chrom=='X':
                        chrom=23
                    elif chrom=='Y':
                        chrom=24
                    elif chrom=='M':
                        chrom=25
                    else:
                        chrom=int(chrom)
                    pos=0
                    for i in range(chrom-1):
                        pos+=chr_sizes[i]+10**6
                    pos+=int(genepos[smpl.gene][1])
                    if smpl.pathogenicity==0:
                        if chrom%2==0:
                            sanos2.append(getattr(smpl, score))
                            s_pos2.append(pos)
                        else:
                            sanos.append(getattr(smpl, score))
                            s_pos.append(pos)

                    if smpl.pathogenicity==1:
                        pathos.append(getattr(smpl, score))
                        p_pos.append(pos)
                        if smpl.gene in names:
                            for i in range(len(names)):
                                if names[i]==smpl.gene:
                                    if names_y[i]<getattr(smpl, score):
                                        names_y[i]=getattr(smpl, score)
                        if smpl.gene not in names:
                            names.append(smpl.gene)
                            names_x.append(pos)
                            names_y.append(getattr(smpl, score))

        plt.scatter(s_pos,sanos, color='#70ACC0', alpha=0.6, marker='o', s=400, label=('neutrals')) #s=30
        plt.scatter(s_pos2,sanos2, color='#008B8B', alpha=0.6, marker='o', s=400, label=('neutrals')) #s=30  #385660
        plt.scatter(p_pos,pathos, color='#AA1C7D', alpha=0.6, marker='o', s=400, label='pathogenic') #s=30
        for i in range(len(names)):
            plt.annotate(names[i], xy = (names_x[i], names_y[i]), xytext = (names_x[i], names_y[i]), fontsize=70, color='#AA1C7D')#, textcoords = 'offset points')
        plt.xlabel('chromosomal position', fontsize=30)
        ticks = []
        tick = 0
        for i in chr_sizes:
            tick += i/2
            ticks.append(tick)
            tick += (i/2)+10**6
        plt.xticks(ticks)
        plt.ylabel( score+' score', fontsize=30)
        plt.legend(loc='upper left', fontsize=25)
        frame1 = plt.gca()
        chr_names = []
        for i in range(1,26):
            if i == 23:
                chr_names.append('X')
            elif i == 24:
                chr_names.append('Y')
            elif i == 25:
                chr_names.append('M')
            else:
                chr_names.append(str(i))
        frame1.axes.xaxis.set_ticklabels(chr_names, fontsize=25)
        frame1.axes.tick_params(axis='x',length=0)
        frame1.axes.tick_params(axis='y', labelsize=25)
        y_min = min([min(sanos), min(sanos2), min(pathos)])
        y_max = max([max(sanos), max(sanos2), max(pathos)])
        plt.ylim(y_min, y_max+(y_max/10)) #ymin-(ymax/30)
        plt.xlim(0, ticks[-1]+(chr_sizes[-1]/2)+10**6)
        plt.figure(figsize=(20, 10))
        filename = "manhattan_" + ID + ".png"
        plt.savefig(filename)

    def ranker(self, col, lab):
        """A function to evaluate (rank) the results of the classification and put into a plot.
        only to be used after data was classified."""

        # data is what is to be analyzed, it must have the structure of alldatascored in classify()
        # col is the color of the plot
        # lab is the label of the plot

        print('ranking results based on',lab)
        data = []
        for smpl in self.samples:
            data.append([smpl.case, smpl.pedia, smpl.gestalt, smpl.pathogenicity])

        n_cases = len(self.casedisgene)
        # sorts the data by case ID because it has index 0 in alldatascored, and then by pedia score,
        # because it has index 1
        data.sort()

        # reverses the data so that each scases starts with the entry with the highest pedia score
        data.reverse()

        # a list that will contain lists of the IDs of each case and the rank of the respective
        # pathogenic variant, ranked by the pedia-score
        combined_rank = []
        rank = 1
        case = data[0][0]
        pathoamongdata = False     # is the pathogenic gene still among the data (it had not been filtered out?)
        npf = 0     # number passed filter
        for entry in data:
            currcase = entry[0]
            patho = entry[-1]
            if currcase != case:
                if not pathoamongdata:
                    combined_rank.append([case, 102])
                    # if the pathogenic gene had not been in that case anymore the case will be assigned
                    # a rank of 105 (so that it is higher than 100 will be regarded as having failed)
                pathoamongdata = False      #pathoamongdata is set back to false
                rank = 1
                case = currcase

            if patho == 1:
                combined_rank.append([case, rank])    # assignes the rank of the pathogenic gene to the case
                pathoamongdata = True    # true because there was a pathogenic gene in that case
                npf += 1

            rank += 1    # increased by 1 for each iteration, because the list is sorted by case and than pedia score

        combined_performance = []
        for i in range(101):    # will evalute ranks in range 0 to 101)
            sens = 0
            for j in combined_rank:
                rank = j[1]
                if rank <= i:
                    sens += 1    # how many cases have a patho rank lower than or eqal to i
            # the absolute number is divided by the total number of cases,
            # so that one has the fraction of cases having a patho rank not higher than i
            sens = (sens/n_cases)
            # appends sens to i, so that combined rank is a list of floats, each float describing the
            # fraction of cases that have a pathorank lower or eqaul to its index
            combined_performance.append(sens)
        plt.plot(range(1, len(combined_performance)), combined_performance[1:],
                color=col, alpha=0.6, label=lab, linewidth=3)
        plt.scatter([1,10,100],[combined_performance[1],combined_performance[10],combined_performance[100]],
                color=col, alpha=0.6, marker='o', s=50)
        print(lab, [combined_performance[1], combined_performance[10], combined_performance[100]],
                'fraction passed filter:', (npf/n_cases))
        plt.ylim(0, 1.01) #the last lines of code are only needed to display the results
        plt.xlim(0, 100.5)
        plt.xlabel('rank-cut-off')
        plt.ylabel('Sensitivity')
        plt.title('Sensitivity-rank-cut-off-correlation')
        plt.legend(loc='lower right')

    def ranker2(self,col,lab, score='pedia'):
        """A function to evaluate (rank) the results of the classification and put into a plot. only to be used after data was classified."""
        #data is what is to be analyzed, it must have the structure of alldatascored in classify()
        #col is the color of the plot
        #lab is the label of the plot
        print('ranking results based on',lab)
        cases={}
        combined_rank=[] #a list that will contain lists of the IDs of each case and the rank of the respective pathogenic variant, ranked by the pedia-score
        n_cases = len(self.casedisgene)
        npf=0 #number passed filter
        for smpl in self.samples:
            if smpl.case in cases:
                cases[smpl.case].append([getattr(smpl, score), smpl.pathogenicity])
            if smpl.case not in cases:
                cases[smpl.case]=[[getattr(smpl, score), smpl.pathogenicity]]
        for case in cases:
            cases[case].sort()
            cases[case].reverse()
            ranks=(list(enumerate(cases[case])))
            for i in ranks:
                rank=102
                if i[1][1]==1:
                    rank=i[0]+1
                    npf+=1
                combined_rank.append([case,rank])
        combined_performance=[]
        for i in range(101): #will evalute ranks in range 0 to 101)
            sens=0
            for j in combined_rank:
                rank=j[1]
                if rank<=i:
                    sens+=1 #how many cases have a patho rank lower than or eqal to i
            sens=(sens/n_cases) #the absolute number is divided by the total number of cases, so that one has the fraction of cases having a patho rank not higher than i
            combined_performance.append(sens) #appends sens to i, so that combined rank is a list of floats, each float describing the fraction of cases that have a pathorank lower or eqaul to its index
        plt.plot(range(1,len(combined_performance)),combined_performance[1:], color=col, alpha=0.6, label=lab, linewidth=3)
        plt.scatter([1,10,100],[combined_performance[1],combined_performance[10],combined_performance[100]], color=col, alpha=0.6, marker='o', s=50)
        print(lab,[combined_performance[1],combined_performance[10],combined_performance[100]],'fraction passed filter:',(npf/n_cases))
        plt.ylim(0, 1.01) #the last lines of code are only needed to display the results
        plt.xlim(0, 100.5)
        plt.xlabel('rank-cut-off')
        plt.ylabel('Sensitivity')
        plt.title('Sensitivity-rank-cut-off-correlation')
        plt.legend(loc='lower right')

    def ranker_returner(self, lab, score='pedia'):
        """A function to evaluate (rank) the results of the classification and put into a plot.
        only to be used after data was classified."""

        # data is what is to be analyzed, it must have the structure of alldatascored in classify()
        # col is the color of the plot
        # lab is the label of the plot
        print('ranking results based on', lab)
        cases = {}
        # a list that will contain lists of the IDs of each case and the rank of the respective
        # pathogenic variant, ranked by the pedia-score
        combined_rank = []
        n_cases = len(self.casedisgene)
        npf = 0    #number passed filter
        for smpl in self.samples:
            if smpl.case in cases:
                cases[smpl.case].append([getattr(smpl, score), smpl.pathogenicity * (-1)])
            if smpl.case not in cases:
                cases[smpl.case] = [[getattr(smpl, score), smpl.pathogenicity * (-1)]]
        for case in cases:
            cases[case].sort()
            cases[case].reverse()
            ranks = (list(enumerate(cases[case])))
            for i in ranks:
                rank = 102
                if i[1][1] == -1:
                    rank = i[0] + 1
                    npf += 1
                combined_rank.append([case, rank])
        combined_performance = []
        for i in range(101):    # will evalute ranks in range 0 to 101
            sens = 0
            for j in combined_rank:
                rank = j[1]
                if rank <= i:
                    sens += 1    # how many cases have a patho rank lower than or eqal to i
            # the absolute number is divided by the total number of cases, so that one has
            # the fraction of cases having a patho rank not higher than i
            sens = (sens/n_cases)
            # appends sens to i, so that combined rank is a list of floats, each float describing
            # the fraction of cases that have a pathorank lower or eqaul to its index
            combined_performance.append(sens)
#        plt.plot(range(1,len(combined_performance)),combined_performance[1:], color=col, alpha=0.6, label=lab, linewidth=3)
#        plt.scatter([1,10,100],[combined_performance[1],combined_performance[10],combined_performance[100]], color=col, alpha=0.6, marker='o', s=50)
#        print(lab,[combined_performance[1],combined_performance[10],combined_performance[100]],'fraction passed filter:',(npf/n_cases))
#        plt.ylim(0, 1.01) #the last lines of code are only needed to display the results
#        plt.xlim(0, 100.5)
#        plt.xlabel('rank-cut-off')
#        plt.ylabel('Sensitivity')
#        plt.title('Sensitivity-rank-cut-off-correlation')
#        plt.legend(loc='lower right')
        return([combined_performance[1], combined_performance[10], combined_performance[100]])

    def ranker_returner2(self,lab, score='pedia'):
        """A function to evaluate (rank) the results of the classification and put into a plot. only to be used after data was classified."""
        #data is what is to be analyzed, it must have the structure of alldatascored in classify()
        #col is the color of the plot
        #lab is the label of the plot
        print('ranking results based on',lab)
        cases={}
        combined_rank=[] #a list that will contain lists of the IDs of each case and the rank of the respective pathogenic variant, ranked by the pedia-score
        n_cases = len(self.casedisgene)
        npf=0 #number passed filter
        for smpl in self.samples:
            if smpl.case in cases:
                cases[smpl.case].append([getattr(smpl, score), smpl.pathogenicity*(-1)])
            if smpl.case not in cases:
                cases[smpl.case]=[[getattr(smpl, score), smpl.pathogenicity*(-1)]]
        for case in cases:
            cases[case].sort()
            cases[case].reverse()
            ranks=(list(enumerate(cases[case])))
            print(ranks)
            for i in ranks:
                rank=102
                if i[1][1]==-1:
                    rank=i[0]+1
                    npf+=1
                combined_rank.append([case,rank])
        combined_performance=[]
        for i in range(101): #will evalute ranks in range 0 to 101)
            sens=0
            for j in combined_rank:
                rank=j[1]
                if rank<=i:
                    sens+=1 #how many cases have a patho rank lower than or eqal to i
            sens=(sens/n_cases) #the absolute number is divided by the total number of cases, so that one has the fraction of cases having a patho rank not higher than i
            combined_performance.append(sens) #appends sens to i, so that combined rank is a list of floats, each float describing the fraction of cases that have a pathorank lower or eqaul to its index
#        plt.plot(range(1,len(combined_performance)),combined_performance[1:], color=col, alpha=0.6, label=lab, linewidth=3)
#        plt.scatter([1,10,100],[combined_performance[1],combined_performance[10],combined_performance[100]], color=col, alpha=0.6, marker='o', s=50)
#        print(lab,[combined_performance[1],combined_performance[10],combined_performance[100]],'fraction passed filter:',(npf/n_cases))
#        plt.ylim(0, 1.01) #the last lines of code are only needed to display the results
#        plt.xlim(0, 100.5)
#        plt.xlabel('rank-cut-off')
#        plt.ylabel('Sensitivity')
#        plt.title('Sensitivity-rank-cut-off-correlation')
#        plt.legend(loc='lower right')
        print([combined_performance[1],combined_performance[10],combined_performance[100]])


    def compare(self, score1='pedia', score2='gestalt', score3='extom'):
        cases={}
        rank1=1000
        rank2=1000
        rank5=1000
        ranking={}
        for smpl in self.samples:
            if smpl.case in cases:
                cases[smpl.case].append([getattr(smpl, score1), smpl.pathogenicity])
            if smpl.case not in cases:
                cases[smpl.case]=[[getattr(smpl, score1), smpl.pathogenicity]]
        for case in cases:
            cases[case].sort()
            cases[case].reverse()
            ranks=(list(enumerate(cases[case])))
            for i in ranks:
                if i[1][1]==1:
                    #print(i)
                    ranking[case]=[i[0]+1]
                    #print(case,ranking[case],[i[0]+1])
        cases={}
        for smpl in self.samples:
            if smpl.case in cases:
                cases[smpl.case].append([getattr(smpl, score2), smpl.pathogenicity])
            if smpl.case not in cases:
                cases[smpl.case]=[[getattr(smpl, score2), smpl.pathogenicity]]
        for case in cases:
            cases[case].sort()
            cases[case].reverse()
            ranks=(list(enumerate(cases[case])))
            for i in ranks:
                if i[1][1]==1:
                    ranking[case].append(i[0]+1)
        cases={}
        for smpl in self.samples:
            if smpl.case in cases:
                cases[smpl.case].append([getattr(smpl, score3), smpl.pathogenicity])
            if smpl.case not in cases:
                cases[smpl.case]=[[getattr(smpl, score3), smpl.pathogenicity]]
        for case in cases:
            cases[case].sort()
            cases[case].reverse()
            ranks=(list(enumerate(cases[case])))
            for i in ranks:
                if i[1][1]==1:
                    ranking[case].append(i[0]+1)
        for case in ranking:
            if ranking[case][0]<ranking[case][2]:
                print(str(case),ranking[case])

    def ranker3(self,col,lab, score='pedia'):
        """A function to evaluate (rank) the results of the classification and put into a plot. only to be used after data was classified."""
        #data is what is to be analyzed, it must have the structure of alldatascored in classify()
        #col is the color of the plot
        #lab is the label of the plot
        print('ranking results based on',lab)
        genes={}
        cdg={}
        for entry in self.casedisgene:
            genes[entry[1]]=[]
            cdg[entry[0]]=entry[1]

        cases={}
        combined_rank=[] #a list that will contain lists of the IDs of each case and the rank of the respective pathogenic variant, ranked by the pedia-score
        n_cases = len(self.casedisgene)
        npf=0 #number passed filter
        for smpl in self.samples:
            if smpl.case in cases:
                cases[smpl.case].append([getattr(smpl, score), smpl.pathogenicity, smpl.gene])
            if smpl.case not in cases:
                cases[smpl.case]=[[getattr(smpl, score), smpl.pathogenicity, smpl.gene]]
        for case in cases:
            cases[case].sort()
            cases[case].reverse()
            ranks=(list(enumerate(cases[case])))
            rank=102
            for i in ranks:
                if i[1][1]==1:
                    rank=i[0]+1
                    npf+=1
            genes[cdg[case]].append(rank)
        #print('genes:',genes)
        for gene in genes:
#            if genes[gene]==[]:
#                genes[gene]=[102]
            ranksum=0
            for rank in genes[gene]:
                ranksum+=rank
            ranksum/=len(genes[gene])
            combined_rank.append([gene,ranksum])
            print(gene, genes[gene], ranksum)
        combined_performance=[]
        for i in range(101): #will evalute ranks in range 0 to 101)
            sens=0
            for j in combined_rank:
                rank=j[1]
                if rank<=i:
                    sens+=1 #how many cases have a patho rank lower than or eqal to i
            sens=(sens/len(genes)) #the absolute number is divided by the total number of cases, so that one has the fraction of cases having a patho rank not higher than i
            combined_performance.append(sens) #appends sens to i, so that combined rank is a list of floats, each float describing the fraction of cases that have a pathorank lower or eqaul to its index
        plt.plot(range(1,len(combined_performance)),combined_performance[1:], color=col, alpha=0.6, label=lab, linewidth=3)
        plt.scatter([1,10,100],[combined_performance[1],combined_performance[10],combined_performance[100]], color=col, alpha=0.6, marker='o', s=50)
        print(lab,[combined_performance[1],combined_performance[10],combined_performance[100]],'fraction passed filter:',(npf/n_cases))
        plt.ylim(0, 1.01) #the last lines of code are only needed to display the results
        plt.xlim(0, 100.5)
        plt.xlabel('rank-cut-off')
        plt.ylabel('Sensitivity')
        plt.title('Sensitivity-rank-cut-off-correlation')
        plt.legend(loc='lower right')






    def save_jsons(self,path):
        '''a function to save the pedia scores in their respective jsons'''
        cwd=os.getcwd()
        os.chdir(path)
        print('saving results')
        for file in os.listdir():
            if file[-5:]=='.json':
                print(file)
                with open(file) as json_data:
                        casedata = json.load(json_data)
                        for smpl in self.samples:
                            for i in casedata['geneList']:
                                if i['gene_symbol']==smpl.gene:
                                    i['pedia_score']=smpl.pedia
                with open(file, 'w') as f:
                     json.dump(casedata, f)
        os.chdir(cwd)
        print('finished saving')

    def hyper_search_helper(self, start=-5, stop=5, step=10, maximum=0, attempts=2, best=[0,[0,0,0]]):
        for i in range(0, step + 1, 1):
            exp = start + (i / step * (stop - start))
            print('evaluating c-value of 10**' + str(exp) + '\nstep ' + str(i + 1) + ' of ' + str(step))
            c_value=10**exp
            self.classify_10xSVM(c_value)
            performance = [exp, self.ranker_returner(lab=('c_value = 10**' + str(exp)))]
            if performance[1][1] > best[1][1]:
                best = performance
            elif performance[1][1] == best[1][1]:
                if performance[1][0] > best[1][0]:
                    best = performance
                elif performance[1][0] == best[1][0] and performance[1][2] > best[1][2]:
                    best = performance
            #results.append(performance)
            print('best', best)
        #print(results)
        print('best',best)
        if best[0] == maximum:
            attempts -= 1
        if best[0] != start and best[0] != stop:
            result = [best[0] - (2 * ((stop - start) / step)), best[0] + (2 * ((stop-start) / step)), step, attempts, best]
        else:
            result=[start - ((stop - start)), stop + ((stop - start)), step, attempts, best]
        return(result)

    def hyper_search(self, start=-5, stop=5, step=10, maximum=0, attempts=2, best=[0,[0,0,0]]):
        iteration = 1
        while attempts > 0:
            print('hyperparameter search round: ' + str(iteration) + ' \nremaining determination attempts ' + str(attempts))
            new = self.hyper_search_helper(start, stop, step, maximum, attempts, best)
            start = new[0]
            stop = new[1]
            step = new[2]    # not really necessary as step doesnt change in hyper_search_helper
            attempts = new[3]
            maximum = new[4][0]
            best = new[4]
            iteration += 1
        print('hyperparameter search determined best c-value at ' + str(best))

