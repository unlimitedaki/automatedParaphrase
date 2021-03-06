from translator import my_memory_translator as memory
from translator import yandex_translator as yandex
from pos import pos_extraction as pos
from filtering import bert_filter as bert
from filtering import use_filter as use
from synonym import nltk_wordnet as nlt
import os
import configparser
#import spacy
# import pdb
import nltk
nltk.download('wordnet')
import argparse


def write_to_folder(data,message,file_name):
    """
    Conserve data as file in result folder
    :param data: python dictionary containing the generated paraphrases
    :param message: a short message that describe the element to be listed
    :param file_name: file name
    """
    path = os.path.join("result",file_name)
    # pdb.set_trace()
    if not os.path.exists(path):
        f = open(path, "w",encoding = "utf8")
    else:
        f = open(path, "a")
    f.write(message+'\n\t'+str(data)+'\n')
    f.close()

def merge_data(dataset1,dataset2):
    """
    Merge dataset1 with dataset2
    :param dataset1: python dictionary
    :param dataset2: python dictionary
    :return a Python dictionary, Key is the initial expression and value is a list of paraphrases
    """
    for (k,v), (k2,v2) in zip(dataset1.items(), dataset2.items()):
        v.add(k2) # add key of dataset2 to dataset1 list of paraphrases
        v.update(v2) # add dataset2 paraphrases list to dataset1 paraphrases list
    return dataset1

def main():
    # required arg
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', required=True) # -f data set file name argument
    parser.add_argument('-g') # if -g is defined use google_translator.translate method not translate_wrapper
    parser.add_argument('-l') # -l integer that indicate the pivot language level, single-pivot or multi-pivot range between 1 and 3
    args = parser.parse_args()
    
    # load configs from config.ini file
    config = configparser.ConfigParser(inline_comment_prefixes="#")
    config.read(os.path.join(os.path.dirname(__file__), ".","config.ini"))
    my_memory_config = config["MYMEMORY"]
    yandex_config = config["YANDEX"]
    google_config = config["GOOGLE"]

    try:
        if "email" not in my_memory_config or my_memory_config["email"] == "":
            raise Exception("Define a Valid email address for MyMemory API in config.ini")
        else:
            valid_mail = my_memory_config['email']
        # if "api_key" not in yandex_config or yandex_config["api_key"] == "":
        #     raise Exception("Yandex Translate API token is not defined in config.ini")
        # else:
        #     yandex_api_key = yandex_config["api_key"]
        if args.g:
            if "api_key" not in google_config or google_config["api_key"] == "":
                raise Exception("Google Translate API token is not defined in config.ini")
            else:
                google_api_key = google_config['api_key']
        if args.l:
            pivot_level = int(args.l)
        else:
            pivot_level = 0

    except Exception as e:
        print(str(e))
        exit()

    file_path = os.path.join(os.path.dirname(__file__), ".", "dataset/"+args.f) # data to paraphrase

    #wordnet
    print("Start weak supervision data generation")
    # Generate data by Replacing only word with VERB pos-tags by synonym
    spacy_tags = ['VERB'] #list of tag to extract from sentence using spacy
    wm_tags = ['v'] #wordnet select only lemmas which pos-taggs is in wm_tags
    data1 = nlt.main(file_path,spacy_tags,wm_tags)
    # Generate data by Replacing only word with NOUN pos-tags by synonym 
    spacy_tags = ['NOUN'] #list of tag to extract from sentence using spacy
    wm_tags = ['n'] #wordnet select only lemmas which pos-taggs is in wm_tags
    data2 = nlt.main(file_path,spacy_tags,wm_tags)
    # Generate data by Replacing only word with NOUN and VERB pos-tags by synonym
    spacy_tags = ['VERB','NOUN'] #list of tag to extract from sentence using spacy
    wm_tags = ['v','n'] #wordnet select only lemmas which pos-taggs is in wm_tags
    data3 = nlt.main(file_path,spacy_tags,wm_tags)
    print(data1,data2,data3)
    print("Start translation")
    # generate paraphrases with MyMemory API
    memory_result1 = memory.translate_list(data1,valid_mail)
    memory_result2 = memory.translate_list(data2,valid_mail)
    memory_result3 = memory.translate_list(data3,valid_mail)
    print(memory_result1,memory_result2,memory_result3)
    result = memory.translate_file(file_path,valid_mail)
    # pdb.set_trace()
    
    # merge memory_result1, memory_result2, memory_result3 with result
    result= merge_data(result,memory_result1)
    result= merge_data(result,memory_result2)
    result= merge_data(result,memory_result3)

    # generate paraphrases with Yandex Translator API
    # yandex_result1 = yandex.translate_list(data1,yandex_api_key,pivot_level)
    # yandex_result2 = yandex.translate_list(data2,yandex_api_key,pivot_level)
    # yandex_result3 = yandex.translate_list(data3,yandex_api_key,pivot_level)

    # # merge memory_result1, memory_result2, memory_result3 with result
    # result= merge_data(result,yandex_result1)
    # result= merge_data(result,yandex_result2)
    # result= merge_data(result,yandex_result3)

    # yandex_result = yandex.translate_file(file_path,yandex_api_key,pivot_level)

    # extracted_pos = pos.pos_extraction(file_path)
    # yandex_paraphrases = yandex.translate_dict(extracted_pos,yandex_api_key,pivot_level)
    
    
    # #create a function that take a list of dataset and merge them togheteherset
    # for key,values in result.items():
    #     values.update(yandex_result[key])
    #     values.update(yandex_paraphrases[key])
    #     result[key] = values


    write_to_folder(result,"Generated Paraphrases:","paraphrases.txt")
    #universal sentence encoder filtering
    print("Start Universal Sentence ENcoder filtering")
    use_filtered_paraphrases = use.get_embedding(result)
    write_to_folder(use_filtered_paraphrases,"Universal Sentence Encoder Filtering:","paraphrases.txt")

    # apply BERT filtering after USE filtering
    print("Start BERT filtering")
    bert_filtered_paraphrases = bert.bert_filtering(use_filtered_paraphrases)
    write_to_folder(bert_filtered_paraphrases,"BERT filtering:","paraphrases.txt")
    print("Start BERT deduplication")
    bert_deduplicate_paraphrases = bert.bert_deduplication(bert_filtered_paraphrases)
    write_to_folder(bert_deduplicate_paraphrases,"BERT deduplication:","paraphrases.txt")

if __name__ == "__main__":
    main()
