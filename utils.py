import re
from datasets import load_from_disk

def texts(path='./DataSet/article_2634.txt'):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
    except:
        text = None
        print("File is not exists")
    return text

def load_saved_dataset(dataset_path):
    """
    Load a saved dataset from the specified path.
    
    Args:
        dataset_path (str): The path to the saved dataset.
        
    Returns:
        dataset: The loaded dataset.
    """
    dataset = load_from_disk(dataset_path)
    texts = ""
    for text in dataset['train']['text']:
        texts += text+"<end>"
    return texts

# مسار مجلد البيانات المحفوظة
saved_dataset_path = "./data"

# تحميل مجموعة البيانات المحفوظة
loaded_dataset = load_saved_dataset(saved_dataset_path)
text = loaded_dataset

# here are all the unique characters that occur in this text
chars = sorted(list(set(text)))
vocab_size = len(chars)
# create a mapping from characters to integers
stoi = {ch: i for i, ch in enumerate(chars)}
itos = {i: ch for i, ch in enumerate(chars)}
# encoder: take a string, output a list of integers
def encode(s): return [stoi[c] for c in s]
# decoder: take a list of integers, output a string
def decode(l): return ''.join([itos[i] for i in l])


def text_standardize(text):
    text = text.replace('—', '-')
    text = text.replace('–', '-')
    text = text.replace('―', '-')
    text = text.replace('…', '...')
    text = text.replace('´', "'")
    text = re.sub(
        '''(-+|~+|!+|"+|;+|\?+|\++|,+|\)+|\(+|\\+|\/+|\*+|\[+|\]+|}+|{+|\|+|_+)''', r' \1 ', text)
    text = re.sub('\s*\n\s*', ' \n ', text)
    text = re.sub('[^\S\n]+', ' ', text)
    return text.strip()
