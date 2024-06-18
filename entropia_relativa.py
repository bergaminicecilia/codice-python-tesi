import zlib


# uso le ridondanze interne al testo per scriverne una versione più corta
def entropia_relativa(text_A, text_X):
    if not text_A or not text_X:
        return None
    compressed_A_X = zlib.compress(text_A.encode() + text_X.encode())  # Comprimi il testo A + X
    compressed_A = zlib.compress(text_A.encode())  # Comprimi solo il testo A

    # Calcola l'entropia relativa: diff tra lunghezza di A+X compresso e A compresso divisa per la lunghezza di X
    # tanto + piccolo quante più parti di X vengono trovate in A
    relative_entropy = (len(compressed_A_X) - len(compressed_A)) / len(text_X)

    return relative_entropy


"""
text_A = "Questo è il testo A."
text_X = "Questo è il testo X."
text_X2 = "Non so che scrivere"
entropy = relative_entropy(text_A, text_X)
entropy2 = relative_entropy(text_A, text_X2)
print("Entropia relativa tra il testo X e il testo A:", entropy)  # valore basso di entropia => molte parti di X sono presenti in A
print("Entropia relativa tra il testo X2 e il testo A:", entropy2)  # valore alto => testo X2 e A sono molto diversi
"""
