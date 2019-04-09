import argparse
import inspect
from keras import losses, optimizers
from keras.models import load_model
from lee_dernoncourt import lee_dernoncourt
from kadjk import kadjk
from embedding import read_word2vec, read_glove_twitter, read_fasttext_embedding
from dataset import load_swda_corpus_data
from translate import translate_and_store_swda_corpus_test_data

models =     {
#                'Lee-Dernoncourt': lee_dernoncourt,
                'KADJK': kadjk
             }

embeddings = {
#                'word2vec': read_word2vec, # https://code.google.com/archive/p/word2vec/
#                'GloVe': read_glove_twitter # https://nlp.stanford.edu/projects/glove/
                'FastText': read_fasttext_embedding # https://fasttext.cc/docs/en/crawl-vectors.html
             }

datasets =   {
                'SwDA': load_swda_corpus_data
             }

supported_languages =   {
                            'de',
                            'es',
                            'tr'
                        }

default_parameters =    {
                            'Lee-Dernoncourt': {'loss':'logcosh' , 'optimizer': 'adadelta'},
                            'KADJK': {'loss':'logcosh' , 'optimizer': 'adadelta'}
                        }


def print_options(option_dict):
    for key in option_dict.keys():
        print('\t' + key)

def check_keras_option_validity(option_given, keras_option_data):
    for a, b in keras_option_data:
        if a == option_given:
            return True
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Short-text classification training tool.')
    parser.add_argument('--loss-functions', action='store_true', help='Print available loss functions.')
    parser.add_argument('--optimizers', action='store_true', help='Print available optimizers.')
    parser.add_argument('--models', action='store_true', help='Print available models.')
    parser.add_argument('--embeddings', action='store_true', help='Print possible word embeddings.')
    parser.add_argument('--datasets', action='store_true', help='Print possible datasets.')
    parser.add_argument('--languages', action='store_true', help='Print supported languages.')
    parser.add_argument('--translate-tests-by-word', nargs=2, metavar=('LANG', 'PATH'), type=str, help='Translate language of the SwDA test data word by word, to one of the supported languages.')
    parser.add_argument('--translate-tests-by-utterance', nargs=2, metavar=('LANG', 'PATH'), type=str, help='Translate language of the SwDA test data by utterance, to one of the supported languages.')

    parser.add_argument('--model', type=str, help='Model to use.')
    parser.add_argument('--dataset', nargs=2, metavar=('TYPE', 'PATH'), type=str, help='Dataset to use.')
    parser.add_argument('--source-language', nargs=2, metavar=('LANG', 'PATH'), type=str, help='Source language, and the path to the relevant monolingual embedding file.')
    parser.add_argument('--target-language', nargs=2, metavar=('LANG', 'PATH'), type=str, help='Target language, and the path to the relevant monolingual embedding file.')
    parser.add_argument('--target-testing-data', nargs=1, metavar=('LANG'), type=str, help='Source language.')
    parser.add_argument('--use-translated-tests', nargs=2, metavar=('LANG', 'PATH'), type=str, help='Use translated test data.')
    parser.add_argument('--embedding', nargs=1, metavar=('TYPE'), type=str, help='Embedding to use.')
    parser.add_argument('--loss-function', type=str, help='Loss function to use.')
    parser.add_argument('--optimizer', type=str, help='Optimizer to use.')
    parser.add_argument('--save-model', type=str, metavar=('SAVE_FILE_PATH'), help='Save model to a .h5 file once training is complete.')
    parser.add_argument('--load-model', type=str, help='Load pretrained model from a .h5 file and print its accuracy.')
    parser.add_argument('--shuffle-words', action='store_true', help='Shuffle the order of the words in utterances for training dataset.')

    parser.add_argument('--train', nargs=1, metavar=('NUM_EPOCHS'), type=int, help='Train the specified network for given number of epochs.')
    # TODO: Add a parameter that helps a trained network evaluate a sample conversation

    args = parser.parse_args()

    if args.translate_tests_by_word:
        if args.translate_tests_by_word[0] in supported_languages:
            language = args.translate_tests_by_word[0]
            translation_path = args.translate_tests_by_word[1]
            if args.dataset and datasets[args.dataset[0]]:
                dataset_loading_function = datasets[args.dataset[0]]
                dataset_file_path = args.dataset[1]
                translate_and_store_swda_corpus_test_data(dataset_file_path, translation_path, language, False)
    elif args.translate_tests_by_utterance:
        if args.translate_tests_by_utterance[0] in supported_languages:
            language = args.translate_tests_by_utterance[0]
            translation_path = args.translate_tests_by_utterance[1]
            if args.dataset and datasets[args.dataset[0]]:
                dataset_loading_function = datasets[args.dataset[0]]
                dataset_file_path = args.dataset[1]
                translate_and_store_swda_corpus_test_data(dataset_file_path, translation_path, language, True)
    elif args.loss_functions:
        loss_functions = inspect.getmembers(losses, inspect.isfunction)
        print('Loss functions available:')
        for (a, b) in loss_functions:
            print('\t' + a)
    elif args.optimizers:
        optimizer_classes = inspect.getmembers(optimizers, inspect.isclass)
        print('Optimizers available:')
        for (a, b) in optimizer_classes:
            print('\t' + a)
    elif args.models:
        print('Models available:')
        print_options(models)
    elif args.languages:
        print('Languages available:')
        for lang in supported_languages:
            print('\t' + lang)
    elif args.embeddings:
        print('Embeddings available:')
        print_options(embeddings)
    elif args.datasets:
        print('Datasets available:')
        print_options(datasets)
    else:
        if args.model and args.embedding and args.dataset and\
           models[args.model] and embeddings[args.embedding[0]] and datasets[args.dataset[0]] and\
           args.target_language[0] in supported_languages:
            model = models[args.model]
            embedding_loading_function = embeddings[args.embedding[0]]

            source_lang = args.source_language[0]
            target_lang = args.target_language[0]
            source_lang_embedding_file = args.source_language[1]
            target_lang_embedding_file = args.target_language[1]

            dataset_loading_function = datasets[args.dataset[0]]
            dataset_file_path = args.dataset[1]

            language_to_translate = None
            parameters = default_parameters[args.model]
            load_from_model_file = args.load_model
            save_model_to_file = args.save_model
            num_epochs_to_train = 0

            language_to_translate = None
            translation_path = None
            target_test_data_path = args.target_testing_data[0]

            if args.loss_function:
                loss_valid = check_keras_option_validity(args.loss_function,
                                                         inspect.getmembers(losses, inspect.isfunction))
                if loss_valid:
                    parameters['loss'] = args.loss_function

            if args.optimizer:
                optimizer_valid = check_keras_option_validity(args.optimizer,
                                                              inspect.getmembers(optimizers, inspect.isclass))
                if optimizer_valid:
                    parameters['optimizer'] = args.optimizer

            if args.train:
                num_epochs_to_train = args.train[0]

            shuffle_words = args.shuffle_words

            model(dataset_loading_function, dataset_file_path,
                  embedding_loading_function,
                  source_lang, source_lang_embedding_file,
                  target_lang, target_lang_embedding_file,
                  target_test_data_path,
                  num_epochs_to_train, parameters['loss'], parameters['optimizer'],
                  shuffle_words, load_from_model_file, save_model_to_file)
        else:
            print("Please enter all the required arguments. Use --help to review required arguments.")
