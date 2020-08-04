from spacy.matcher import PhraseMatcher             # Import the PhraseMatcher Class
from watermarkingMethod import WatermarkingMethod


class SynonymSubstitution(WatermarkingMethod):
    undSynonymObject = None
    oderSynonymObject = None

    # Listen mit den unterstützten Synonymen
    undSynonym = list({
        "und",
        "sowie",
        "wie auch",
        "außerdem",
        "daneben",
        "darüber hinaus",
        "dazu",
        "des Weiteren",
        "ferner",
        "gleichzeitig",
        "obendrein",
        "überdies",
        "zugleich",
        "zusätzlich",
        "zudem"
    })

    oderSynonym = list({
        "oder",
        "beziehungsweise",
        "respektive"
    })

    def __init__(self):
        super().__init__("Synonymaustauschung", 5)

    def initializeMethod(self, nlp):
        # Initialisierung eines neuen Objektes der Matchter-Klasse
        undMatcher = PhraseMatcher(nlp.vocab, attr='LOWER')
        oderMatcher = PhraseMatcher(nlp.vocab, attr='LOWER')

        # Definierung der Synonyme
        undPattern = [
            nlp(text) for text in self.undSynonym
        ]
        oderPattern = [
            nlp(text) for text in self.oderSynonym
        ]

        # Hinzufügen der Muster zu dem Matcher-Objekt
        undMatcher.add("UND", None, *undPattern)
        oderMatcher.add("ODER", None, *oderPattern)
        self.undSynonymObject = undMatcher
        self.oderSynonymObject = oderMatcher


    def process(self, docOfSentence, nlp, optionalObject=None):
        allUndMatches = self.undSynonymObject(docOfSentence)
        allOderMatches = self.oderSynonymObject(docOfSentence)
        possibleSentences = list()

        # Iteration über alle Übereinstimmungen
        for match_id, start, end in allUndMatches:
            # Überprüfung, ob sich vor und nach dem Match ein Leerzeichen befindet, um ausschließen zu können, dass
            # es ein Match innerhalb eines Wortes ist
            if not self.checkIfMatchIsIndependent(docOfSentence, start, end):
                continue

            changedSentences = self.changeSentence(docOfSentence, start, end)
            if changedSentences:
                for changedSentence in changedSentences:
                    possibleSentences.append(changedSentence)

        # Iteration über alle Übereinstimmungen
        for match_id, start, end in allOderMatches:
            # Überprüfung, ob sich vor und nach dem Match ein Leerzeichen befindet, um ausschließen zu können, dass
            # es ein Match innerhalb eines Wortes ist
            if not self.checkIfMatchIsIndependent(docOfSentence, start, end):
                continue

            changedSentences = self.changeSentence(docOfSentence, start, end)
            if changedSentences:
                for changedSentence in changedSentences:
                    possibleSentences.append(changedSentence)

        # Rückgabe aller Änderungen
        if not possibleSentences:
            return None
        else:
            return possibleSentences


    def checkIfMatchIsIndependent(self, docOfSentence, start, end):
        # Überprüfung, ob sich vor und nach dem Match ein Leerzeichen befindet, um ausschließen zu können, dass es
        # ein Match innerhalb eines Wortes ist
        startOfSentence = 0
        endOfSentence = len(docOfSentence) - 1

        # Überprüfung, ob die Übereinstimmung am Anfang des Satzes steht
        if startOfSentence == docOfSentence[start].idx:
            # Überprüfung, ob die Übereinstimmung nicht am Satzende steht
            try:
                if endOfSentence != docOfSentence[end].idx:
                    # Überprüfung, ob das Zeichen nach der Übereinstimmung kein Leerzeichen ist
                    if docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != " " \
                            and docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != "\n" \
                            and docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != "." \
                            and docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != "," \
                            and docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != ";" \
                            and docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != "?" \
                            and docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != "!":
                        # Match war innerhalb eines Wortes
                        return False
            except:
                return False
        else:
            # Die Übereinstimmung steht nicht am Anfang des Satzes
            # Überprüfung, ob vor der Übereinstimmung kein Leerzeichen ist
            if docOfSentence.text[docOfSentence[start].idx - 1] != " ":
                # Match war innerhalb eines Wortes
                return False

            # Überprüfung, ob die Übereinstimmung nicht am Satzende steht
            try:
                if endOfSentence != docOfSentence[end].idx:
                    # Überprüfung, ob das Zeichen nach der Übereinstimmung kein Leerzeichen ist
                    if docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != " " \
                            and docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != "\n" \
                            and docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != "." \
                            and docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != "," \
                            and docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != ";" \
                            and docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != "?" \
                            and docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != "!":
                        # Match war innerhalb eines Wortes
                        return False
            except:
                return False
        return True

    def changeSentence(self, docOfSentence, start, end):
        # Speicherung des ursprünglichen Satzes
        changedSentence = docOfSentence.text

        # Speicherung der Übereinstimmung
        matchedWord = changedSentence[docOfSentence[start].idx:docOfSentence[end].idx]

        # Entfernen von eventuellen Leerzeichen am Ende der Übereinstimmung
        currentIndex = len(matchedWord) - 1
        while currentIndex > -1:
            if matchedWord[currentIndex] != " ":
                matchedWord = matchedWord[0:currentIndex + 1]
                break
            currentIndex -= 1

        # Speicherung des Wortes bzw. der Wörter, welche mit der Übereinstimmung vertauscht werden
        possibleSentences = list()
        changeMatchWith = ""
        # Überprüfung, in welcher Liste sich die Übereinstimmung befindet
        if matchedWord.lower() in self.undSynonym:
            # Die "Und"-Synonymliste kann verwendet werden
            for synonym in self.undSynonym:
                if synonym.lower() != matchedWord.lower():
                    # Überprüfung, ob vor dem Synonym ein Beistrich eingefügt werden muss oder nicht
                    if synonym == "und":
                        possibleSentences.append(self.insertSynonymIntoSentence(docOfSentence, start, end, synonym,
                                                                                changedSentence, False))
                    else:
                        possibleSentences.append(self.insertSynonymIntoSentence(docOfSentence, start, end, synonym,
                                                                                changedSentence, True))
        elif matchedWord.lower() in self.oderSynonym:
            # Die "Oder"-Synonymliste kann verwendet werden
            for synonym in self.oderSynonym:
                if synonym.lower() != matchedWord.lower():
                    # Überprüfung, ob vor dem Synonym ein Beistrich eingefügt werden muss oder nicht
                    if synonym == "oder":
                        possibleSentences.append(self.insertSynonymIntoSentence(docOfSentence, start, end, synonym,
                                                                                changedSentence, False))
                    else:
                        possibleSentences.append(self.insertSynonymIntoSentence(docOfSentence, start, end, synonym,
                                                                                changedSentence, True))
        else:
            # Es konnte keine Übereinstimmung in keiner der Listen gefunden werden
            return None
        return possibleSentences


    def insertSynonymIntoSentence(self, docOfSentence, start, end, changeMatchWith, changedSentence,
                                  insertKommaBeforeMatchedWord):
        startOfSentence = changedSentence[:docOfSentence[start].idx]
        endOfSentence = changedSentence[docOfSentence[end].idx:]

        # Überprüfung, ob nach der Übereinstimmung ein Satzzeichen steht
        # In diesem Fall darf kein zusätzlicher Abstand nach der Übereinstimmung eingefügt werden
        if docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != "." and \
                docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != "," and \
                docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != ";" and \
                docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != "?" and \
                docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != "!":
            changeMatchWith += " "

        # Überprüfung, ob die Übereinstimmung am Anfang des Satzes steht
        if docOfSentence[start].idx == 0:
            # Der erste Buchstabe muss groß geschrieben werden
            changeMatchWith = changeMatchWith[0].capitalize() + changeMatchWith[1:len(changeMatchWith)]
        else:
            # Die Übereinstimmung steht nicht am Satzbeginn
            # Überprüfung, ob ein Beistrich vor dem Synonym eingefügt werden soll
            if insertKommaBeforeMatchedWord:
                startOfSentence = startOfSentence[:len(startOfSentence) - 1]
                changeMatchWith = ", " + changeMatchWith

        # Einfügen der Abänderung in den Satz
        changedSentence = startOfSentence + changeMatchWith + endOfSentence
        return changedSentence
