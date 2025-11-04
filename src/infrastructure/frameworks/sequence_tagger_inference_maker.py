from flair.data import Sentence
from src.domain.sentence_with_boundary import SentenceWithBoundary
from src.infrastructure.frameworks.model_inference_maker import ModelInferenceMaker
from src.infrastructure.frameworks.sequence_tagger_loader import SequenceTaggerLoader
from src.infrastructure.frameworks.somajo_tokenizer import SoMaJoTokenizer
from typing import List, Tuple

class SequenceTaggerInferenceMaker(ModelInferenceMaker):
    """
    This class implements the infer method to return the inference result with a Flair SequenceTagger model.
    """
    _somajo_tokenizer: SoMaJoTokenizer = None

    def __init__(self, model_loader: SequenceTaggerLoader):
        """
        :param model_loader: The SequenceTaggerLoader instance with the model object.
        """
        super().__init__(model_loader)
        self._load_somajo_tokenizer()
    
    def _load_somajo_tokenizer(self):
        """
        Load the SoMaJo tokenizer.
        """
        if self._somajo_tokenizer is None:
            self._somajo_tokenizer = SoMaJoTokenizer()

    def infer(self, input_text: str, **kwargs) -> List[SentenceWithBoundary]:
        """
        Make inference using the loaded SequenceTagger model.
        
        :param input_text: The input text for which inference is to be made.
        :param **kwargs: Additional keyword arguments for inference.
        :return: The inference result as a list of SentenceWithBoundary objects.
        """
        
        tagger = self.model_loader.load()
        sentences: List[SentenceWithBoundary] = self._get_sentences_with_boundaries(input_text)
        flair_sentences = [swb.sentence for swb in sentences]
        tagger.predict(flair_sentences)
        return sentences

    def _get_sentences_with_boundaries(self, original_text: str, buffer: int = 15) -> List[SentenceWithBoundary]:
        """
        Get flair sentences built with SoMaJo tokens along with sentence boundaries in the original text.
        :param original_text: The original text to process.
        :param buffer: The buffer size to use for sentence boundary detection.
        :return: List of SentenceWithBoundary objects
        """

        sentences_with_boundaries: List[SentenceWithBoundary] = list()
        text_for_tokenization = original_text.replace('\t', '!!!')
        sentences = self._somajo_tokenizer.tokenizer.tokenize_text([text_for_tokenization])
        offset: int = 0
        prev_end: int = 0
        for _, sentence in enumerate(sentences):
            potential_sentence_of_original_form = ""
            for token in sentence:
                token_text = token.text.replace('!!!', '')
                potential_sentence_of_original_form += token_text + (' ' if token.space_after and not token.last_in_sentence else '')
            
            start, end = self._get_potential_sentence_boundary(original_text, potential_sentence_of_original_form, offset, buffer)
            if start - prev_end > buffer:
                start, end = self._get_potential_sentence_boundary(original_text, potential_sentence_of_original_form, prev_end - buffer, buffer)
            prev_end = end
            
            sentences_with_boundaries.append(SentenceWithBoundary(Sentence(potential_sentence_of_original_form), start, end))
            offset = end
        
        if len(sentences_with_boundaries) > 1:
            idx = 0
            while idx < len(sentences_with_boundaries):
                swb = sentences_with_boundaries[idx]
                if swb.start == swb.end:
                    start_idx = idx
                    end_idx = idx
                    while end_idx + 1 < len(sentences_with_boundaries) and \
                        sentences_with_boundaries[end_idx + 1].start == sentences_with_boundaries[end_idx + 1].end:
                        end_idx += 1
                    
                    if start_idx > 0:
                        new_start = sentences_with_boundaries[start_idx - 1].end
                        for fix_idx in range(start_idx, end_idx + 1):
                            sentences_with_boundaries[fix_idx].start = max(new_start - buffer, 0)
                    
                    if end_idx + 1 < len(sentences_with_boundaries):
                        new_end = sentences_with_boundaries[end_idx + 1].start
                        for fix_idx in range(start_idx, end_idx + 1):
                            sentences_with_boundaries[fix_idx].end = min(new_end -1, len(original_text))
                    idx = end_idx + 1
                else:
                    idx += 1
        
        return sentences_with_boundaries
    
    def _get_potential_sentence_boundary(self,
                                         original_text: str,
                                         somajo_tokenized_sentence: str,
                                         offset: int = 0,
                                         buffer: int = 15) -> Tuple[int, int]:
        """
        Find sentence boundaries in the original text based on the SoMaJo tokenized sentence.
        
        :param original_text: The original text.
        :param somajo_tokenized_sentence: The SoMaJo tokenized sentence as a single string.
        :param offset: The offset to start searching from.
        :param buffer: Additional buffer length to consider when searching for the end token.

        :return: A tuple (start_index, end_index) representing the sentence boundaries.
        """

        tokens = [token for token in somajo_tokenized_sentence.split(' ') if token]
        if not tokens:
            return offset, offset

        start_stretch = tokens[0]
        final_stretch = tokens[-1]

        start_index = original_text.find(start_stretch, offset)
        if start_index == -1:
            return offset, offset
        
        expected_length = len(somajo_tokenized_sentence)
        search_end = min((start_index + expected_length + buffer), len(original_text))
    
        final_index = -1
        temp_offset = start_index
        
        while temp_offset < search_end:
            pos = original_text.find(final_stretch, temp_offset)
            if pos == -1 or pos + len(final_stretch) > search_end:
                break

            if pos >= start_index:
                temp_offset = pos + len(final_stretch)
                final_index = pos
            else:
                temp_offset = pos + 1

        if final_index != -1:
            final_index += len(final_stretch)
        else:
            final_index = min(start_index + expected_length, len(original_text))
            
        return start_index, final_index