from lib.chunker_lib import split_into_chunks, estimate_tokens

text = "one two three four five six seven"
chunks = split_into_chunks(text, max_words_per_chunk=3)
print(chunks)
print([estimate_tokens(c) for c in chunks])