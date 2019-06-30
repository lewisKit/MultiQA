import json
from datasets.multiqa_dataset import MultiQA_DataSet
from overrides import overrides
from allennlp.common.file_utils import cached_path
from common.uuid import gen_uuid
import tqdm


class SQuAD(MultiQA_DataSet):
    """

    """

    def __init__(self):
        self.DATASET_NAME = 'SQuAD'

    @overrides
    def build_header(self, contexts, split, preprocessor ):
        header = {}

        return header

    @overrides
    def build_contexts(self, split, preprocessor, sample_size):
        single_file_path = cached_path("https://raw.githubusercontent.com/rajpurkar/SQuAD-explorer/master/dataset/" + \
                                       split + "-v2.0.json")

        with open(single_file_path, 'r') as myfile:
            original_dataset = json.load(myfile)

        contexts = []
        data = original_dataset['data']


        for topic in tqdm.tqdm(data, total=len(data), ncols=80):
            for paragraph in topic['paragraphs']:
                qas = []
                for qa in paragraph['qas']:
                    new_qa = {'qid':self.DATASET_NAME + '_q_' + qa['id'],
                                'question':qa['question']}
                    answer_candidates = []
                    if qa['is_impossible']:
                        new_qa['answers'] = {"open-ended": {'cannot_answer': 'yes'}}
                        new_qa['metadata'] = {'plausible_answers': qa['plausible_answers']}
                    else:
                        for answer_candidate in qa['answers']:
                            answer_candidates.append({'extractive':{"single_answer":{"answer": answer_candidate['text'],
                                "instances": [{'doc_id':0,
                                           'doc_part':'text',
                                           'start_byte':answer_candidate['answer_start'],
                                           'text':answer_candidate['text']}]}}})
                        new_qa['answers'] = {"open-ended": {'answer_candidates': answer_candidates}}
                    qas.append(new_qa)

                contexts.append({"id": self.DATASET_NAME + '_'  + gen_uuid(),
                                 "context": {"documents": [{"text": paragraph['context'],
                                                            "title":topic['title']}]},
                                 "qas": qas})


        if sample_size != None:
            contexts = contexts[0:sample_size]
        contexts = preprocessor.tokenize_and_detect_answers(contexts)

        # detect answers

        # save dataset

        return contexts