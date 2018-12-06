# -*- coding: utf-8 -*-
import spacy
import re
from spacy import displacy

coreference_words = ["they", "them", "their", "it", "its", "she", "he", "her", "hers", "his", "herself",
                     "himself"]

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
s = s.replace(',', '')

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

'''for token in doc:
    print(token.text, token.dep_, token.head.text, token.head.pos_,
          [child for child in token.children])'''

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
for token in doc:
    for head in immediate_coreference_words:
        if re.match(head, token.text):
            if str(prev_token_dep_) == "nsubj" or str(prev_token_dep_) == "conj" or str(prev_token_dep_) == "dobj" or \
                    str(prev_token_dep_) == "pobj":
                print("FOUND:")
                print(str(prev_prev_token))
                print(str(prev_token))
                print(str(token.text))
                print ("\n")

    prev_prev_token = prev_token
    prev_prev_token_dep = prev_token_dep_
    prev_token = token.text
    prev_token_dep_ = token.dep_


for sentence in sentences:
    print (sentence)

