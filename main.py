from entropia_relativa import entropia_relativa
from n_grammi import calcolo_distanza
from Bio import Entrez  # modulo di BioPython per l'accesso a database biologici (PubMed)
import xml.etree.ElementTree as ET  # per parsing xml
from collections import defaultdict  # gestione dei gruppi di articoli
import logging

# Configura il logging -> per tracciare gli errori e le info di debug
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Funzione per cercare un articolo su PubMed Central attraverso l'identificatore pmcid, restituisce testo e autori
def estrai_articolo_con_id(pmcid):
    Entrez.email = "cecilia.bergamini.02@gmail.com"
    try:
        handle = Entrez.efetch(db="pmc", id=pmcid, rettype="xml", retmode="xml")  # recupero l'articolo in formato xml
        articolo_xml = handle.read()  # memorizzo il contenuto in una stringa
        handle.close()

        # converto in una struttura ad albero di elementi xml
        root = ET.fromstring(articolo_xml)

        # Estrazione del testo completo dell'articolo e delle informazioni sull'autore
        # authors usa un list comprehension per trovare tutti gli elementi <contrib> situati sotto ogni <contrib-group> nel documento xml
        testo_articolo = "".join(root.itertext())
        autori = [autore.findtext('name') for autore in root.findall('.//contrib-group/contrib')]

        # verifico se il testo contiene solo spazi bianchi oppure non ha autori
        if not testo_articolo.strip() or not autori:
            return None

        return {'text': testo_articolo, 'authors': autori} # restituisco un dizionario con testi e autori
    except Exception as e:
        logging.error(f"Errore nell'estrazione dell'articolo con ID {pmcid}: {e}")
        return None


# Funzione per caricare articoli da PubMed Central in base a un parametro di ricerca specifico <term>
def estrai_articoli_pubmed(term, max_count=150):
    Entrez.email = "cecilia.bergamini.02@gmail.com"
    try:
        handle = Entrez.esearch(db="pmc", term=term, retmax=max_count) # ricerca nel database pmc usando <term> limitando il numero massimo di articoli restituiti
        record = Entrez.read(handle)
        handle.close()

        if 'IdList' in record:
            ids = record['IdList'] # estrazione della lista degli id degli articoli
            articoli = []
            for pmcid in ids: # per ogni id nella lista ids
                articolo = estrai_articolo_con_id(pmcid)
                if articolo: # se l'aticolo è recuperato con successo
                    articoli.append(articolo)
                else:
                    logging.warning(f"Mancato salvataggio dell'articolo con ID {pmcid} a causa di errore di estrazione o contenuto invalido.")
            return articoli
        else:
            logging.info("Nessun articolo trovato.")
            return []
    except Exception as e:
        logging.error(f"Errore durante la ricerca su PubMed Central: {e}")
        return []


# Funzione per raggruppare gli articoli per autore o gruppi di autori
def raggruppamento_autori(articoli):
    gruppo_autori = defaultdict(list) # creazione di un dizionario con lista vuota come valore predefinito per nuove chiavi

    for articolo in articoli:
        if articolo and articolo['authors'] and articolo['text']:  # verifica che l'articolo non sia None e abbia autori e testo
            author_key = tuple(sorted(articolo['authors']))
            gruppo_autori[author_key].append(articolo['text'])
        else:
            logging.warning("Saltato un articolo trovato senza autori o testo.")
    return gruppo_autori


