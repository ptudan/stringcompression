import re
import csv
import sys

def load_file_to_string(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"The file {file_path} does not exist.")
        sys.exit(1)
    except IOError:
        print(f"An error occurred while reading the file {file_path}.")
        sys.exit(1)

def create_frequency_map(csv_file_path, initial_rankings, loop_limit_ct):
    frequency_map = {}
    
    for i, word in enumerate(initial_rankings):
        frequency_map[word] = i  
    
    csv_starting_rank = len(initial_rankings)

    try:
        with open(csv_file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            
            next(reader, None)  
            loop_limit = loop_limit_ct - csv_starting_rank

            added = 0
            for i, row in enumerate(reader):
                if i == loop_limit:
                    break  
                word, count = row
                if(len(word) == 1 and added < 10 or len(word) == 2 and added < 100 or len(word) == 3 and added < 1000 or len(word) == 4 and added < 10000 or len(word) == 3 and added < 100000):
                    continue
                frequency_map[word] = added + csv_starting_rank 
                added += 1

    except FileNotFoundError:
        print(f"The file {csv_file_path} does not exist.")
        sys.exit(1)
    except IOError:
        print(f"An error occurred while reading the file {csv_file_path}.")
        sys.exit(1)

    return frequency_map

def string_compress(input_string, word_freq_map):
    # Replace all double spaces with single spaces
    input_string = input_string.replace('  ', ' ')

    # Prepare the words by splitting the string into words for iteration
    words = input_string.split(' ')

    # This list will hold the processed words
    processed_words = []

    # Helper function to determine if a word starts with a capital letter
    def starts_with_capital(word):
        if word:
            return word[0].isupper()
        return False

    # Helper function to check if a string starts or ends with a punctuation
    def starts_or_ends_with_punctuation(word):
        return bool(re.match(r'^\W|\W$', word))
    
    words_replaced = 0
    total_words = 0

    for word in words:
        total_words += 1
        original_word = word.strip()
        punctuation_prefix = punctuation_suffix = ''

        # If the word starts or ends with punctuation, we separate the punctuation
        if starts_or_ends_with_punctuation(original_word):
            match = re.match(r'(^\W*)(.*?)(\W*$)', original_word)
            if match:
                punctuation_prefix, original_word, punctuation_suffix = match.groups()

        # Check if the word is in the word frequency map
        lower_word = original_word.lower()
        if lower_word in word_freq_map:
            words_replaced += 1
            replacement = str(word_freq_map[lower_word])  # This will be the replacement from the map

            # Applying different rules for formatting the replacement
            if starts_with_capital(original_word):
                processed_word = '   ' + replacement
            else:
                processed_word = '  ' + replacement

            # If there was a punctuation at the start, we include it before spaces
            processed_word = punctuation_prefix + processed_word

            # If there was a punctuation at the end, we include it after the number (with a space)
            if punctuation_suffix:
                processed_word += ' ' + punctuation_suffix

            processed_words.append(processed_word)
        else:
            # If the word is not in the map, we append it as it is, along with any separated punctuation
            processed_words.append(punctuation_prefix + original_word + punctuation_suffix)

    output_string = ''.join(processed_words)

    return output_string, words_replaced, total_words

def print_byte_sizes(original_string, word_freq_map):
    # Compress the string
    compressed_string, words_replaced, total_words = string_compress(original_string, word_freq_map)

    # Encode the strings in UTF-8
    original_bytes = original_string.encode('utf-8')
    compressed_bytes = compressed_string.encode('utf-8')

    # Calculate and print the byte sizes
    original_byte_size = sys.getsizeof(original_bytes)
    compressed_byte_size = sys.getsizeof(compressed_bytes)

    print(f"- {words_replaced} words replaced out of {total_words}. {100 *((words_replaced) /total_words):.4f}% replacement")
    print(f"- Original string byte size: {original_byte_size} bytes")
    print(f"- Compressed string byte size: {compressed_byte_size} bytes. {100 - 100 *(original_byte_size /compressed_byte_size):.4f}% reduction")

def build_string_from_tsv(file_path):
    """
    Read data from a TSV file and concatenate the last field from each row.

    :param file_path: str, path to the TSV file.
    :return: str, concatenated result.
    """
    # The string to be built from the file content.
    result_string = ''

    try:
        # Open the TSV file.
        with open(file_path, 'r', newline='', encoding='utf-8') as tsvfile:
            # Create a CSV reader specified for TSV format.
            reader = csv.reader(tsvfile, delimiter='\t')

            # Iterate over each row in the TSV file.
            for row in reader:
                if row:  # Ensure row is not empty
                    # Concatenate the last field to the result string.
                    result_string += row[-1] + ' '  # Adding a space for separation between texts

        # Return the constructed string, removing the trailing space.
        return result_string.rstrip()

    except FileNotFoundError:
        print(f"The file {file_path} does not exist.")
        return None  # You can also choose to raise the exception depending on your error handling.
    except IOError:
        print(f"An error occurred while reading the file {file_path}.")
        return None  # Similar as above, depends on how you prefer to handle errors.


def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_text_file> (is_tsv)")
        sys.exit(1)

    text_file_path = sys.argv[1]  

    texts = []
    files = []
    if len (sys.argv) > 2:
        if sys.argv[2] == True:
            texts.append(build_string_from_tsv(text_file_path))
        else:
            files = text_file_path.split(',')
            for f in files:    
                texts.append(load_file_to_string(f))
    else:
        text = load_file_to_string(text_file_path)

    csv_file_path = 'unigram_freq.csv'

    initial_rankings = []  # ... and so on

    # round digits are for  raw unicode strategy, powers of 2 are for theorizing about lower level strategy in readme
    sizes_to_try = [10, 64, 100, 1000, 10000, 16448, 100000]
    for i, t in enumerate(texts):
        print(f"{files[i]}:")
        for s in sizes_to_try:
            print(f"for {s} size list:")
            word_frequency_map = create_frequency_map(csv_file_path, initial_rankings, s)
            print_byte_sizes(t, word_frequency_map)
            print()
        print()

if __name__ == "__main__":
    main()

