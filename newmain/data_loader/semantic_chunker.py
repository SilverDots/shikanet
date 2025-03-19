import pandas as pd
from loader import ChatDB

class SemanticChunkedChatDB(ChatDB):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(self.data.head())




# text_splitter = SemanticChunker(
#   embed_model,
#   add_start_index=True,
#   breakpoint_threshold_type='percentile',
#   breakpoint_threshold_amount=90.,
#   min_chunk_size=3
# )

# def split_text_w_indices(
#     self,
#     text: str,
#     join_char: str = '\n'
# ):
#     start_indices = [0]

#     # Splitting the essay (by default on '.', '?', and '!')
#     single_sentences_list = re.split(self.sentence_split_regex, text)

#     # having len(single_sentences_list) == 1 would cause the following
#     # np.percentile to fail.
#     if len(single_sentences_list) == 1:
#         return single_sentences_list, start_indices
#     # similarly, the following np.gradient would fail
#     if (
#         self.breakpoint_threshold_type == "gradient"
#         and len(single_sentences_list) == 2
#     ):
#         return single_sentences_list, start_indices
#     distances, sentences = self._calculate_sentence_distances(single_sentences_list)
#     if self.number_of_chunks is not None:
#         breakpoint_distance_threshold = self._threshold_from_clusters(distances)
#         breakpoint_array = distances
#     else:
#         (
#             breakpoint_distance_threshold,
#             breakpoint_array,
#         ) = self._calculate_breakpoint_threshold(distances)

#     indices_above_thresh = [
#         i
#         for i, x in enumerate(breakpoint_array)
#         if x > breakpoint_distance_threshold
#     ]

#     chunks = []

#     # Iterate through the breakpoints to slice the sentences
#     for index in indices_above_thresh:
#         # The end index is the current breakpoint
#         end_index = index

#         # Slice the sentence_dicts from the current start index to the end index
#         group = sentences[start_indices[-1] : end_index + 1]
#         combined_text = join_char.join([d["sentence"] for d in group])
#         # If specified, merge together small chunks.
#         if (
#             self.min_chunk_size is not None
#             and len(combined_text) < self.min_chunk_size
#         ):
#             continue
#         chunks.append(combined_text)

#         # Update the start index for the next group
#         start_indices.append(index + 1)

#     # The last group, if any sentences remain
#     if start_indices[-1] < len(sentences):
#         combined_text = join_char.join([d["sentence"] for d in sentences[start_indices[-1]:]])
#         chunks.append(combined_text)
#     return chunks, start_indices

# text_splitter.split_text_w_indices = MethodType(split_text_w_indices, text_splitter)