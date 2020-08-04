from itertools import permutations
from spacy.tokens import Token, Span
from watermarkingMethod import WatermarkingMethod


class Conjunction(WatermarkingMethod):

    def __init__(self):
        super().__init__("Konjunktion", 3)

    def initializeMethod(self, nlp):
        pass

    def process(self, docOfSentence, nlp, optionalObject=None):
        docOfSentence, sentenceEnding = self.removeAllSpacesAndPunctiationMarksAtEndOfSentence(docOfSentence)

        # Teilung des Satzes in Haupt- und Nebensatz, sofern dies möglich ist, um eine präziseres Ergebnis zu erzielen
        splittedDocOfSentence = list()
        beginOfNextSentence = 0
        for word in docOfSentence:
            # Bei Auftreten eines Beistriches im Satz, wird der Satz geteilt.
            if word.tag_ == "$,":
                # Speicherung des Satzteiles ohne den trennenden Beistrich, sofern es sich um einen vollständigen Satz
                # handelt
                if self.checkIfProperSentence(docOfSentence[beginOfNextSentence:word.i]):
                    splittedDocOfSentence.append(docOfSentence[beginOfNextSentence:word.i])
                    beginOfNextSentence = word.i + 1

        # Abspeicherung des letzten Satzteiles bzw. des gesamten Satzes sofern, kein Beistrich enthalten war
        splittedDocOfSentence.append(docOfSentence[beginOfNextSentence:len(docOfSentence) + 1])

        possibleSplittedSentence = list()           # Hält alle Möglichkeiten für einen Satzteil

        for partOfSentence in splittedDocOfSentence:
            tempPossibleSplittedSentence = list()   # Hält alle Möglichkeiten für den aktuellen Satzteil
            endOfSentence = ""                      # Hält das aktuell definierte Satzende
            conjunctionFound = False
            currentWord = 0
            endOfLastConjunctionPartIndex = 0       # Hält die Position jenes Wortes, welches das Ende des zuletzt
                                                    # überprüften Satzes dargestellt hat
            while currentWord < len(partOfSentence):
                if partOfSentence[currentWord].tag_ == "KON" and partOfSentence[currentWord].text == "und":
                    conjunctionFound = True

                    # Ist es der erste Satzteil muss auf die Groß- und Kleinschreibung des ersten Wortes geachtet werden
                    if splittedDocOfSentence.index(partOfSentence) == 0:
                        possibleSentencesOfCurrentPart, endOfConjunctionPart = self.checkConjunction(
                            partOfSentence[currentWord].i, partOfSentence[endOfLastConjunctionPartIndex:len(
                                partOfSentence)], "und", True)
                        if possibleSentencesOfCurrentPart is not None:
                            tempPossibleSplittedSentence.append(possibleSentencesOfCurrentPart)
                    else:
                        possibleSentencesOfCurrentPart, endOfConjunctionPart = self.checkConjunction(
                            partOfSentence[currentWord].i, partOfSentence[endOfLastConjunctionPartIndex:len(
                                partOfSentence)], "und")
                        if possibleSentencesOfCurrentPart is not None:
                            tempPossibleSplittedSentence.append(possibleSentencesOfCurrentPart)

                    # Überprüfung, welche Position der letzte Teil der Konjunktion hatte, um bei dieser weiterzusuchen
                    while currentWord < len(partOfSentence):
                        if partOfSentence[currentWord].i == endOfConjunctionPart:
                            endOfLastConjunctionPartIndex = currentWord
                            endOfSentence = partOfSentence[currentWord:len(partOfSentence)].text
                            currentWord -= 1
                            break
                        currentWord += 1

                elif partOfSentence[currentWord].tag_ == "KON" and partOfSentence[currentWord].text == "oder":
                    conjunctionFound = True

                    # Ist es der erste Satzteil muss auf die Groß- und Kleinschreibung des ersten Wortes geachtet werden
                    if splittedDocOfSentence.index(partOfSentence) == 0:
                        possibleSentencesOfCurrentPart, endOfConjunctionPart = self.checkConjunction(
                            partOfSentence[currentWord].i, partOfSentence[endOfLastConjunctionPartIndex:len(
                                partOfSentence)], "oder", True)
                        if possibleSentencesOfCurrentPart is not None:
                            tempPossibleSplittedSentence.append(possibleSentencesOfCurrentPart)
                    else:
                        possibleSentencesOfCurrentPart, endOfConjunctionPart = self.checkConjunction(
                            partOfSentence[currentWord].i, partOfSentence[endOfLastConjunctionPartIndex:len(
                                partOfSentence)], "oder")
                        if possibleSentencesOfCurrentPart is not None:
                            tempPossibleSplittedSentence.append(possibleSentencesOfCurrentPart)

                    # Überprüfung, welche Position der letzte Teil der Konjunktion hatte, um bei dieser weiterzusuchen
                    while currentWord < len(partOfSentence):
                        if partOfSentence[currentWord].i == endOfConjunctionPart:
                            endOfLastConjunctionPartIndex = currentWord
                            endOfSentence = partOfSentence[currentWord:len(partOfSentence)].text
                            currentWord -= 1
                            break
                        currentWord += 1
                currentWord += 1

            if not conjunctionFound:
                # Der aktuelle Satzteil enthält keine der gewünschten Konjunktionen
                listWithOriginalSentence = list()
                listWithOriginalSentence.append(partOfSentence.text)
                possibleSplittedSentence.append(listWithOriginalSentence)
            else:
                # Endung des aktuellen Satzteiles anhängen
                possiblePartSentenceWithEnding = list()
                if tempPossibleSplittedSentence:
                    for possiblePartSentence in tempPossibleSplittedSentence[len(tempPossibleSplittedSentence) - 1]:
                        possiblePartSentenceWithEnding.append(possiblePartSentence + " " + endOfSentence)

                    for possiblePartSentenceIndex in range(0, len(tempPossibleSplittedSentence) - 1):
                        possibleSplittedSentence.append(tempPossibleSplittedSentence[possiblePartSentenceIndex])
                    possibleSplittedSentence.append(possiblePartSentenceWithEnding)

        # Verbindung aller Satzteilabwandlungen miteinander
        possibleSentences = list()
        if possibleSplittedSentence:
            for possibleFirstPart in possibleSplittedSentence[0]:
                currentSentence = possibleFirstPart
                for nextIndex in range(1, len(possibleSplittedSentence)):
                    for possibleNextPart in possibleSplittedSentence[nextIndex]:

                        # Überprüfung, ob bereits ein Satzzeichen am Ende des aktuellen Teiles ist
                        if possibleFirstPart[len(possibleFirstPart) - 1] == "," or possibleFirstPart[len(
                                possibleFirstPart) - 1] == ";" or possibleFirstPart[len(
                            possibleFirstPart) - 1] == "." or possibleFirstPart[len(
                            possibleFirstPart) - 1] == "?" or possibleFirstPart[len(possibleFirstPart) - 1] == "!":
                            possibleSentences.append(currentSentence + possibleNextPart + sentenceEnding)
                        else:
                            possibleSentences.append(currentSentence + ", " + possibleNextPart + sentenceEnding)

        # Überprüfung, ob die Liste von möglichen Sätzen leer ist
        # In diesem Fall gab es nur einen und nicht mehrere Satzteile
        if len(possibleSentences) == 0:
            if possibleSplittedSentence:
                for possiblePart in possibleSplittedSentence[0]:
                    possibleSentences.append(possiblePart + sentenceEnding)

        # Rückgabe der möglichen Sätze
        if len(possibleSentences) == 0:
            return None
        else:
            return possibleSentences


    def checkConjunction(self, positionOfConjunction, partOfSentence, conjunctionWord, firstSentencePart=False):
        # Registrierung eines Attributes zum Festlegen, dass ein am Beginn des Satzes stehendes Wort klein
        # geschrieben werden muss, sofern dieses verschoben wird
        Token.set_extension("shouldBeLowercase", default=False, force=True)
        Span.set_extension("shouldBeLowercase", default=False, force=True)

        # Zerteilen des Satzes in die Konjunktionsbestandteile
        connectedConjunctionParts = list()
        partBeforeConjunction = partOfSentence[0:positionOfConjunction - partOfSentence[0].i]

        # Überprüfung, ob weitere Aufzählungen, welche mit einem Beistrich voneinander getrennt enthalten sind
        lastPositionOfConjunctPart = 0
        currentPosition = 0
        while currentPosition < len(partOfSentence):
            if partBeforeConjunction[currentPosition].tag_ == "$,":
                connectedConjunctionParts.append(partBeforeConjunction[lastPositionOfConjunctPart:currentPosition])
                lastPositionOfConjunctPart = currentPosition + 1
            currentPosition += 1

        # Hinzufügen der letzten Aufzählung vor der Konjunktion zur Liste
        connectedConjunctionParts.append(partBeforeConjunction[lastPositionOfConjunctPart:len(partBeforeConjunction)])

        # Hinzufügen der Aufzählung nach der Konjunktion zur Liste
        connectedConjunctionParts.append(partOfSentence[(positionOfConjunction - partOfSentence[0].i) + 1:len(
            partOfSentence)])

        # Kategorisierung und Zerteilung der verbundenen Wörter
        beginOfSentence = ""
        endOfSentence = ""
        endOfSentencePosition = None
        conjunctWords = dict()
        currentPosition = 0

        while currentPosition < (len(connectedConjunctionParts) - 1):
            if connectedConjunctionParts[currentPosition][0].tag_ != "KON":
                if currentPosition == 0:
                    if connectedConjunctionParts[currentPosition][0].pos_ != "PUNCT":
                        extractedConjunctWord, typeOfExtratedConjunctWord, beginOfSentence = \
                            self.categorizeAndExtractConjuctWords(connectedConjunctionParts[currentPosition], False, True)
                        conjunctWords[extractedConjunctWord] = typeOfExtratedConjunctWord
                else:
                    if connectedConjunctionParts[currentPosition][0].pos_ != "PUNCT":
                        extractedConjunctWord, typeOfExtratedConjunctWord, nothing = \
                            self.categorizeAndExtractConjuctWords(connectedConjunctionParts[currentPosition])
                        conjunctWords[extractedConjunctWord] = typeOfExtratedConjunctWord
            currentPosition += 1

        try:
            if connectedConjunctionParts[currentPosition][0].pos_ != "PUNCT":
                extractedConjunctWord, typeOfExtratedConjunctWord, endOfSentence = \
                    self.categorizeAndExtractConjuctWords(connectedConjunctionParts[currentPosition], True)
                if extractedConjunctWord is not None and typeOfExtratedConjunctWord is not None:
                    conjunctWords[extractedConjunctWord] = typeOfExtratedConjunctWord
                else:
                    # Es wurde ein nicht unterstützter Typ gefunden, daher wird der Satz nicht verändert
                    listWithOriginalSentence = list()
                    listWithOriginalSentence.append(partOfSentence.text)
                    return listWithOriginalSentence, endOfSentencePosition
        except:
            return None, None

        if type(endOfSentence) == str:
            endOfSentencePosition = len(endOfSentence)
        else:
            try:
                endOfSentencePosition = endOfSentence[0].i
            except:
                return None, None

        # Überprüfung, ob alle verbundenen Wörter vom gleichen Typ sind, da nur gleiche Typen vertauscht werden können
        try:
            typeOfExtratedConjunctWords = str(list(conjunctWords.values())[0])
            for currentType in conjunctWords.values():
                if currentType != typeOfExtratedConjunctWords:
                    # Es wurde ein widersprüchlicher Typ gefunden, daher wird der Satz nicht verändert
                    listWithOriginalSentence = list()
                    listWithOriginalSentence.append(partOfSentence.text)
                    return listWithOriginalSentence, endOfSentencePosition
        except:
            return None, None

        # Generierung einer Liste mit allen möglichen Anordnungen der verbundenen Wörter
        permutationsOfConjunctWords = permutations(list(conjunctWords.keys()))

        # Überprüfung, ob die Anzahl der möglichen Permutationen nicht zu groß ist, um einen Speicherfehler zu vermeiden
        permutationsOfConjunctWordsList = list()
        for permutation in permutationsOfConjunctWords:
            permutationsOfConjunctWordsList.append(permutation)
            if len(permutationsOfConjunctWordsList) > 99:
                break

        # Seperierung der am Beginn befindlichen Satzzeichen am Beginn von endOfSentence
        # Diese müssen an jede Variation des Satzes angehängt werden
        punctuationCharactersAtBeginEndOfSentence = ""
        currentPosition = 0
        while currentPosition < len(endOfSentence):
            if endOfSentence[currentPosition].pos_ != "PUNCT":
                punctuationCharactersAtBeginEndOfSentence = endOfSentence[0:currentPosition]
                endOfSentence = endOfSentence[currentPosition:len(endOfSentence)]
                break
            currentPosition += 1

        # Einsetzen aller möglichen Anordnungen in den Satz
        allPossibleSentences = list()
        for permutation in permutationsOfConjunctWordsList:
            currentSentence = ""

            if not isinstance(beginOfSentence, str) and beginOfSentence.text != "" and beginOfSentence.text != " ":
                if not isinstance(permutation[0], str):
                    currentSentence += beginOfSentence.text + " " + permutation[0].text.capitalize()
                else:
                    currentSentence += beginOfSentence.text + " " + permutation[0].capitalize()
            else:
                if not isinstance(permutation[0], str):
                    currentSentence += permutation[0].text.capitalize()
                else:
                    currentSentence += permutation[0].capitalize()

            if len(permutation) > 2:
                positionOfCurrentWord = 1
                while positionOfCurrentWord < len(permutation) - 1:
                    # Überprüfung, ob das aktuelle Wort eigentlich klein geschrieben werden sollte
                    if not isinstance(permutation[positionOfCurrentWord], str):
                        currentSentence += ", " + permutation[positionOfCurrentWord].text
                    else:
                        currentSentence += ", " + permutation[positionOfCurrentWord]
                    positionOfCurrentWord += 1

            lastWord = None
            if not isinstance(permutation[len(permutation) - 1], str):
                lastWord = permutation[len(permutation) - 1].text
            else:
                lastWord = permutation[len(permutation) - 1]

            if not isinstance(punctuationCharactersAtBeginEndOfSentence, str) and \
                    punctuationCharactersAtBeginEndOfSentence.text != "" and \
                    punctuationCharactersAtBeginEndOfSentence.text != " ":
                if punctuationCharactersAtBeginEndOfSentence[0].pos_ != "PUNCT":
                    currentSentence += " " + conjunctionWord + " " + lastWord + " " + \
                                       punctuationCharactersAtBeginEndOfSentence.text
                else:
                    currentSentence += " " + conjunctionWord + " " + lastWord + \
                                       punctuationCharactersAtBeginEndOfSentence.text
            else:
                currentSentence += " " + conjunctionWord + " " + lastWord

            allPossibleSentences.append(currentSentence)
        return allPossibleSentences, endOfSentencePosition

    def categorizeAndExtractConjuctWords(self, conjunctionPartDoc, lastConjunctionPart=False, firstSentencePart=False):
        if not lastConjunctionPart:
            if len(conjunctionPartDoc) > 0 and (conjunctionPartDoc[len(conjunctionPartDoc) - 1].pos_ ==
                                                "NOUN" or conjunctionPartDoc[len(conjunctionPartDoc) - 1].pos_ ==
                                                "PROPN"):
                # Das letzte Wort ist ein Nomen
                if len(conjunctionPartDoc) > 1 and conjunctionPartDoc[len(conjunctionPartDoc) - 2].pos_ == "ADJ":
                    # Das vorletzte Wort ist ein Adjektiv
                    if len(conjunctionPartDoc) > 2 and conjunctionPartDoc[len(conjunctionPartDoc) - 3].tag_ == "ART":
                        # Das Wort davor ist ein Artikel
                        if len(conjunctionPartDoc) > 3 and (conjunctionPartDoc[len(conjunctionPartDoc) - 4].tag_ ==
                                                            "APPRART" or conjunctionPartDoc[len(
                                    conjunctionPartDoc) - 4].tag_ == "APPR"):
                            # Das Wort davor ist eine Präposition
                            # Rückgabe des letzten vier Wörter und deren Typ
                            # Ist es der Satzanfang, wird der erste Buchstabe des ersten Wortes auf
                            # Kleinschreibung konvertiert
                            conjunctionPart = conjunctionPartDoc[len(conjunctionPartDoc) - 4:len(conjunctionPartDoc)].text
                            if firstSentencePart:
                                if len(conjunctionPartDoc) == 4:
                                    # Es handelt sich um das erste Wort des Satzes
                                    conjunctionPart = conjunctionPart[0].lower() + conjunctionPart[1:]
                            return conjunctionPart, "NOUN", conjunctionPartDoc[0:len(conjunctionPartDoc) - 4]
                        else:
                            # Rückgabe des letzten drei Wörter und deren Typ
                            # Ist es der Satzanfang, wird der erste Buchstabe des ersten Wortes auf
                            # Kleinschreibung konvertiert
                            conjunctionPart = conjunctionPartDoc[len(conjunctionPartDoc) - 3:len(conjunctionPartDoc)].text
                            if firstSentencePart:
                                if len(conjunctionPartDoc) == 3:
                                    # Es handelt sich um das erste Wort des Satzes
                                    conjunctionPart = conjunctionPart[0].lower() + conjunctionPart[1:]
                            return conjunctionPart, "NOUN", conjunctionPartDoc[0:len(conjunctionPartDoc) - 3]
                    else:
                        # Rückgabe des letzten beiden Wörter und deren Typ
                        # Ist es der Satzanfang, wird der erste Buchstabe des ersten Wortes auf
                        # Kleinschreibung konvertiert
                        conjunctionPart = conjunctionPartDoc[len(conjunctionPartDoc) - 2:len(conjunctionPartDoc)].text
                        if firstSentencePart:
                            if len(conjunctionPartDoc) == 2:
                                # Es handelt sich um das erste Wort des Satzes
                                conjunctionPart = conjunctionPart[0].lower() + conjunctionPart[1:]
                        return conjunctionPart, "NOUN", conjunctionPartDoc[0:len(conjunctionPartDoc) - 2]
                elif len(conjunctionPartDoc) > 1 and conjunctionPartDoc[len(conjunctionPartDoc) - 2].tag_ == "ART":
                    # Das vorletzte Wort ist ein Artikel
                    if len(conjunctionPartDoc) > 2 and (conjunctionPartDoc[len(conjunctionPartDoc) - 3].tag_ ==
                                                        "APPRART" or conjunctionPartDoc[len(
                                conjunctionPartDoc) - 3].tag_ == "APPR"):
                        # Das Wort davor ist eine Präposition
                        # Rückgabe der letzten drei Wörter und deren Typ
                        # Ist es der Satzanfang, wird der erste Buchstabe des ersten Wortes auf
                        # Kleinschreibung konvertiert
                        conjunctionPart = conjunctionPartDoc[len(conjunctionPartDoc) - 3:len(conjunctionPartDoc)].text
                        if firstSentencePart:
                            if len(conjunctionPartDoc) == 3:
                                # Es handelt sich um das erste Wort des Satzes
                                conjunctionPart = conjunctionPart[0].lower() + conjunctionPart[1:]
                        return conjunctionPart, "NOUN", conjunctionPartDoc[0:len(conjunctionPartDoc) - 3]
                    else:
                        # Rückgabe der letzten beiden Wörter und deren Typ
                        # Ist es der Satzanfang, wird der erste Buchstabe des ersten Wortes auf
                        # Kleinschreibung konvertiert
                        conjunctionPart = conjunctionPartDoc[len(conjunctionPartDoc) - 2:len(conjunctionPartDoc)].text
                        if firstSentencePart:
                            if len(conjunctionPartDoc) == 2:
                                # Es handelt sich um das erste Wort des Satzes
                                conjunctionPart = conjunctionPart[0].lower() + conjunctionPart[1:]
                        return conjunctionPart, "NOUN", conjunctionPartDoc[0:len(conjunctionPartDoc) - 2]
                elif len(conjunctionPartDoc) > 1 and (conjunctionPartDoc[len(conjunctionPartDoc) - 2].tag_ == "APPRART"
                                                      or conjunctionPartDoc[len(conjunctionPartDoc) - 2].tag_ == "APPR"):
                    # Das vorletzte Wort ist eine Präposition
                    # Ist es der Satzanfang, wird der erste Buchstabe des ersten Wortes auf Kleinschreibung konvertiert
                    conjunctionPart = conjunctionPartDoc[len(conjunctionPartDoc) - 2:len(conjunctionPartDoc)].text
                    if firstSentencePart:
                        if len(conjunctionPartDoc) == 2:
                            # Es handelt sich um das erste Wort des Satzes
                            conjunctionPart = conjunctionPart[0].lower() + conjunctionPart[1:]
                    # Rückgabe des letzten beiden Worte und deren Typ
                    return conjunctionPart, "NOUN", conjunctionPartDoc[0:len(conjunctionPartDoc) - 2]
                else:
                    # Rückgabe des letzten Wortes und dessen Typs
                    return conjunctionPartDoc[len(conjunctionPartDoc) - 1], "NOUN", conjunctionPartDoc[0:len(
                        conjunctionPartDoc) - 1]
            else:
                # Das letzte Wort ist kein Nomen
                # Rückgabe des letzten Wortes und dessen Typs
                # Ist es der Satzanfang, wird der erste Buchstabe des ersten Wortes auf Kleinschreibung konvertiert
                conjunctionPart = conjunctionPartDoc[len(conjunctionPartDoc) - 1].text
                if firstSentencePart:
                    if len(conjunctionPartDoc) == 1:
                        # Es handelt sich um das erste Wort des Satzes
                        conjunctionPart = conjunctionPart[0].lower() + conjunctionPart[1:]
                return conjunctionPart, conjunctionPartDoc[len(conjunctionPartDoc) - 1].pos_, conjunctionPartDoc[0:len(
                    conjunctionPartDoc) - 1]
        else:
            # Der letzte Teil der Aufzählung soll geprüft werden
            if len(conjunctionPartDoc) > 0 and conjunctionPartDoc[0].tag_ == "ART":
                # Das erste Wort ist ein Artikel
                if len(conjunctionPartDoc) > 1 and (conjunctionPartDoc[1].pos_ == "NOUN" or conjunctionPartDoc[1].pos_
                                                    == "PROPN"):
                    # Das zweite Wort ist ein Nomen
                    # Rückgabe der beiden Wörter und deren Typ
                    return conjunctionPartDoc[0:2], "NOUN", conjunctionPartDoc[2:len(conjunctionPartDoc)]
                elif len(conjunctionPartDoc) > 1 and conjunctionPartDoc[1].pos_ == "ADJ":
                    # Das zweite Wort ist ein Adjektiv
                    if len(conjunctionPartDoc) > 2 and (conjunctionPartDoc[2].pos_ == "NOUN"
                                                        or conjunctionPartDoc[2].pos_ == "PROPN"):
                        # Das dritte Wort ist ein Nomen
                        # Rückgabe der drei Wörter und deren Typ
                        return conjunctionPartDoc[0:3], "NOUN", conjunctionPartDoc[3:len(conjunctionPartDoc)]
                    else:
                        # Nicht unterstützter Typ entdeckt
                        return None, None, conjunctionPartDoc
                else:
                    # Rückgabe des ersten Wortes
                    return conjunctionPartDoc[0], conjunctionPartDoc[0].pos_, conjunctionPartDoc[1:len(conjunctionPartDoc)]
            elif len(conjunctionPartDoc) > 0 and (conjunctionPartDoc[0].tag_ == "APPRART" or
                                                  conjunctionPartDoc[0].tag_ == "APPR"):
                # Das erste Wort ist eine Präposition
                if len(conjunctionPartDoc) > 1 and conjunctionPartDoc[1].tag_ == "ART":
                    # Das zweite Wort ist ein Artikel
                    if len(conjunctionPartDoc) > 2 and conjunctionPartDoc[2].pos_ == "ADJ":
                        # Das dritte Wort ist ein Adjektiv
                        if len(conjunctionPartDoc) > 3 and (conjunctionPartDoc[3].pos_ == "NOUN" or
                                                            conjunctionPartDoc[3].pos_ == "PROPN"):
                            # Das vierte Wort ist ein Nomen
                            # Rückgabe der vier Wörter und deren Typ
                            return conjunctionPartDoc[0:5], "NOUN", conjunctionPartDoc[5:len(conjunctionPartDoc)]
                        else:
                            # Nicht unterstützter Typ entdeckt
                            return None, None, conjunctionPartDoc
                    elif len(conjunctionPartDoc) > 2 and (conjunctionPartDoc[2].pos_ == "NOUN" or
                                                          conjunctionPartDoc[2].pos_ == "PROPN"):
                        # Das dritte Wort ist ein Nomen
                        # Rückgabe der drei Wörter und deren Typ
                        return conjunctionPartDoc[0:4], "NOUN", conjunctionPartDoc[4:len(conjunctionPartDoc)]
                    else:
                        # Nicht unterstützter Typ entdeckt
                        return None, None, conjunctionPartDoc
                elif len(conjunctionPartDoc) > 1 and (conjunctionPartDoc[1].pos_ == "NOUN" or
                                                      conjunctionPartDoc[1].pos_ == "PROPN"):
                    # Das zweite Wort ist ein Nomen
                    # Rückgabe der beiden Wörter und deren Typ
                    return conjunctionPartDoc[0:3], "NOUN", conjunctionPartDoc[3:len(conjunctionPartDoc)]
                else:
                    # Rückgabe des ersten Wortes
                    return conjunctionPartDoc[0], conjunctionPartDoc[0].pos_, conjunctionPartDoc[1:len(conjunctionPartDoc)]
            elif len(conjunctionPartDoc) > 0 and conjunctionPartDoc[0].pos_ == "ADJ":
                # Das erste Wort ist ein Adjektiv
                if len(conjunctionPartDoc) > 1 and (conjunctionPartDoc[1].pos_ == "NOUN" or
                                                    conjunctionPartDoc[1].pos_ == "PROPN"):
                    # Das zweite Wort ist ein Nomen
                    # Rückgabe der beiden Wörter und deren Typ
                    return conjunctionPartDoc[0:3], "NOUN", conjunctionPartDoc[3:len(conjunctionPartDoc)]
                else:
                    # Rückgabe des ersten Wortes
                    return conjunctionPartDoc[0], conjunctionPartDoc[0].pos_, conjunctionPartDoc[1:len(conjunctionPartDoc)]
            elif len(conjunctionPartDoc) > 0 and (conjunctionPartDoc[0].pos_ == "NOUN" or
                                                  conjunctionPartDoc[0].pos_ == "PROPN"):
                # Das erste Wort ist ein Nomen
                # Rückgabe des ersten Wortes und dessen Typs
                return conjunctionPartDoc[0], "NOUN", conjunctionPartDoc[1:len(conjunctionPartDoc)]
            else:
                # Das erste Wort ist weder Artikel, noch Präposition
                # Rückgabe des ersten Wortes und dessen Typs
                return conjunctionPartDoc[0], conjunctionPartDoc[0].pos_, conjunctionPartDoc[1:len(conjunctionPartDoc)]


    def checkIfProperSentence(self, partOfSentence):
        # Ein vollständiger Satz muss mindestens ein Subjekt und ein Prädikat aufweisen
        sentenceContainsSubject = False
        sentenceContainsPredicate = False
        for word in partOfSentence:
            if word.pos_ == "NOUN" or word.pos_ == "PROPN":
                sentenceContainsSubject = True
            elif word.pos_ == "AUX" or word.pos_ == "VERB":
                sentenceContainsPredicate = True

        if sentenceContainsSubject and sentenceContainsPredicate:
            return True
        else:
            return False


    def removeAllSpacesAndPunctiationMarksAtEndOfSentence(self, docOfSentence):
        sentenceEnding = ""
        lastCharacterPosition = len(docOfSentence) - 1
        while lastCharacterPosition != 0:
            if docOfSentence[lastCharacterPosition].tag_ == "_SP" or docOfSentence[lastCharacterPosition].pos_ == "PUNCT":
                docOfSentence = docOfSentence[0:lastCharacterPosition]
                sentenceEnding = docOfSentence[lastCharacterPosition].text + sentenceEnding
                lastCharacterPosition -= 1
            else:
                return docOfSentence, sentenceEnding
        return docOfSentence, sentenceEnding