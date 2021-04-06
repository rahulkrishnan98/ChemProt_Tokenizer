'''
file: tokenize.py
inputs,
1. Abstract sentence list - [[sent1], [sent2]]
2. Entity list - [[start_ind, end_ind, tag], ..]

output,
1. Words, tags - tokenized and tagged
'''
import re
from tqdm import tqdm

class Tokenize:
    def __init__(
        self, 
        delimiter,
        sentence_list,
        entity_list
    ):
        self.delimiter = delimiter
        self.sentence_list = sentence_list
        self.entity_list = entity_list
        self.words, self.tags = [], []

    def expand(
        self,
        words,
        tag,
        delimiter,
        start
    ):
        '''
        Expand the word with the tag after delimiter tokenize
        '''
        res = []
        for m in re.finditer(delimiter, words):
            res.append(
                [
                    start+ m.start(), start+ m.end() -1, m.group(), tag
                ]
            )
       
        return res



    def tokenize(self):
        for _, (sent, entities) in tqdm(enumerate(zip(self.sentence_list, self.entity_list))):
            '''
            Corner Cases
            1. multiple tag at varying lengths
            eg: 
                Sent: this is a Acyl-1 Dopamine
                Entity1: Chemical -> Acyl-1
                Entity2: GENE -> Acyl-1 Dopamine
            Solution:
                visited matrix maintained,
                Select only first occurance 
                    >> Only take if visited is false
            2. How to reconcile the extracted ones with 
            rest of sent?
            Solution:
                split using delimiter on whole sent and hit 
                the tok_sent to see if your target word
                has an entity mentioned, otherwise JUNK
            3. If the entity extracted is a sub-word, algo 
            breaks.
            eg:
                this is a subWord example
                entity: sub
            Reason: Since we are not looking smaller un-tokenized parts

            Solution:
                Index check in the algo, stops it from breaking, but
                this also means it will skip it altogether.
                God save us.    
            '''

            visited = [False]*len(sent[0])
            tok_sent = []
            for _, (start, end, word_, tag_) in enumerate(entities):
                if True in visited[start: end+1]:
                    #means, its already a part of another tag
                    continue
                else:
                    visited[start: end+1] = [True]*(end+1 - start)
                    tok_sent.append(
                        self.expand(
                            sent[0][start: end+1],
                            tag_,
                            self.delimiter,
                            start              
                        )
                    )

            temp_tags, temp_words = [], []
            for m in re.finditer(self.delimiter, sent[0]):
                flg = False
                st_ind, end_ind, word = m.start(), m.end(), m.group()
                #iterate through the target groups to see if it exists
                for _, val in enumerate(tok_sent):
                    for _, inn in enumerate(val):
                        st_, end_, wd_, tag_ = inn
                        if st_== st_ind and end_ind-1 == end_ and word == wd_:
                            #there is an associated tag
                            temp_tags.append(tag_)
                            temp_words.append(word)
                            flg = True
                if not flg:
                    temp_words.append(word)
                    temp_tags.append("JUNK")
            
            self.tags.append(temp_tags)
            self.words.append(temp_words)
        
        return (self.words, self.tags)
