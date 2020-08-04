from spacy.matcher import Matcher           # Import the Matcher Class
from watermarkingMethod import WatermarkingMethod


class Contraction(WatermarkingMethod):
    matcherObjectContractionCandidate = None
    matcherObjectContracted = None

    def __init__(self):
        super().__init__("Kontraktion", 3)

    def initializeMethod(self, nlp):
        # Initialisierung der neuen Objekte der Matchter-Klasse
        matcherContractionCandidate = Matcher(nlp.vocab)
        matcherContracted = Matcher(nlp.vocab)

        # Definierung des Musters von Kontraktionen
        # Mögliche Präpositionen, welche mit dem nachvollgendem Artikel verschmelzen können
        patternContractionCandidate = [
            {'TAG': 'APPR'},
            {'TAG': 'ART'}
        ]

        # Kontraktion, welche wieder gelöst werden könnte
        patternContracted = [
            {'TAG': 'APPRART'}
        ]

        # Hinzufügen der Muster zu den Matcher-Objekten
        matcherContractionCandidate.add("CONTRACTIONCANDIDATE", None, patternContractionCandidate)
        matcherContracted.add("CONTRACTION", None, patternContracted)
        self.matcherObjectContractionCandidate = matcherContractionCandidate
        self.matcherObjectContracted = matcherContracted

    def changeSentence(self, docOfSentence, startIndex, endIndex, replacement):
        changedSentence = docOfSentence[0:startIndex].text
        if startIndex == 0:
            changedSentence += replacement.capitalize() + " "
        else:
            changedSentence += " " + replacement + " "
        changedSentence += docOfSentence[endIndex:len(docOfSentence)].text
        return changedSentence

    def process(self, docOfSentence, nlp, optionalObject=None):
        # Dictionary mit den möglichen Verschmelzungen
        possibleContractions = dict({
            "an dem": "am",
            "an das": "ans",
            "bei dem": "beim",
            "in dem": "im",
            "in das": "ins",
            "von dem": "vom",
            "zu dem": "zum",
            "zu der": "zur"
        })

        changedSentences = list()                   # Liste der veränderten Sätze

        # Prüfung, ob eine Kontraktion durchgeführt werden kann
        contractionCandidateMatches = self.matcherObjectContractionCandidate(docOfSentence)

        contractedMatches = self.matcherObjectContracted(docOfSentence)

        # Iteration über alle Übereinstimmungen
        for match_id, start, end in contractionCandidateMatches:
            # Überprüfung, ob eine gültige Kontraktion vorliegt
            if docOfSentence[start:end].text.lower() in possibleContractions.keys():
                changedSentences.append(self.changeSentence(docOfSentence, start, end, possibleContractions[docOfSentence[start:end].text.lower()]))

        for match_id, start, end in contractedMatches:
            # Überprüfung, ob eine gültige Kontraktion vorliegt
            if docOfSentence[start:end].text.lower() in possibleContractions.values():
                changedSentences.append(self.changeSentence(docOfSentence, start, end, list(possibleContractions.keys())[list(possibleContractions.values()).index(docOfSentence[start:end].text.lower())]))

        if changedSentences:
            return changedSentences
        else:
            # Keine Übereinstimmung gefunden
            return None
