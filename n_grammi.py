from collections import Counter

def genera_ngrammi(text, n):
    ngrams = []
    for i in range(len(text) - n + 1):
        ngrams.append(text[i:i+n])
    return ngrams

def calcolo_frequenza_relativa(text, n): # dato un testo in input restituisco un dizionario con le frequenze relative degli n-grammi nel testo
    """
    Calcola la frequenza relativa degli n-grammi in un testo dato.

    :param text: testo in input
    :param n: lunghezza dell'n-grammo considerato
    :return: un dizionario con n-grammi come chiave e frequenza relativa come valore
    """
    ngrams = genera_ngrammi(text, n)
    ngram_conteggio = Counter(ngrams)
    total_ngrams = sum(ngram_conteggio.values())
    return {ngram: count/total_ngrams for ngram, count in ngram_conteggio.items()}

def calcolo_distanza(text_x, testi_autore, n):
    """
    Calcola la distanza tra un testo generico e un testo di un autore dato

    :param text_x: testo da comparare
    :param author_texts: testi concatenati di un autore
    :param n: lunghezza dell'n-grammo considerato
    :return: la misura della distanza d_n^K(x, A)
    """
    if not text_x or not testi_autore:
        return None

    freq_x = calcolo_frequenza_relativa(text_x, n)
    freq_A = calcolo_frequenza_relativa(testi_autore, n)

    all_ngrams = set(freq_x.keys()).union(set(freq_A.keys())) # creo un insieme con tutti gli elementi presenti sia in X che nei testi dell'autore A
    tot_unique_ngrams = len(all_ngrams)
    distanza = 0.0
    for ngram in all_ngrams:
        f_x = freq_x.get(ngram, 0.0) # estraggo il valore associato alla chiave ngram, se non esiste tale chiave restituisco 0
        f_A = freq_A.get(ngram, 0.0)
        numerator = (f_A - f_x) ** 2
        denominator = (f_A + f_x) ** 2
        if denominator > 0:
            distanza += numerator / denominator

    return distanza/tot_unique_ngrams #  così restituisco un numero rinormalizzato

# Esempio d'uso
testo_x = "Esempio di testo per il calcolo degli n-grammi."
testi_autore_A = "Concatenazione di tutti i testi dell'autore A."
testi_autore_B = "Concatenazione di tutti i testi dell'autore B."
# Lunghezza degli n-grammi
n = 3

# Calcola la distanza
distanza = calcolo_distanza(testo_x, testi_autore_A, n)
distanza2 = calcolo_distanza(testi_autore_B, testi_autore_A, n)

#print(f"Distanza: {distanza}") # siccome sono diversi la distanza è prossima a 1
#print(f"Distanza: {distanza2}") # siccome sono quasi uguali la distanza è molto bassa


