# -*- coding: utf-8 -*-
import spacy
import re
from spacy import displacy
from string import digits


coreference_words = ["they", "them", "their", "it", "its", "she", "he", "her", "hers", "his", "herself",
                     "himself"]
number_values = ["million", "billion", "thousand", "hundred", "hundreds", "millions", "thousands", "billions"]

immediate_coreference_words = ["who", "that"]

nlp = spacy.load('en_core_web_sm')

s = (u"When it comes to entertainment programming, they spend less than a third of their screen time on "
          u"traditional television, and the rest of their hours on a mix of Netflix, YouTube and other streaming "
          u"services, according to a survey by the media company Awesomeness. To reach them, creators compete with "
          u"other professionals and also with the everyday people who fill up social-media feeds, giving them a matter"
          u" of seconds to prove a piece of content is worth a longer look. Two years after introducing herself on "
          u"YouTube with a squirrel impression, Ms. Koshy has cracked the code, accumulating 1.6 billion views and the "
          u"advertising business that chases those numbers. The entrepreneur strategy presents a way forward for "
          u"entertainment companies and marketers, who have flocked to Ms. Koshy expanding brand. The latest placement:"
          u" a series of comical advertisements for Apple Inc.‚Äôs Beats earphones that play on her fast rise and "
          u"obsessive fans. Online, her Beats ads have four times the rate of clicks for those starring other "
          u"celebrities, including quarterback Tom Brady, Apple says.")

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

for chunk in doc.noun_chunks:
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

    '''print(token.text, token.dep_, token.head.text, token.head.pos_,
          [child for child in token.children])'''
'''take data, capture linking from following links, map in a json'''
'''for link in entity_links:
    print(link)
    print("\n")'''

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

joined_phrase = ""
sentence_pairing = []
found = False
for phrase in conj_vec:
    for value in phrase:
        for sentence in sentences:
            for word in sentence:
                sentence_words = word.split()
                result_words = [list_word for list_word in sentence_words if list_word.lower() not in
                                coreference_words and list_word.lower() not in number_values]
                word = ' '.join(result_words)
                if len(value) > 0:
                    if len(value) >= 1:
                        joined_phrase = ' '.join(map(str, value))
                    word = filter(lambda x: x.isalpha() or x.isspace(), word)
                    word = word.lstrip()
                    if word != sentence[1] and (word in joined_phrase):
                        sentence_pairing.append(sentence + phrase)
                        break

print "\n"
print "Identified relations: "
for pair in sentence_pairing:
    print pair

print "\n"
print "Identified links: "
for sentence in sentences:
    print sentence


