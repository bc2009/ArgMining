import argparse
from argmining.sentence.loaders.THF_sentence_corpus_loader import load_dataset
from time import time
from sklearn.model_selection import GridSearchCV
import logging
from argmining.pipelines.pipeline import pipeline
from argmining.strategies.strategies import STRATEGIES
from argmining.evaluation.gridsearch_report import report_best_results
from argmining.classifiers.classifier import get_classifier
from argmining.evaluation.reduce_training_set import reduce_training_set
from argmining.evaluation.shuffle import shuffle_training_Set

NJOBS = 1


def config_argparser():
    argparser = argparse.ArgumentParser(description='ArgMining')
    argparser.add_argument('-nfold', type=int, help='n-fold crossvalidation', default=2)
    argparser.add_argument('-subtask', type=str, required=True, help='Name of the subtask')
    argparser.add_argument('-strategy', type=str, required=True, help='Name of the strategy')
    argparser.add_argument('-c', '--classifier', type=str, required=True, help='Name of the classifier')
    argparser.add_argument('--shuffle', type=int, help='Random state of the shuffle or None', default=None)
    argparser.add_argument('--trainingsize', type=int,
                           help='Amount of training data to be used, e.g. 50 for 50% of the data', default=100)
    return argparser.parse_args()


if __name__ == '__main__':
    t0 = time()
    logger = logging.getLogger()
    arguments = config_argparser()
    # 1) Load data sets
    X_train, y_train = load_dataset(file_path='data/THF/sentence/subtask{}_train.json'.format(arguments.subtask))
    # 2) Shuffle if desired
    X_train, y_train = shuffle_training_Set(X_train, y_train, arguments.shuffle)
    # 4) Reduce training size
    X_train, y_train = reduce_training_set(X_train, y_train, arguments.trainingsize)
    # 5) Select feature combination
    logger.info("Using strategy: {}".format(arguments.strategy))
    strategy = STRATEGIES[arguments.strategy]
    # 6) Select classifier
    logger.info("Using classifier: {}".format(arguments.classifier))
    classifier, param_grid = get_classifier(arguments.classifier)
    # 7) Start grid search
    pipe = pipeline(strategy=strategy, classifier=classifier)
    logger.info("Start grid search")
    gridsearch = GridSearchCV(pipe, param_grid, scoring='f1_macro', cv=arguments.nfold, n_jobs=NJOBS, verbose=2)
    gridsearch.fit(X_train, y_train)
    # 8) Report results
    report_best_results(gridsearch.cv_results_)
    logger.info("Total execution time in %0.3fs" % (time() - t0))
    logger.info("*****************************************")
