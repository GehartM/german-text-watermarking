from spacy.matcher import Matcher           # Import the Matcher Class
from watermarkingMethod import WatermarkingMethod


class PrefixExpansion(WatermarkingMethod):
    matcherObject = None

    def __init__(self):
        super().__init__("Prefix Expansion", 1)

    def initializeMethod(self, nlp):
        # Initialisierung eines neuen Objektes der Matchter-Klasse
        matcher = Matcher(nlp.vocab)
        # Definierung des Musters für die Prefix-Expansion Methode
        pattern = [
            {"TEXT": {"REGEX": "^Un*|^un*"}, 'POS': 'ADJ'}
        ]
        # Hinzufügen des Musters zu dem Matcher-Objekt
        matcher.add("PREFIXEXPANSION", None, pattern)
        self.matcherObject = matcher

    def process(self, docOfSentence, nlp, optionalObject=None):
        allMatches = self.matcherObject(docOfSentence)

        # Iteration über alle Übereinstimmungen
        for match_id, start, end in allMatches:
            # Überprüfung, ob es sich bei dem aktuellen Satz, um eine Frage handelt oder eine Negation beinhaltet
            # Bei diesen darf die Prefix-Expansion-Methode nicht angewendet werden
            invalidSentence = False
            for token in docOfSentence:
                # print("Current Token: ", token.text)
                if token.pos_ == "PUNCT" and token.text == "?":
                    invalidSentence = True
                    break
                elif token.dep_ == "ng":
                    # Negierung mit "Nicht"
                    invalidSentence = True
                    break
                elif token.lemma_.lower() == "kein":
                    invalidSentence = True
                    break
                elif token.lemma_.lower() == "weder":
                    invalidSentence = True
                    break
                elif token.lemma_.lower() == "niemand":
                    invalidSentence = True
                    break
                elif token.lemma_.lower() == "nichts":
                    invalidSentence = True
                    break
                elif token.lemma_.lower() == "nie":
                    invalidSentence = True
                    break
                elif token.lemma_.lower() == "niemals":
                    invalidSentence = True
                    break
                elif token.lemma_.lower() == "nirgendwo":
                    invalidSentence = True
                    break
                elif token.lemma_.lower() == "nirgends":
                    invalidSentence = True
                    break
                elif token.lemma_.lower() == "nirgendwohin":
                    invalidSentence = True
                    break

            if invalidSentence:
                continue

            # Speicherung des ursprünglichen Satzes
            originalSentence = docOfSentence.text

            try:
                # Speicherung des Wortes, welches den Kriterien ensprochen hat
                matchedWord = originalSentence[docOfSentence[start].idx:docOfSentence[end].idx]

                # Entfernung des Prefix "un" aus dem Wort
                matchedWord = matchedWord[2:]

                # Entfernung jenes Wortes aus dem Satz, welches den Kriterien entsprochen hat
                originalSentence = originalSentence[0:docOfSentence[start].idx:] + originalSentence[
                                                                                   docOfSentence[end].idx::]

                # Einfügen der Abänderung in den Satz
                originalSentence = originalSentence[:docOfSentence[start].idx] + "nicht " + matchedWord + originalSentence[
                                                                                                          docOfSentence[
                                                                                                              start].idx:]
            except:
                return None

            # Rückgabe des geänderten Satzes
            changedSentence = list()
            changedSentence.append(originalSentence)
            return changedSentence

        # Keine Übereinstimmung gefunden
        return None
