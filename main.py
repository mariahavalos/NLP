# -*- coding: utf-8 -*-
import spacy
import re
import json


coreference_words = ["they", "them", "their", "it", "its", "she", "he", "her", "hers", "his", "herself",
                     "himself"]
number_values = ["million", "billion", "thousand", "hundred", "hundreds", "millions", "thousands", "billions"]

immediate_coreference_words = ["who", "that"]

nlp = spacy.load('en_core_web_sm')

final_json = {}
node_number = 0
prev_node_number = 0

import csv

# Takes a csv file and outputs an array containing its contents

with open("/Users/mariahavalos/Desktop/Apple_data.csv", "r") as open_csv:
    content = open_csv.readlines()

	# Load each line of csv contents into array, return array
    for line in content:

        line = re.sub(r'[^\x00-\x7F]+',' ', line)
        s = unicode(line,encoding="utf-8")
        s = s.replace(".", "")
        doc = nlp(s)

        span = doc[doc[4].left_edge.i : doc[4].right_edge.i+1]
        span.merge()

        noun_count = 0
        verb_count = 0

        nouns = []
        direct_objects = []
        verbs = []
        entity_relation = []
        interm_pair = []

        for token in doc:
            entityCount = 0
            if token.pos_ == "VERB":
                verbs.append(str(token.text))

        interm_pair_prev_dep_ = ""
        interm_pair_prev = ""
        inter_pair_prev_prev_dep_ = ""
        inter_pair_prev_prev = ""
        interm_pair_prev_head = ""
        interm_pair_prev_prev_head = ""
        sentences = []

        for chunk in list(doc.noun_chunks):
            not_in_words = True
            not_verb_connected = True
            for word in coreference_words:
                if word == str(chunk):
                    not_in_words = False
            if not_in_words:
                for verb in verbs:
                    if verb == str(chunk.root.head.text):
                        not_verb_connected = False
                if not not_verb_connected:
                    interm_pair_prev_prev = interm_pair_prev
                    interm_pair_prev_prev_dep_ = interm_pair_prev_dep_
                    interm_pair_prev_prev_head = interm_pair_prev_head
                    interm_pair_prev = str(chunk)
                    interm_pair_prev_dep_ = str(chunk.root.dep_)
                    interm_pair_prev_head = str(chunk.root.head.text)

                    if str(chunk.root.dep_) == "nsubj":
                        interm_pair_prev_dep_ = "nsubj"
                    if str(chunk.root.dep_) == "conj":
                        interm_pair_prev_dep_ = "conj"
                    if str(chunk.root.dep_) == "dobj":
                        interm_pair_prev_dep_ = "dobj"
                        if interm_pair_prev_prev_dep_ == "nsubj":
                            sentences.append([interm_pair_prev_prev] + [interm_pair_prev_head] + [interm_pair_prev])
                    if str(chunk.root.dep_) == "pobj" or str(chunk.root.dep_) == "dobj" or str(chunk.root.dep_) == "conj":
                        if interm_pair_prev_prev_dep_ == "dobj":
                            sentences.append([interm_pair_prev_prev] + [interm_pair_prev_head] + [interm_pair_prev])

                if not_verb_connected:
                    if interm_pair_prev_dep_ == "dobj" and interm_pair_prev_prev_dep_ == "":
                        sentences.append([interm_pair_prev_prev] + [interm_pair_prev_head] + [str(chunk)])

                    if interm_pair_prev_dep_ != "" and interm_pair_prev_dep_ != "dobj":
                        sentences.append([interm_pair_prev] + [interm_pair_prev_head] + [str(chunk)])


                    interm_pair_prev_prev_dep_ = interm_pair_prev_dep_
                    iterm_pair_prev_prev = interm_pair_prev
                    interm_pair_prev = str(chunk)
                    interm_pair_prev_dep_ = ""

        entity_links = []
        temp_links = []
        prev_token = ""
        prev_token_dep = ""
        keep_going = False
        links = []
        iteration = 0

        for token in doc:
            if str(token.dep_) == 'pobj' and not keep_going:
                temp_links.append([str(prev_token)] + [str(token.text)])
                keep_going = True

            if keep_going and str(token.head.pos_) == 'PROPN' or str(token.head.pos_) == 'NOUN' and str(token.head.pos_) != 'ADP':
                temp_links.append([token.text])

            if keep_going and str(token.head.pos_) == 'ADP':
                for child in token.children:
                    links.append([str(token.text)])
                    links.append([str(child)])
                iteration = 1

            if str(token.head.pos_) == "VERB":
                if len(links) > 0:
                    if iteration == 1:
                        for child in links[1]:
                            if str(child) in entity_links:
                                entity_links.append(links)
                                break

                        iteration = 0
                links = []


            if keep_going and not (str(token.head.pos_) == 'PROPN' or str(token.head.pos_) == 'NOUN' and str(token.head.pos_) != 'ADP'):
                entity_links.append(temp_links)
                temp_links = []
                keep_going = False

            prev_token = token.text


        coref_phrases = []
        for sentence in sentences:
            is_pronoun = False
            for head in coreference_words:
                for phrase in sentence:
                    if re.match(head, phrase):
                        coref_phrases.append(phrase)

        prev_token = ""
        prev_token_dep_ = ""
        prev_prev_token = ""
        prev_prev_token_dep_ = ""

        coref_resolution = []

        coref_s = re.sub(r'[^\w\s]','',s)
        coref_doc = nlp(re.sub(r'[^\w\s]','', coref_s))

        for token in coref_doc:
            for head in immediate_coreference_words:
                if re.match(head, token.text):
                    if str(prev_token_dep_) == "nsubj" or str(prev_token_dep_) == "conj" or str(prev_token_dep_) == "dobj" or \
                            str(prev_token_dep_) == "pobj":
                        coref_resolution.append([str(token.text)] + [str(prev_token)])
            prev_prev_token = prev_token
            prev_prev_token_dep = prev_token_dep_
            prev_token = token.text
            prev_token_dep_ = token.dep_

        prev_sentence = ""
        replace_sentence = False
        replace_sentence_value = ""

        for coref_value in coref_resolution[:]:
            for sentence in sentences:
                if sentence[0] == coref_value[0]:
                    sentence[0] = coref_value[len(coref_value) - 1]
                    break

        for sentence in sentences:

            if prev_sentence == sentence[0]:
                replace_sentence = True

            if replace_sentence:
                sentence[0] = replace_sentence_value
                replace_sentence = False

            prev_sentence = sentence[2]
            replace_sentence_value = sentence[0]


        conj_phrases = []
        collection_nouns = []
        prev_token = ""
        prev_token_pos_ = ""
        prev_prev_token = ""
        prev_prev_token_pos_ = ""


        for token in doc:

            if str(token.pos_) == "NOUN" or str(token.pos_) == "PROPN" or str(token.pos_) == "ADP":
                collection_nouns.append([token.text, token.pos_])

            if (prev_token == "and" or prev_token == "with") and (prev_prev_token_pos_ == "NOUN" or prev_prev_token_pos_ == "ADP" or prev_prev_token_pos_ == "PROPN"):
                conj_phrases.append(collection_nouns)

            if str(token.pos_) == "VERB":
                collection_nouns = []

            prev_prev_token = prev_token
            prev_prev_token_pos_ = prev_token_pos_
            prev_token = token.text
            prev_token_pos_ = token.pos_

        prev_prev_phrase_pos_ = ""
        prev_phrase = ""
        prev_phrase_pos_ = ""
        new_vec = []
        conj_vec = []
        noun_chunk = []

        for value in conj_phrases:
            for phrase in value:
                if str(phrase[1]) == "NOUN" or str(phrase[1]) == "PROPN":
                    noun_chunk.append(str(phrase[0]))

                if str(phrase[1]) != "NOUN" and str(phrase[1]) != "PROPN" and \
                    (prev_phrase_pos_ == "NOUN" or prev_phrase_pos_ == "PROPN"):
                    if len(noun_chunk) > 0:
                        new_vec.append(noun_chunk)
                        noun_chunk = []

                prev_prev_phrase_pos_ = prev_phrase_pos_
                prev_prev_phrase = prev_phrase
                prev_phrase = phrase[0]
                prev_phrase_pos_ = phrase[1]

            if len(noun_chunk) > 0:
                new_vec.append(noun_chunk)
            noun_chunk = []
            conj_vec.append(new_vec)
            new_vec = []

        entity_links = {}

        joined_phrase = ""
        sentence_pairing = []
        found = False
        for phrase in conj_vec:
            for value in phrase:
                found = False
                for sentence in sentences:
                    for word in sentence:
                        sentence_words = word.split()
                        original_word = word
                        result_words = [list_word for list_word in sentence_words if list_word.lower() not in
                                        coreference_words and list_word.lower() not in number_values]
                        word = ' '.join(result_words)
                        if len(value) > 0:
                            if len(value) >= 1:
                                joined_phrase = ' '.join(map(str, value))
                            word = filter(lambda x: x.isalpha() or x.isspace(), word)
                            word = word.lstrip()
                            if word != sentence[1] and (word in joined_phrase):
                                if final_json != {}:
                                    for key, val in final_json.items():
                                        if original_word in val['full_form']:
                                            final_json[key]['relations'].append({'relation_term': {word: {'related_to': phrase}}})
                                        else:
                                            final_json[node_number] = {'full_form': original_word, 'relations': [{'relation_term': {word: {'related_to': phrase}}}], 'node_link': [prev_node_number]}
                                            prev_node_number = node_number
                                            node_number += 1
                                            break
                                else:
                                    final_json[node_number] = {'full_form': original_word, 'relations': [{'relation_term': {word: {'related_to': phrase}}}], 'node_link': [prev_node_number]}
                                    prev_node_number = node_number
                                    node_number += 1

                                found = True
                                sentence_pairing.append(sentence + phrase)
                                break
                    if found:
                        break

        temp_node_number = 0
        temp_prev_node_number = 0

        for sentence in sentences:
            node_number += 1
            node_in_json = False
            second_node_in_json = False

            for key, value in final_json.items():
                if sentence[0] in value['full_form']:
                    node_in_json = True
                    temp_node_number = key
                if sentence[2] in value['full_form']:
                    temp_prev_node_number = key
                    second_node_in_json = True

            if node_in_json and second_node_in_json:
                final_json[temp_node_number]['relations'].append({'relation_term': {sentence[1]: {'related_to': sentence[2]}}})
                final_json[temp_prev_node_number]['relations'].append({'relation_term': {sentence[1]: {'related_to': sentence[0]}}})
                final_json[temp_prev_node_number]['node_link'].append(temp_node_number)
                final_json[temp_node_number]['node_link'].append(temp_prev_node_number)

            if node_in_json and not second_node_in_json:
                final_json[temp_node_number]['relations'].append({'relation_term': {sentence[1]: {'related_to': sentence[2]}}})
                final_json[temp_node_number]['node_link'].append(prev_node_number)
                final_json[prev_node_number] = {'full_form': sentence[2], 'relations': [{'relation_term': {sentence[1]: {'related_to': sentence[0]}}}], 'node_link': [node_number]}
                node_number += 1

            if not node_in_json and second_node_in_json:
                final_json[node_number] = {'full_form': sentence[0],
                    'relations': [{'relation_term': {sentence[1]: {'related_to': sentence[2]}}}], 'node_link': [temp_prev_node_number]}
                node_number += 1

                final_json[temp_prev_node_number]['relations'].append({'relation_term': {sentence[1]: {'related_to': sentence[0]}}})
                final_json[temp_prev_node_number]['node_link'].append(node_number)

            if not node_in_json and not second_node_in_json:
                final_json[node_number] = {'full_form': sentence[0], 'relations': [{'relation_term': {sentence[1]: {'related_to': sentence[2]}}}], 'node_link': [prev_node_number]}
                final_json[prev_node_number] = {'full_form': sentence[2], 'relations': [{'relation_term': {sentence[1]: {'related_to': sentence[0]}}}], 'node_link': [node_number]}
                node_number += 1

            prev_node_number = node_number

        temp_container = []
        temp_dict = {}
        second_dict = {}
        prev_word = ""
        prev_dict_key = ""
        prev_words = []
        temp_node_number = 0
        dict_in_json = False
        for pair in sentence_pairing:
            for key, value in final_json.items():
                prev_dict_key = value['full_form']
                for word in pair:
                    if value['full_form'] == word:
                        if isinstance(word, list):
                            for instance in word:
                                prev_words.append(instance)
                            second_dict = {'relation_term': {prev_dict_key: {'related_to': prev_words}}}

                        if not isinstance(word, list):
                            second_dict = {'relation_term': {prev_dict_key: {'related_to': word}}}

                        dict_in_json = False
                        for key, value in final_json.items():
                            if second_dict in value['relations']:
                                temp_node_number = key
                                dict_in_json = True
                                break

                        if (len(prev_words) > 0 or not isinstance(word, list)) and prev_dict_key != "" and dict_in_json:
                            final_json[key]['relations'].append(second_dict)

                        if (len(prev_words) > 0 or not isinstance(word, list)) and prev_dict_key == "" and dict_in_json:
                            final_json[key]['relations'].append(second_dict)

                        if isinstance(word, list):
                            prev_dict_key = word[len(word) - 1]
                        else:
                            prev_dict_key = word

                        second_dict = {}
                        prev_words = []
                temp_dict = {}


        for pair in sentence_pairing:
            for key, value in final_json.items():
                prev_dict_key = value['full_form']
                pair_stripped = pair[2].split()
                result_words = [list_word for list_word in pair_stripped if list_word.lower() not in
                                        coreference_words and list_word.lower() not in number_values]
                pair_stripped = ' '.join(result_words)
                pair_stripped = filter(lambda x: not x.isdigit() or x.isspace(), pair_stripped)
                pair_stripped = pair_stripped.lstrip()

                if value['full_form'] == pair_stripped:
                    for word in pair:
                        if isinstance(word, list):
                            for instance in word:
                                prev_words.append(instance)
                            second_dict = {'relation_term': {prev_dict_key: {'related_to': prev_words}}}

                        if not isinstance(word, list):
                            second_dict = {'relation_term': {prev_dict_key: {'related_to': word}}}

                        if (len(prev_words) > 0 or not isinstance(word, list)) and prev_dict_key != "":
                            if second_dict not in final_json[key]['relations']:
                                final_json[key]['relations'].append(second_dict)
                        if (len(prev_words) > 0 or not isinstance(word, list)) and prev_dict_key == "":
                            if second_dict not in final_json[key]['relations']:
                                final_json[key]['relations'].append(second_dict)

                        if isinstance(word, list):
                            prev_dict_key = word[len(word) - 1]
                        else:
                            prev_dict_key = word

                        second_dict = {}
                        prev_words = []
                temp_dict = {}


        print (json.dumps(final_json, indent=2))