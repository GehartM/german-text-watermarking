from spacy.tokens import Token, Span
from watermarkingMethod import WatermarkingMethod


class MainAndDependentClausePermutation(WatermarkingMethod):
    def __init__(self):
        super().__init__("Haupt- und Nebensatzvertauschung", 2)

    def initializeMethod(self, nlp):
        pass

    def process(self, docOfSentence, nlp, optionalObject=None):
        docOfSentence, sentenceEnding = self.removeAllSpacesAndPunctiationMarksAtEndOfSentence(docOfSentence)

        Token.set_extension("isMainClause", default=False, force=True)
        Token.set_extension("predicateIsAtBegin", default=True, force=True)
        Token.set_extension("shouldBeLowercase", default=False, force=True)
        Token.set_extension("belongsToPreviousPart", default=False, force=True)
        Span.set_extension("isMainClause", default=False, force=True)
        Span.set_extension("predicateIsAtBegin", default=True, force=True)
        Span.set_extension("shouldBeLowercase", default=False, force=True)
        Span.set_extension("belongsToPreviousPart", default=False, force=True)

        # Zerlegung des Satzes in seine Haupt- und Nebensätze
        allSentenceParts = self.splitAndCategorizeSentenceParts(docOfSentence)
        if allSentenceParts == None:
            return None

        # Verbindung von Nebensätzen zu deren Hauptsätzen
        relatedMainAndDependentClauses = self.relateSentenceToEachOther(allSentenceParts)
        if relatedMainAndDependentClauses == None:
            return None

        # Vertauschung der Haupt- und Nebensätze durchführen
        possibleVariations = self.changeMainAndDependentClauses(relatedMainAndDependentClauses, sentenceEnding)

        # Rückgabe der Variationen
        return possibleVariations

    def splitAndCategorizeSentenceParts(self, docOfSentence):
        # Teilung des Satzes in seine Bestandteile
        allSentenceParts = list()

        beginOfCurrentSentencePart = 0
        currentWordPosition = 0
        while currentWordPosition < len(docOfSentence) and beginOfCurrentSentencePart < len(docOfSentence):
            # Bei Auftreten eines Beistriches im Satz, wird der Satz geteilt.
            if docOfSentence[currentWordPosition].tag_ == "$," or currentWordPosition == len(docOfSentence) - 1:
                # Überprüfung, ob es sich um einen vollständigen Satz handelt
                properSentence = False
                if currentWordPosition == len(docOfSentence) - 1:
                    properSentence = self.checkIfProperSentence(docOfSentence[
                                                                beginOfCurrentSentencePart:docOfSentence[
                                                                                               currentWordPosition].i + 1])
                else:
                    properSentence = self.checkIfProperSentence(docOfSentence[
                                                                beginOfCurrentSentencePart:docOfSentence[
                                                                    currentWordPosition].i])

                if properSentence:
                    # Wenn das aktuelle Satzteil nicht am Anfang steht wird der Anfang und das Ende der
                    # Konjunktion ermittelt
                    startOfConjunction = 0
                    endOfConjunction = 0
                    if beginOfCurrentSentencePart != 0:
                        # Speicherung der Konjunktion
                        startOfConjunction = beginOfCurrentSentencePart
                        endOfConjunction = startOfConjunction
                        tempCurrentWordPosition = startOfConjunction
                        while tempCurrentWordPosition < len(docOfSentence):
                            tempCurrentWordPosition += 1
                            if docOfSentence[tempCurrentWordPosition].pos_ != "CCONJ" and docOfSentence[
                                tempCurrentWordPosition].pos_ != "SCONJ":
                                endOfConjunction = tempCurrentWordPosition
                                break

                    # Hinzufügen des Satzteiles zur Liste aller Satzteile
                    # Ist es der erste Satzteil, muss Groß- und Kleinschreibung des ersten Wortes beachtet werden
                    if beginOfCurrentSentencePart == 0:
                        # Sollte das erste Wort kein Nomen sein, so wird dieses Wort klein geschrieben
                        if docOfSentence[beginOfCurrentSentencePart:docOfSentence[currentWordPosition].i][
                            0].pos_ != "NOUN" and \
                                docOfSentence[beginOfCurrentSentencePart:docOfSentence[currentWordPosition].i][
                                    0].pos_ != "PROPN":
                            docOfSentence[
                            beginOfCurrentSentencePart:docOfSentence[currentWordPosition].i]._.shouldBeLowercase = True

                    if currentWordPosition == len(docOfSentence) - 1:
                        allSentenceParts.append(docOfSentence[beginOfCurrentSentencePart:docOfSentence[
                                                                                             currentWordPosition].i + 1])
                        currentWordPosition += 1
                    else:
                        allSentenceParts.append(docOfSentence[beginOfCurrentSentencePart:docOfSentence[
                            currentWordPosition].i])

                    # Überprüfung, ob es sich um einen Haupt- oder Nebensatz handelt
                    try:
                        isMainClause, predicateIsAtBegin = self.checkForMainClause(
                            docOfSentence[endOfConjunction:docOfSentence[currentWordPosition].i])
                    except:
                        return None
                    allSentenceParts[len(allSentenceParts) - 1]._.isMainClause = isMainClause
                    allSentenceParts[len(allSentenceParts) - 1]._.predicateIsAtBegin = predicateIsAtBegin

                    # Beginn des nächsten Satzes aktualisieren
                    currentWordPosition -= 1
                    beginOfCurrentSentencePart = currentWordPosition + 1

                elif currentWordPosition == len(docOfSentence) - 1:
                    # Wenn es aktuell um den letzten Teil des Satzes handelt und dieser kein vollständiger Satz ist,
                    # wird dieser Teil an den vorletzten Satzteil angehängt und übernimmt dessen Eigenschaften
                    if allSentenceParts:
                        allSentenceParts.append(docOfSentence[beginOfCurrentSentencePart:len(docOfSentence) + 1])
                        allSentenceParts[len(allSentenceParts) - 1]._.belongsToPreviousPart = True
                    else:
                        # Es gibt kein Satzteil davor und der aktuelle Teil ist kein vollständiger Satz, darum wird
                        # None zurückgegeben
                        return None

            currentWordPosition += 1

        if len(allSentenceParts) < 2:
            return None

        return allSentenceParts

    def relateSentenceToEachOther(self, splittedSentence):
        relatedMainAndDependentClauses = list()
        relatedMainAndDependentClauses.append([])
        currentListContainsMainClause = False

        for currentClause in splittedSentence:
            # Sollte das letzte Satzteil kein vollständiger Satz sein, so wird dieses dem vorletzten Satz zugeordnet
            if currentClause._.belongsToPreviousPart == False:
                if currentClause._.isMainClause == True:
                    # Es handelt sich um einen Hauptsatz
                    # Überprüfe, ob in der aktuellen Liste bereits ein Hauptsatz enthalten ist. In diesem Fall muss
                    # eine neue Liste angehängt werden
                    if currentListContainsMainClause:
                        relatedMainAndDependentClauses.append([])
                        currentListContainsMainClause = False
                    currentListContainsMainClause = True
                elif currentClause._.isMainClause == False:
                    # Es handelt sich um einen Nebensatz
                    if currentClause._.predicateIsAtBegin == True:
                        # Das Prädikat befindet sich am Beginn des Satzteiles, daher gehört der Nebensatz zum
                        # nachfolgenden Hauptsatz
                        relatedMainAndDependentClauses.append([])
                        currentListContainsMainClause = False
                else:
                    # Der aktuelle Satzteil konnte nicht zugeordnet werden
                    # Ist es der letzte Satzteil wird er mit dem vorletzten Satz in Verbindung gebracht
                    # Andernfalls kann die Methode nicht erfolgreich durchgeführt werden
                    if splittedSentence.index(currentClause) != len(splittedSentence) - 1:
                        return None
                    else:
                        currentClause._.belongsToPreviousPart = True

                # Hinzufügen des aktuellen Satzteiles zur aktuellen Liste
                relatedMainAndDependentClauses[len(relatedMainAndDependentClauses) - 1].append(currentClause)
            else:
                # Hinzufügen des letzten Satzteiles zur aktuellen Liste
                relatedMainAndDependentClauses[len(relatedMainAndDependentClauses) - 1].append(currentClause)

        return relatedMainAndDependentClauses


    def changeMainAndDependentClauses(self, relatedMainAndDependentClauses, sentenceEnding):
        changedVariations = list()
        beginOfSentence = ""
        for relatedClauses in relatedMainAndDependentClauses:
            # Befinden sich ein oder mehrere Nebensätze vor dem Hauptsatz, so kann die Methode nicht angewendet werden
            if relatedClauses[0]._.isMainClause:
                # Der erste Satzteil ist ein Hauptsatz
                currentClauseIndex = 0
                while currentClauseIndex < len(relatedClauses):
                    if relatedClauses[currentClauseIndex]._.isMainClause == False and relatedClauses[\
                            currentClauseIndex]._.belongsToPreviousPart == False:
                        # Es handelt sich um einen Nebensatz, welcher auf den Hauptsatz folgt
                        # Entfernung des Kommas am Beginn und des Abstandes danach beim Haupt- und Nebensatz
                        mainClauseDoc = self.removeKommaAndSpacesAtBeginningOfSentence(relatedClauses[0])
                        dependentClauseDoc = self.removeKommaAndSpacesAtBeginningOfSentence(relatedClauses[
                                                                                                currentClauseIndex])

                        # Ermittlung der Position des Prädikats im Hauptsatz
                        predicateStartPosition, predicateEndPosition = self.getPositionIndexOfPredicate(mainClauseDoc)

                        # Umwandlung der Doc-Objekte in Textobjekte
                        mainClauseText = mainClauseDoc.text
                        dependentClauseText = dependentClauseDoc.text

                        # Prüfung, ob es einen nachfolgenden Nebensatz gibt und dieser zum aktuellen Satzteil gehört
                        if len(relatedClauses) > currentClauseIndex + 1:
                            if relatedClauses[currentClauseIndex + 1]._.belongsToPreviousPart == True:
                                dependentClauseText = dependentClauseText + relatedClauses[currentClauseIndex + 1].text

                        # Ist am Beginn des Hauptsatzes kein Nomen, wird der erste Buchstabe klein geschrieben
                        if relatedClauses[0]._.shouldBeLowercase == True:
                            mainClauseText = mainClauseText[0].lower() + mainClauseText[1:]

                        # Ermittlung des Teilsatzendes
                        endOfSentencePart = ""
                        i = currentClauseIndex + 1
                        while i < len(relatedClauses):
                            endOfSentencePart += relatedClauses[currentClauseIndex].text
                            i += 1
                        i = relatedMainAndDependentClauses.index(relatedClauses) + 1
                        while i < len(relatedMainAndDependentClauses):
                            for relatedClausesForEnding in relatedMainAndDependentClauses[i]:
                                endOfSentencePart += relatedClausesForEnding.text
                                i += 1

                        # Vertauschung des Haupt- und Nebensatzes
                        changedSentence = self.mainAndDependentClauseChangeExecution(beginOfSentence, mainClauseText,
                                                                                     predicateStartPosition,
                                                                                     predicateEndPosition,
                                                                                     dependentClauseText,
                                                                                     endOfSentencePart, sentenceEnding)

                        # Satzanfang in Großbuchstaben umwandeln
                        changedSentence = changedSentence[0].capitalize() + changedSentence[1:]

                        changedVariations.append(changedSentence)
                        break
                    currentClauseIndex += 1

            # Hinzufügen des aktuellen Satzteiles zum Satzbeginn:
            for currentClause in relatedClauses:
                beginOfSentence += currentClause.text

        if not changedVariations:
            return None
        else:
            return changedVariations


    def getPositionIndexOfPredicate(self, mainClauseDoc):
        # Ermittlung der Position des Prädikats im Hauptsatz
        currentPosition = 0
        while currentPosition < len(mainClauseDoc):
            # Suche nach dem ersten Verb
            if mainClauseDoc[currentPosition].pos_ == "AUX" or mainClauseDoc[currentPosition].pos_ == "VERB":
                break
            currentPosition += 1

        predicateStartPosition = mainClauseDoc[currentPosition].idx - mainClauseDoc[0].idx
        predicateEndPosition = 0
        if currentPosition + 1 < len(mainClauseDoc):
            predicateEndPosition = mainClauseDoc[currentPosition + 1].idx - mainClauseDoc[0].idx
        else:
            predicateEndPosition = len(mainClauseDoc.text) - 1
        return predicateStartPosition, predicateEndPosition

    def mainAndDependentClauseChangeExecution(self, beginOfSentence, mainClause, predicateStartPosition,
                                              predicateEndPosition, dependentClause, endOfSentencePart, sentenceEnding):
        newSentence = beginOfSentence
        if beginOfSentence != "":
            newSentence += ", " + dependentClause
        else:
            newSentence += dependentClause

        # Modifierung des Hauptsatzes, damit das Prädikat an erster Stelle steht
        newSentence += ", " + mainClause[predicateStartPosition:predicateEndPosition]
        newSentence += mainClause[0:predicateStartPosition]
        if predicateEndPosition + 1 < len(mainClause):
            newSentence += mainClause[predicateEndPosition:len(mainClause)]

        newSentence += endOfSentencePart
        newSentence += sentenceEnding
        return newSentence

    def checkForMainClause(self, partOfSentenceWithoutConjunction):
        # Erste Überprüfung, ob es sich um einen Haupt- oder Nebensatz handelt
        # Feststellung der Position des Prädikats
        partOfSentenceIsMainClause = None
        predicateIsAtBegin = True
        currentPosition = 0
        while currentPosition < len(partOfSentenceWithoutConjunction):
            # Suche nach dem ersten Verb
            if partOfSentenceWithoutConjunction[currentPosition].pos_ == "AUX" or \
                    partOfSentenceWithoutConjunction[currentPosition].pos_ == "VERB":
                # Überprüfung, ob es sich nicht um die letzte Stelle des Satzes handelt
                if currentPosition != (len(partOfSentenceWithoutConjunction) - 1):
                    # Das Prädikat befindet sich nicht am Ende des Satzes
                    partOfSentenceIsMainClause = True

                    if currentPosition == 0:
                        predicateIsAtBegin = True
                    else:
                        predicateIsAtBegin = False
                else:
                    # Das Prädikat befindet sich am Ende des Satzes
                    partOfSentenceIsMainClause = False
                    predicateIsAtBegin = False
            currentPosition += 1
        return partOfSentenceIsMainClause, predicateIsAtBegin


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


    def removeKommaAndSpacesAtBeginningOfSentence(self, docOfSentencePart):
        currentCharacter = 0
        while currentCharacter < len(docOfSentencePart):
            if docOfSentencePart[currentCharacter].tag_ != "_SP" and docOfSentencePart[currentCharacter].tag_ != "$,":
                docOfSentencePart = docOfSentencePart[currentCharacter:]
                break
            currentCharacter += 1
        return docOfSentencePart


    def checkIfProperSentence(self, partOfSentence):
        # Ein vollständiger Satz muss mindestens ein Subjekt und ein Prädikat aufweisen
        sentenceContainsSubject = False
        sentenceContainsPredicate = False
        for word in partOfSentence:
            if word.pos_ == "NOUN" or word.pos_ == "PROPN" or word.pos_ == "PRON":
                sentenceContainsSubject = True
            elif word.pos_ == "AUX" or word.pos_ == "VERB":
                sentenceContainsPredicate = True
        if sentenceContainsSubject and sentenceContainsPredicate:
            return True
        else:
            return False

