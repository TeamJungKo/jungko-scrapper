from collections import defaultdict
import math
import numpy as np

class KRWordRank:
    """Unsupervised Korean Keyword Extractor

    Implementation of Kim, H. J., Cho, S., & Kang, P. (2014). KR-WordRank: 
    An Unsupervised Korean Word Extraction Method Based on WordRank. 
    Journal of Korean Institute of Industrial Engineers, 40(1), 18-33.

    Arguments
    ---------
    min_count : int
        Minimum frequency of subwords used to construct subword graph
        Default is 5
    max_length : int
        Maximum length of subwords used to construct subword graph
        Default is 10
    verbose : Boolean
        If True, it shows training status
        Default is False

    Usage
    -----
        >>> from krwordrank.word import KRWordRank

        >>> texts = ['예시 문장 입니다', '여러 문장의 list of str 입니다', ... ]
        >>> wordrank_extractor = KRWordRank()
        >>> keywords, rank, graph = wordrank_extractor.extract(texts, beta, max_iter, verbose)
    """
    def __init__(self, min_count=2, max_length=5, verbose=False):
        self.min_count = min_count
        self.max_length = max_length
        self.verbose = verbose
        self.sum_weight = 1
        self.vocabulary = {}
        self.index2vocab = []

    def scan_vocabs(self, docs):
        """
        It scans subwords positioned of left-side (L) and right-side (R) of words.
        After scanning was done, KR-WordRank has index2vocab as class attribute.

        Arguments
        ---------
        docs : list of str
            Sentence list

        Returns
        -------
        counter : dict
            {(subword, 'L')] : frequency}
        """
        self.vocabulary = {}
        if self.verbose:
            print('scan vocabs ... ')

        counter = {}
        for doc in docs:

            for token in doc.split():
                len_token = len(token)
                counter[(token, 'L')] = counter.get((token, 'L'), 0) + 1

                for e in range(1, min(len(token), self.max_length)):
                    if (len_token - e) > self.max_length:
                        continue

                    l_sub = (token[:e], 'L')
                    r_sub = (token[e:], 'R')
                    counter[l_sub] = counter.get(l_sub, 0) + 1
                    counter[r_sub] = counter.get(r_sub, 0) + 1

        counter = {token:freq for token, freq in counter.items() if freq >= self.min_count}
        for token, _ in sorted(counter.items(), key=lambda x:x[1], reverse=True):
            self.vocabulary[token] = len(self.vocabulary)

        self._build_index2vocab()

        if self.verbose:
            print('num vocabs = %d' % len(counter))
        return counter

    def _build_index2vocab(self):
        self.index2vocab = [vocab for vocab, index in sorted(self.vocabulary.items(), key=lambda x:x[1])]
        self.sum_weight = len(self.index2vocab)
    
    def extract(self, docs, beta=0.75, max_iter=10, num_keywords=-1,
        num_rset=-1, vocabulary=None, bias=None, rset=None):
        """
        It constructs word graph and trains ranks of each node using HITS algorithm.
        After training it selects suitable subwords as words.

        Arguments
        ---------
        docs : list of str
            Sentence list.
        beta : float
            PageRank damping factor. 0 < beta < 1
            Default is 0.85
        max_iter : int
            Maximum number of iterations of HITS algorithm.
            Default is 10
        num_keywords : int
            Number of keywords sorted by rank.
            Default is -1. If the vaule is negative, it returns all extracted words.
        num_rset : int
            Number of R set words sorted by rank. It will be used to L-part word filtering.
            Default is -1.
        vocabulary : None or dict
            User specified vocabulary to index mapper
        bias : None or dict
            User specified HITS bias term
        rset : None or dict
            User specfied R set

        Returns
        -------
        keywords : dict
            word : rank dictionary. {str:float}
        rank : dict
            subword : rank dictionary. {int:float}
        graph : dict of dict
            Adjacent subword graph. {int:{int:float}}

        Usage
        -----
            >>> from krwordrank.word import KRWordRank

            >>> texts = ['예시 문장 입니다', '여러 문장의 list of str 입니다', ... ]
            >>> wordrank_extractor = KRWordRank()
            >>> keywords, rank, graph = wordrank_extractor.extract(texts, beta, max_iter, verbose)
        """

        rank, graph = self.train(docs, beta, max_iter, vocabulary, bias)

        lset = {self.int2token(idx)[0]:r for idx, r in rank.items() if self.int2token(idx)[1] == 'L'}
        if not rset:
            rset = {self.int2token(idx)[0]:r for idx, r in rank.items() if self.int2token(idx)[1] == 'R'}

        if num_rset > 0:
            rset = {token:r for token, r in sorted(rset.items(), key=lambda x:-x[1])[:num_rset]}

        keywords = self._select_keywords(lset, rset)
        keywords = self._filter_compounds(keywords)
        keywords = self._filter_subtokens(keywords)

        if num_keywords > 0:
            keywords = {token:r for token, r in sorted(keywords.items(), key=lambda x:-x[1])[:num_keywords]}

        return keywords, rank, graph

    def _select_keywords(self, lset, rset):
        keywords = {}
        for word, r in sorted(lset.items(), key=lambda x:x[1], reverse=True):
            len_word = len(word)
            if len_word == 1:
                continue

            is_compound = False
            for e in range(2, len_word):
                if (word[:e] in keywords) and (word[:e] in rset):
                    is_compound = True
                    break

            if not is_compound:
                keywords[word] = r

        return keywords

    def _filter_compounds(self, keywords):
        keywords_= {}
        for word, r in sorted(keywords.items(), key=lambda x:x[1], reverse=True):
            len_word = len(word)

            if len_word <= 2:
                keywords_[word] = r
                continue

            if len_word == 3:
                if word[:2] in keywords_:
                    continue

            is_compound = False
            for e in range(2, len_word - 1):
                # fixed. comment from Y. cho
                if (word[:e] in keywords) and (word[e:] in keywords):
                    is_compound = True
                    break

            if not is_compound:
                keywords_[word] = r

        return keywords_

    def _filter_subtokens(self, keywords):
        subtokens = set()
        keywords_ = {}

        for word, r in sorted(keywords.items(), key=lambda x:x[1], reverse=True):
            subs = {word[:e] for e in range(2, len(word)+1)}

            is_subtoken = False
            for sub in subs:
                if sub in subtokens:
                    is_subtoken = True
                    break

            if not is_subtoken:
                keywords_[word] = r
                subtokens.update(subs)

        return keywords_

    def train(self, docs, beta=0.85, max_iter=10, vocabulary=None, bias=None):
        """
        It constructs word graph and trains ranks of each node using HITS algorithm.
        Use this function only when you want to train rank of subwords

        Arguments
        ---------
        docs : list of str
            Sentence list.
        beta : float
            PageRank damping factor. 0 < beta < 1
            Default is 0.85
        max_iter : int
            Maximum number of iterations of HITS algorithm.
            Default is 10
        vocabulary : None or dict
            User specified vocabulary to index mapper
        bias : None or dict
            User specified HITS bias term
            {str: float} Format

        Returns
        -------
        rank : dict
            subword : rank dictionary. {int:float}
        graph : dict of dict
            Adjacent subword graph. {int:{int:float}}
        """
        if (not vocabulary) and (not self.vocabulary):
            self.scan_vocabs(docs)
        elif (not vocabulary):
            self.vocabulary = vocabulary
            self._build_index2vocab()

        graph = self._construct_word_graph(docs)

        # add custom bias dict
        encoded_bias = {}
        custom_bias_dict = bias

        if custom_bias_dict:
            for word, value in custom_bias_dict.items():
                encoded_word = self.token2int((word, 'L'))
                if encoded_word != -1:
                    encoded_bias[encoded_word] = value

        rank = hits(graph, beta, max_iter, encoded_bias,
                    sum_weight=self.sum_weight,
                    number_of_nodes=len(self.vocabulary),
                    verbose=self.verbose
                    )

        return rank, graph

    def token2int(self, token):
        """
        Arguments
        ---------
        token : tuple
            (subword, 'L') or (subword, 'R')
            For example, ('이것', 'L') or ('은', 'R')

        Returns
        -------
        index : int
            Corresponding index
            If it is unknown, it returns -1
        """
        return self.vocabulary.get(token, -1)

    def int2token(self, index):
        """
        Arguments
        ---------
        index : int
            Token index

        Returns
        -------
        token : tuple
            Corresponding index formed such as (subword, 'L') or (subword, 'R')
            For example, ('이것', 'L') or ('은', 'R').
            If it is unknown, it returns None
        """
        return self.index2vocab[index] if (0 <= index < len(self.index2vocab)) else None

    def _intra_link(self, token):
        links = []
        len_token = len(token)
        for e in range(1, min(len_token, 10)):
            if (len_token - e) > self.max_length:
                continue
            links.append( ((token[:e], 'L'), (token[e:], 'R')) )
        return links

    def _inter_link(self, tokens):
        def rsub_to_token(t_left, t_curr):
            return [((t_left[-b:], 'R'), (t_curr, 'L')) for b in range(1, min(10, len(t_left)))]
        def token_to_lsub(t_curr, t_rigt):
            return [((t_curr, 'L'), (t_rigt[:e], 'L')) for e in range(1, min(10, len(t_rigt)))]

        links = []
        for i in range(1, len(tokens)-1):
            links += rsub_to_token(tokens[i-1], tokens[i])
            links += token_to_lsub(tokens[i], tokens[i+1])
        return links

    def _check_token(self, token_list):
        return [(token[0], token[1]) for token in token_list if (token[0] in self.vocabulary and token[1] in self.vocabulary)]

    def _encode_token(self, token_list):
        return [(self.vocabulary[token[0]],self.vocabulary[token[1]]) for token in token_list]