if __name__ == "__main__":
    try:
        articoli = estrai_articoli_pubmed("diabetes", max_count=150)

        if not articoli:
            logging.info("Nessun articolo estratto.")
        else:
            # Raggruppa gli articoli per autore
            gruppo_autori = raggruppamento_autori(articoli)

            # Seleziona il primo gruppo di autori che abbia almeno 50 articoli
            gruppo_selezionato = None
            for autori, testi in gruppo_autori.items():
                if len(testi) >= 10:
                    gruppo_selezionato = testi[:10]
                    break

            if gruppo_selezionato is not None:
                for testo in gruppo_selezionato:
                    print(testo)
            else:
                print("Nessun gruppo selezionato con almeno 10 articoli.")


            if not gruppo_selezionato:
                logging.info("Nessun gruppo di autori trovato con 10 pubblicazioni.")
            else:
                #other_articles = [article['text'] for article in articles if article and article['text'] and article['text'] not in selected_group][:10]
                articoli_validi = []
                for articolo in articoli:
                    if articolo and articolo['text']:  # Verifica che l'articolo esista e abbia un testo
                        articoli_validi.append(articolo)

                altri_articoli = []
                for articolo in articoli_validi:
                    if articolo['text'] not in gruppo_selezionato:  # Verifica che il testo dell'articolo non sia già nel gruppo selezionato
                        altri_articoli.append(articolo['text'])
                        if len(altri_articoli) >= 10:  # Limita a un massimo di 10 articoli
                            break

                if not altri_articoli:
                    logging.info("Non sono stati trovati articoli di altri autori.")

                else:
                    # Test sull'entropia relativa
                    testo_concatenato = "".join([testo for testo in gruppo_selezionato if testo])
                    logging.info("Test Entropia Relativa:")
                    for articolo in gruppo_selezionato + altri_articoli:
                        if articolo:  # verifica che l'articolo non sia None
                            entropia = entropia_relativa(testo_concatenato, articolo)
                            logging.info(f"Entropia: {entropia}")

                    # Test con n-grammi
                    logging.info("\nTest con n-grammi:")
                    for testo_1 in gruppo_selezionato:
                        for testo_2 in altri_articoli:
                            if testo_1 and testo_2:
                                distanza = calcolo_distanza(testo_1, testo_2, 8)
                                logging.info(f"Distanza: {distanza}")

    except Exception as e:
        logging.error(f"Errore durante l'esecuzione: {e}")

# bisogna effettuare sia il test aperto che il test cieco
# 1. test aperto -> 50 articoli scientifici di uno stesso autore (gruppo dei testi da attribuire)
# e 50 di autori diversi (gruppo dei testi di controllo) che trattano lo STESSO tema
# ogni testo dei primi 50 (testi da attribuire) va confrontato con ognuno del secondo gruppo (testi di controllo)

"""
Obiettivo del codice:
Discriminare mediante l'implementazione di due algoritmi, rispettivamente dell'entropia relativa e  degli n-grammi (per 
comprenderne l'implementazione fare riferimento ai file entropia_relativa.py e n_grammi.py), gli autori di testi trattanti 
stesse tematiche. Nello specifico il codice dovrebbe attribuire testi al gruppo di autori fissato oppure no in base ai 
risultati ottenuti dagli algoritmi. Questo metodo fa riferimento a studi eseguiti su testi gramsciani da professori quali 
Maurizio Lana e Mirko Degli espositi; allego un documento pdf più esplicativo nel repository github "IU-03-10-Lana.pdf",
si consultino da pag 35 del documento (risulta la 4° pagina del pdf di riferimento) per il funzionamento del metodo degli 
n-grammi e da pag 37 (7° pagina del pdf) per il metodo sull'entropia relativa.

Commenti sul funzionamento del codice:
Temevo che il problema fosse nel selezionare gruppi di articoli che avessero in comune gli stessi autori, quindi ho 
aumentato max_count a 150 e diminuito la selezione del numero di articoli per gruppo_selezionato (contenente i testi dello 
stesso gruppo di autori) e altri_articoli (in cui non è necessario che gli autori siano gli stessi), ci ha impiegato 26 
minuti senza ottenere alcun risultato. Ho inoltre inserito un print dalla riga 93 alla 97 per verificare che il problema 
fosse nell'inizializzazione di gruppo_selezionato a None ma facendo girare il codice comunque l'ultimo messaggio che viene stampato è 
<ERROR - Errore durante l'esecuzione: '<' not supported between instances of 'NoneType' and 'str'> e poi il codice si blocca.
"""
