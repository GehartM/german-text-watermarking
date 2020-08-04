import spacy
import os
import sys
import re
import hmac
import hashlib
import random
from collections import defaultdict

import characterEncoding
import positionEncoding
from treeNodeGetSignToBinaryCode import GetSignToBinaryCode
from messageCharacterObject import MessageCharacterObject
from possibleSentence import PossibleSentence

# Importierung der zu verwendenden Watermarking-Methoden
from prefixExpansion import PrefixExpansion
from conjunction import Conjunction
from contraction import Contraction
from abbreviations import Abbreviations
from synonymSubstitution import SynonymSubstitution
from mainAndDependentClausePermutation import MainAndDependentClausePermutation

# Globale Variable, um die Beziehungen der Satzglieder eines Satzes untereinander in einem String zu speichern
# Dies stellt die syntaktische Struktur des Satzes dar
dependeciesOfSentence = ""

# Globale Variable, welche den Namen der temporären Datei hält
temporaryFileName = "sentences.tmp"

# Globale Variable, um das Encoding des Textes zu speichern
encodingOfDocument = None


def showUsageOfProgram():
    global possibleWatermarkingMethods
    print("\nDie Parameter entsprechen nicht den Anforderungen!\n"
          "Benutzung:\n\n"
          "\tAuslesen eines Watermarks von einem Text (Modus -A):\n"
          "\t\tSyntax:\n"
          "\t\t\tpython WatermarkingProgram.py -A <AUSLESEMODUS> <PFAD ZUR MARKIERTEN DATEI> <GEHEIMER SCHLÜSSEL> "
          "<PFAD ZUR UNMARKIERTEN DATEI>\n"
          "\t\t\t\tAUSLESEMODUS:\t\t\t\tZur Auswahl steht ein blinder <-B> und ein nicht-blinder <-N> Modus.\n"
          "\t\t\t\tPFAD ZUR MARKIERTEN DATEI:\tAngabe des absoluten bzw. relativen Pfades zu jener Datei, aus der ein "
          "Watermark ausgelesen werden soll\n"
          "\t\t\t\tGEHEIMER SCHLÜSSEL:\t\t\tDies ist der geheime Schlüssel, welcher frei definierbar ist. Er darf Groß-"
          " und Kleinbuchstaben, Zahlen und Sonderzeichen enthalten. "
          "Dieser Schlüssel muss geheim gehalten werden, da mit Hilfe dieses Schlüssels das eingebettete Watermark "
          "wieder ausgelesen werden kann.\n"
          "\t\t\t\tPFAD ZUR UNMARKIERTEN DATEI:\tAngabe des absoluten bzw. relativen Pfades zur originalen unmarkierten"
          " Datei. Diese muss jedoch nur bei Verwendung des nicht-blinden Auslesemodus (-N) angegeben werden!\n\n"
          "\t\tBeispiele:\n"
          "\t\t\tpython WatermarkingProgram.py -A -B C:\\Users\\John\\Documents\\Protokoll.txt T0pS3cr3t\n"
          "\t\t\tpython WatermarkingProgram.py -A -N C:\\Users\\John\\Documents\\Protokoll.txt T0pS3cr3t C:\\Users\\"
          "John\\Documents\\Original.txt\n\n"
          "\tEinbetten eines Watermarks in einen Text (Modus -E):\n"
          "\t\tSyntax:\n"
          "\t\t\tpython WatermarkingProgram.py -E <EINBETTUNGSMODUS> <PFAD ZUR ORIGINALEN DATEI> <PFAD DER "
          "RESULTIERENDEN DATEI> <GEHEIMER SCHLÜSSEL> "
          "<EINZUBETTENDER TEXT> <WATERMARKINGMETHODEN>\n"
          "\t\t\t\tEINBETTUNGSMODUS:\t\t\tZur Auswahl steht ein blinder <-B> und ein nicht-blinder <-N> Modus.\n"
          "\t\t\t\tPFAD ZUR ORIGINALEN DATEI:\tAngabe des absoluten bzw. relativen Pfades zu jener Datei, welcher ein "
          "Watermark hinzugefügt werden soll\n"
          "\t\t\t\tPFAD DER RESULTIERENDEN DATEI:\tAngabe des absoluten bzw. relativen Pfades inklusive Dateinames "
          "unter welchem die markierte Datei gespeichert werden soll.\n"
          "\t\t\t\tGEHEIMER SCHLÜSSEL:\t\t\tDies ist der geheime Schlüssel, welcher frei definierbar ist. Er darf Groß-"
          " und Kleinbuchstaben, Zahlen und Sonderzeichen enthalten. "
          "Dieser Schlüssel muss geheim gehalten werden, da mit Hilfe dieses Schlüssels das eingebettete Watermark "
          "wieder ausgelesen werden kann.\n"
          "\t\t\t\tEINZUBETTENDER TEXT:\t\tStellt die einzubettende Nachricht dar. Es gilt hierbei eine Beschränkung "
          "von", len(positionEncoding.positionEncoding), "Zeichen und es sind nur ausgewählte Zeichen "
                                                         "verfügbar. Jene sind im Anschluss aufgeführt.\n"
                                                         "\t\t\t\tWATERMARKINGMETHODEN:\t\tEs können beliebig viele "
                                                         "Methoden nacheinander durch einen Abstand "
                                                         "getrennt aufgeführt werden. Es stehen die folgenden "
                                                         "Optionen zur Verfügung:")
    print("\t\t\t\t\t -A \t Alle Watermarking-Methoden sind erlaubt. Muss am Beginn der Watermarkingmethoden ohne "
          "nachfolgende Parameter stehen.")

    for abbreviation, methodObject in possibleWatermarkingMethods.items():
        print("\t\t\t\t\t", abbreviation, "\t", methodObject.getName())

    print(
        "\n\t\tBeispiele:\n\t\t\tpython WatermarkingProgram.py -E -B C:\\Users\\John\\Documents\\Protokoll.txt C:"
        "\\Users\\John\\Desktop\\Protokoll_Doe.txt "
        "T0pS3cr3t JohnDoe -P -K\n"
        "\t\t\tpython WatermarkingProgram.py -E -N C:\\Users\\John\\Documents\\Protokoll.txt C:\\Users\\John\\"
        "Desktop\\Protokoll_Doe.txt "
        "T0pS3cr3t JohnDoe -A\n\n"
        "\tErlaubte Zeichen für die einzubettende Nachricht sind:\n\t\t <Leerzeichen>", end="   ")

    for character in characterEncoding.characterEncoding.keys():
        print(character, end="   ")

    sys.exit(0)


def checkIfInputFileExists(filepath):
    if not os.path.isfile(filepath):
        print("\nDie angegebene originale Datei, welcher ein Watermark hinzugefügt werden soll, existiert nicht!\n"
              "Überprüfe den Dateipfad und den Namen der Datei.")
        sys.exit(0)
    return filepath


def checkIfOutputFileExists(filepath):
    if os.path.isfile(filepath):
        print(
            "\nDie Datei, in welche das Resultat des Watermarkings geschrieben werden soll, existiert an diesem "
            "Speicherort bereits!\n"
            "Wähle einen anderen Pfad oder Dateinamen.")
        sys.exit(0)
    return filepath


def checkLengthOfString(stringToBeChecked):
    # Überprüft, ob die maximal erlaubte Länge der einzubettenden Nachricht nicht überschritten wird
    if len(stringToBeChecked) > len(positionEncoding.positionEncoding):
        print("Die maximal erlaubte Länge des einzubettenden Textes wurde überschritten!\n"
              "Es sind maximal", len(positionEncoding.positionEncoding), "Stellen erlaubt.")
        sys.exit(0)


def checkForInvalidCharacters(stringToBeChecked):
    checkLengthOfString(stringToBeChecked)

    allowedCharacters = "[ "
    for character in characterEncoding.characterEncoding.keys():
        allowedCharacters += character
    allowedCharacters += "]*$"
    noIllegalCharacter = re.match(allowedCharacters, stringToBeChecked, re.IGNORECASE)

    if not noIllegalCharacter:
        print("\nEs wurden ungültige Zeichen im einzubettenden Text entdeckt!\n"
              "Groß- und Kleinschreibung wird nicht unterschieden.\n"
              "Es sind ausschließlich die nachfolgenden Zeichen erlaubt:\n"
              "\t <Leerzeichen>", end="   ")
        for character in characterEncoding.characterEncoding.keys():
            print(character, end="   ")

        sys.exit(0)
    return stringToBeChecked


def checkForInvalidWatermarkingMethod(method):
    global possibleWatermarkingMethods
    if method not in possibleWatermarkingMethods:
        print("\nEine der angegebenen Watermarking-Methoden konnte nicht gefunden werden!\n"
              "Die folgenden Methoden stehen zu Auswahl:\n"
              "\t -A \t Alle Watermarking-Methoden sind erlaubt. Muss am Beginn der Watermarkingmethoden ohne "
              "nachfolgende Parameter stehen.")

        for abbreviation, methodObject in possibleWatermarkingMethods.items():
            print("\t", abbreviation, "\t", methodObject.getName())

        sys.exit(0)


# possibleWatermarkingMethods führt alle im Programm verwendbaren Watermarking-Methoden auf.
# Als Schlüssel wird das Kürzel der jeweiligen Methode verwendet.
possibleWatermarkingMethods = dict({
    "-P": PrefixExpansion(),
    "-V": Contraction(),
    "-U": Abbreviations(),
    "-S": SynonymSubstitution(),
    "-K": Conjunction(),
    "-M": MainAndDependentClausePermutation()
})


pathToOutputFile = None                 # Hält den Pfad zur watergemarkten Datei
possibleWatermarkedSentences = dict()   # Speichert die Variationen aller Sätze der originalen Datei


def main():
    print("\n\t[+] Das Programm wird gestartet ...")
    isEmbedMode = True
    methodIsStatic = True
    pathToInputFile = None
    global pathToOutputFile
    pathToComparisonFile = None         # Wird nur im dynamischen Auslesemodus benötigt
    secretKey = None
    messageToEmbed = None
    watermarkingMethods = list()

    # Prüfung, ob ein Modus spezifiziert wurde
    if len(sys.argv) > 1:
        # Wahl des Modus
        if sys.argv[1] == "-E":
            # Einbettungsmodus
            isEmbedMode = True
            # Überprüfung, ob genügend Parameter übergeben wurden
            if len(sys.argv) > 6:
                # Die angegebenen Parameter werden im Program übernommen
                if sys.argv[2] == "-B":
                    # Die anzuwendenden Methoden sollen statisch (blind) agieren
                    methodIsStatic = True
                elif sys.argv[2] == "-N":
                    # Die anzuwendenden Methoden sollen dynamisch (nicht-blind) agieren
                    methodIsStatic = False
                else:
                    # Inkorrekte Angabe
                    print("Es wurde ein ungültiger Einbettungsmodus spezifiziert!\nErlaubt sind:\n\t-B\t"
                          "blinder Modus\n\t-N\tnicht-blinder Modus")
                    showUsageOfProgram()
                pathToInputFile = checkIfInputFileExists(sys.argv[3])
                pathToOutputFile = checkIfOutputFileExists(sys.argv[4])
                secretKey = sys.argv[5]

                # Alle Argumente bis zur Angabe der erlaubten Watermarking-Methoden gehören zur Nachricht
                inputMessage = ""
                beginOfMethods = None
                for i in range(6, len(sys.argv)):
                    if sys.argv[i][:1] == "-":
                        beginOfMethods = i
                        break
                    else:
                        if inputMessage != "":
                            inputMessage += " "
                        inputMessage += sys.argv[i]

                # Prüfung, ob die Watermarking-Methoden angegeben worden sind
                if beginOfMethods is None:
                    # Die Watermarking-Methoden wurden nicht spezifiziert
                    print("Die Watermarking-Methoden wurden nicht spezifiziert!")
                    showUsageOfProgram()

                messageToEmbed = checkForInvalidCharacters(inputMessage)

                # Prüfung, ob alle Watermarking-Methoden erlaubt sind oder nur Spezifische
                if sys.argv[beginOfMethods] == "-A":
                    for abbreviation in possibleWatermarkingMethods:
                        watermarkingMethods.append(possibleWatermarkingMethods[abbreviation])
                else:
                    for i in range(beginOfMethods, len(sys.argv)):
                        checkForInvalidWatermarkingMethod(sys.argv[i])
                        watermarkingMethods.append(possibleWatermarkingMethods[sys.argv[i]])
            else:
                # Es wurden nicht alle Parameter übergeben
                print("Es wurden zu wenig Parameter übergeben!")
                showUsageOfProgram()
        elif sys.argv[1] == "-A":
            # Auslesemodus
            isEmbedMode = False
            # Auslesemethode überprüfen
            if len(sys.argv) > 2:
                if sys.argv[2] == "-B":
                    # Statischer (blinder) Auslesemethode
                    methodIsStatic = True
                elif sys.argv[2] == "-N":
                    # Dynamischer (nicht-blinder) Auslesemethode
                    methodIsStatic = False
                else:
                    # Ungültige Eingabe
                    print("Es wurde ein ungültiger Auslesemodus spezifiziert!\nErlaubt sind:\n\t-B\t"
                          "blinder Modus\n\t-N\tnicht-blinder Modus")
                    showUsageOfProgram()
                # Überprüfung, ob genügend Parameter übergeben wurden
                if methodIsStatic is True and len(sys.argv) == 5:
                    # Die angegebenen Parameter werden im Program übernommen
                    pathToInputFile = checkIfInputFileExists(sys.argv[3])
                    secretKey = sys.argv[4]
                elif methodIsStatic is False and len(sys.argv) == 6:
                    # Die angegebenen Parameter werden im Program übernommen
                    pathToInputFile = checkIfInputFileExists(sys.argv[3])
                    secretKey = sys.argv[4]
                    pathToComparisonFile = sys.argv[5]

                    # Überprüpfung, ob die unmarkierte Originaldatei existiert
                    if not os.path.isfile(pathToComparisonFile):
                        print("\nDie angegebene originale Datei, welcher als Referenz dient, existiert nicht!"
                              "\nÜberprüfe den Dateipfad und den Namen der Datei.")
                        showUsageOfProgram()
                        sys.exit(0)
                else:
                    # Die Anzahl der übergebenen Parameter stimmt nicht
                    print("Die Anzahl der übergebenen Argumente ist nicht korrekt!")
                    showUsageOfProgram()
        else:
            # Invalider Modus spezifiziert
            print("Es wurde ein invalider Modus spezifiziert!")
            showUsageOfProgram()
    else:
        # Es wurde kein Modus angegeben
        print("Es wurde kein Modus spezifiziert!")
        showUsageOfProgram()

    nlp = spacy.load("de_core_news_sm")  # Laden des deutschen Sprachmoduls

    # keyAsByteArray speichert den vom Benutzer spezifizierten geheimen Schlüssel, welcher für das Watermark
    # verwendet werden soll
    keyAsByteArray = bytearray()
    keyAsByteArray.extend(secretKey.encode())

    if isEmbedMode:
        # Ausgabe des Secret Keys und der einzubettenden Nachricht, um den Benutzer über die wichtigsten Informationen
        # zu informieren
        print("\nDer Text '{}' wird mit dem Secret Key '{}' in das Dokument '{}' eingebettet und unter '{}' "
              "gespeichert.".format(messageToEmbed, secretKey, pathToInputFile, pathToOutputFile))
        if methodIsStatic:
            print("\nDas originale Dokument ohne Watermark wird für das Auslesen des eingebetteten Textes nicht mehr "
                  "benötigt.\n")
        else:
            print("\nDas originale Dokument ohne Watermark muss für das Auslesen des eingebetteten Textes "
                  "bereitgestellt werden.\nAus diesem Grund muss das Original erhalten bleiben und an einem sicheren "
                  "Medium verwahrt werden, um Manipulationen an diesem ausschließen zu können!\n")

        print("\t[+] Der Einbettungsmodus wird gestartet ...")
        embedWatermark(nlp, pathToInputFile, keyAsByteArray, messageToEmbed, watermarkingMethods, methodIsStatic)
        print("\nDer Einbettungsprozess konnte erfolgreich abgeschlossen werden.\nDas markierte Dokument wurde "
              "unter \'" + pathToOutputFile + "\' gespeichert.")
    else:
        print("\t[+] Das Watermark wird aus dem übergebenen Text ausgelesen ...\n")
        if methodIsStatic:
            getWatermark(nlp, pathToInputFile, keyAsByteArray, methodIsStatic)
        else:
            getWatermark(nlp, pathToInputFile, keyAsByteArray, methodIsStatic, pathToComparisonFile)


def embedWatermark(nlp, pathToInputFile, keyAsByteArray, messageToEmbed, watermarkingMethods, methodIsStatic):
    # Konvertierung der einzubettenden Nachricht in Großbuchstaben
    messageToEmbed = messageToEmbed.upper()

    # Aufbereitung des einzubettenden Textes
    # Erstellung der CharToEmbedComponent-Objekte, sowie der zugehörigen CharToEmbedComponentPosition-Objekte und
    # Speicherung dieser in einem Dictionary
    messageCharacters = dict()
    for i in range(len(messageToEmbed)):
        if messageToEmbed[i] not in messageCharacters:
            # Hinzufügen des Zeichens zum Dictionary
            messageCharacters[messageToEmbed[i]] = MessageCharacterObject(messageToEmbed[i])
        # Erweiterung, um die neue Stelle des Buchestabens in der einzubettenden Nachricht
        messageCharacters[messageToEmbed[i]].positionInMessage.append(str(i))

    fileContent = getContentOfFile(pathToInputFile)

    # Initialisierung der Watermarking Methoden
    for method in watermarkingMethods:
        method.initializeMethod(nlp)

    doc = getProcessedTextOfDocument(nlp, fileContent)  # Speicherung des aufbereiteten Textes

    # Sofern die temporäre Datei bereits existiert, wird diese geleert
    if os.path.exists(temporaryFileName):
        open(temporaryFileName, 'w', encoding=encodingOfDocument).close()

    # Prozessierung der einzelnen Sätze
    print("\t[+] Der Text wird prozessiert ...")
    allSentences = list(doc.sents)          # Umwandlung der Sätze in eine Liste
    currentSentenceIndex = 1                # Gestartet wird mit dem 2. Satz, da der Satz davor als Marker dient

    # Speicherung des ersten Satzes des Textes
    firstSentenceDoc = allSentences[0].as_doc()

    # Prüfe, ob das erste Bit dem Wert 0 entspricht, um diesen Satz als watermarklosen Satz zu speichern
    if checkIfSentenceIsWithoutWatermark(firstSentenceDoc, keyAsByteArray):
        saveSentenceToTemporaryFile(0, None, firstSentenceDoc.text, valueOfSentenceStartsWithZero=True)
    else:
        # Der Wert entspricht nicht 0. Dennoch soll der ursprüngliche Satz gespeichert werden
        saveSentenceToTemporaryFile(0, None, firstSentenceDoc.text)

    while currentSentenceIndex != len(allSentences):
        # Generierung eines Doc-Objektes für jeden einzelnen Satz
        docOfSentence = allSentences[currentSentenceIndex].as_doc()

        # Überprüfung, ob bereits ein Zeichen ausgelesen werden kann
        matchedCharacter = getCharacterOfSentence(docOfSentence, keyAsByteArray)

        # Nur im statischen Modus darf ein unveränderter Satz als Möglichkeit aufgenommen werden
        if methodIsStatic and matchedCharacter is not None:
            # Prüfung, ob das Zeichen in der einzubettenden Nachricht beinhaltet ist
            if matchedCharacter in messageCharacters:
                # Prüfe, ob es möglich ist die Position des Zeichens in den Marker-Satz einzubetten
                # Generierung eines Doc-Objektes für den vorhergehenden Satz
                docOfPreviousSentence = allSentences[currentSentenceIndex - 1].as_doc()

                # Einbettung der Position in den vorhergehenden Satz
                if currentSentenceIndex != 1:
                    getAllPositionsOfSentence(nlp, keyAsByteArray, watermarkingMethods, methodIsStatic,
                                              messageCharacters[matchedCharacter], currentSentenceIndex - 1,
                                              docOfSentence, docOfPreviousSentence,
                                              embedMethodSentenceWithWatermarked=None)
                else:
                    # Es handelt sich um den zweiten Satz, welcher Bezug zum ersten Satz nimmt
                    getAllPositionsOfSentence(nlp, keyAsByteArray, watermarkingMethods, methodIsStatic,
                                              messageCharacters[matchedCharacter], currentSentenceIndex - 1,
                                              docOfSentence, docOfPreviousSentence,
                                              embedMethodSentenceWithWatermarked=None)
            else:
                # Der aktuelle Buchstabe wird nicht benötigt
                # Dennoch wird der Satz abgespeichert
                saveSentenceToTemporaryFile(currentSentenceIndex, None, docOfSentence.text)
        else:
            # In diesem Satz ist kein Watermark vorhanden oder es wird die dynamische Einbettungsmethode verwendet
            # Prüfe, ob das erste Bit dem Wert 0 entspricht, um diesen Satz als watermarklosen Satz zu speichern
            if checkIfSentenceIsWithoutWatermark(docOfSentence, keyAsByteArray):
                saveSentenceToTemporaryFile(currentSentenceIndex, None, docOfSentence.text,
                                            valueOfSentenceStartsWithZero=True)
            else:
                # Der Wert entspricht nicht 0
                # Dennoch soll der ursprüngliche Satz gespeichert werden
                saveSentenceToTemporaryFile(currentSentenceIndex, None, docOfSentence.text)

        # Anwenden der diversen Watermarking Methoden, um die gewünschten Bits einzubetten
        for method in watermarkingMethods:
            changedSentences = method.process(docOfSentence, nlp)
            if changedSentences is not None:
                for changedSentence in changedSentences:
                    # Neugenerierung des doc-Elementes mit dem veränderten Satz
                    newDoc = getProcessedTextOfDocument(nlp, changedSentence)

                    # Überprüfung, ob der Satz durch die angewendete Methode geändert wurde
                    if checkIfSentencesAreDifferent(docOfSentence, newDoc):

                        # Prüfung, ob ein Zeichen eingebettet werden konnte
                        matchedCharacter = getCharacterOfSentence(newDoc, keyAsByteArray)
                        if matchedCharacter is not None:

                            # Prüfung, ob das Zeichen in der einzubettenden Nachricht beinhaltet ist
                            if matchedCharacter in messageCharacters:

                                # Prüfe, ob es möglich ist die Position des Zeichens in den Marker-Satz einzubetten
                                # Generierung eines Doc-Objektes für den vorhergehenden Satz
                                docOfPreviousSentence = allSentences[currentSentenceIndex - 1].as_doc()

                                # Einbettung der Position in den vorhergehenden Satz
                                if currentSentenceIndex != 1:
                                    getAllPositionsOfSentence(nlp, keyAsByteArray, watermarkingMethods, methodIsStatic,
                                                              messageCharacters[matchedCharacter],
                                                              currentSentenceIndex - 1, newDoc, docOfPreviousSentence,
                                                              embedMethodSentenceWithWatermarked=method)
                                else:
                                    # Es handelt sich um den zweiten Satz, welcher Bezug zum ersten Satz nimmt
                                    getAllPositionsOfSentence(nlp, keyAsByteArray, watermarkingMethods, methodIsStatic,
                                                              messageCharacters[matchedCharacter],
                                                              currentSentenceIndex - 1, newDoc, docOfPreviousSentence,
                                                              True,
                                                              embedMethodSentenceWithWatermarked=method)
                        else:
                            # In diesem Satz ist kein Watermark vorhanden
                            # Prüfe, ob das erste Bit dem Wert 0 entspricht, um diesen Satz als watermarklosen Satz
                            # zu speichern
                            # Führe diese Überprüfung, nur im statischen Modus aus
                            if methodIsStatic and checkIfSentenceIsWithoutWatermark(newDoc, keyAsByteArray):
                                saveSentenceToTemporaryFile(currentSentenceIndex, method, newDoc.text,
                                                            valueOfSentenceStartsWithZero=True)
        currentSentenceIndex += 1

    watermarkedFragmentsOfText = checkIfAllMessagePartsAreSatisfied(messageToEmbed, methodIsStatic)

    if watermarkedFragmentsOfText is None:
        print("\nDie Nachricht kann in dem gegebenen Text in Kombination mit dem spezifizierten Schlüssel nicht "
              "eingebettet werden!")
        textCanNotBeWatermarked()
    else:
        # Generierung und Exportierung des Textes mit enthaltenem Watermark
        print("\t[+] Der markierte Text wird erstellt ...")
        createWatermarkedText(watermarkedFragmentsOfText, methodIsStatic)

    # Löschung der temporäre Datei mit den zwischengespeicherten Sätzen
    if os.path.exists(temporaryFileName):
        os.remove(temporaryFileName)


def getWatermark(nlp, pathToInputFile, keyAsByteArray, methodIsStatic, pathToComparisonFile=None):
    countOfFormatConflicts = 0                  # Wird bei jedem gefundenen Formatierungsfehler erhöht
    retrievedMessages = dict()                  # Speichert die ausgelesenen Zeichen mit ihrer jeweiligen Position
    retrievedMessage = ""                       # Hält die ausgelesene Nachricht
    detailedInfoOfRetrievedMessage = dict()     # Beinhaltet die genaue Auflistung aller Informationen eines Zeichens
    watermarkFragmentsWithoutMarker = list()    # Hält alle Watermarkfragmente zu welchen die zugehörigen Marker fehlen

    # Auslesen des markierten Textes
    fileContent = getContentOfFile(pathToInputFile)

    # Prozessierung der einzelnen Sätze
    doc = getProcessedTextOfDocument(nlp, fileContent)  # Speicherung des aufbereiteten Textes
    allSentences = list(doc.sents)
    allOriginalSentences = None # Liste mit allen Sätzen des originalen Textes bei Verwendung der dynamischen Methode

    # Soll die dynamische Auslesemethode verwendet werden, so muss das originale Dokument ebenfalls prozessiert werden
    if not methodIsStatic:
        originalFileContent = getContentOfFile(pathToComparisonFile)
        originalDoc = getProcessedTextOfDocument(nlp, originalFileContent)
        allOriginalSentences = list(originalDoc.sents)

    currentSentenceIndex = 0
    while currentSentenceIndex < (len(allSentences) - 1):
        # In der dynamischen Methode wird ein Satz nur auf einen enthaltenen Marker oder Watermark überprüft,
        # sofern sich der Satz vom originalen Satz an der aktuellen Stelle unterscheidet
        if not methodIsStatic:
            if allSentences[currentSentenceIndex].text == allOriginalSentences[currentSentenceIndex].text:
                # Die beiden Sätze stimmen überein, daher kann mit dem nächsten Satz fortgefahren werden
                currentSentenceIndex += 1
                continue

        # Generierung eines doc-Objektes für jeden einzelnen Satz
        docOfSentence = allSentences[currentSentenceIndex].as_doc()

        # Überprüfung, ob es sich um einen Marker-Satz handelt
        retrievedPosition = getPositionNumberOfSentence(docOfSentence, keyAsByteArray)

        if retrievedPosition is not None:
            # Prüfung, ob in dem nachfolgendem Satz ein Zeichen eingebettet ist
            currentSentenceIndex += 1

            retrievedCharacter = getCharacterOfSentence(docOfSentence, keyAsByteArray)
            if retrievedCharacter is not None:
                # Es konnte ein Zeichen ausgelesen werden
                # Überprüfung, ob noch kein Watermarkfragment für diese Stelle gefunden wurde
                if retrievedPosition not in retrievedMessages:
                    retrievedMessages[retrievedPosition] = defaultdict(int)

                # Speichere das Zeichen unter der dazugehörigen Stelle ab
                retrievedMessages[retrievedPosition][retrievedCharacter] += 1
            else:
                # Eine widersprüchliche Formatierung wurde gefunden
                # Nach einem Marker-Satz müsste ein Watermarkfragment folgen
                # Dies kann auf einen Änderungsversuch des Watermark hinweisen
                countOfFormatConflicts += 1
                currentSentenceIndex -= 1
        else:
            # Überprüfung, ob es sich um ein Watermarkingfragment handelt bei dem der Marker nicht mehr auslesbar ist
            retrievedCharacter = getCharacterOfSentence(docOfSentence, keyAsByteArray)
            if retrievedCharacter is not None:
                # Es konnte ein Zeichen ausgelesen werden
                # Speichere das Zeichen als nicht zuordenbares Zeichen ab
                watermarkFragmentsWithoutMarker.append(retrievedCharacter)

                # Es handelt sich dabei um eine widersprüchliche Formatierung
                # Vor einem Watermarkfragment müsste sich ein Marker-Satz befinden
                # Dies kann auf einen Änderungsversuch des Watermark hinweisen
                countOfFormatConflicts += 1

        currentSentenceIndex += 1

    # Überprüfung, ob eine Mehrdeutigkeit innerhalb einer Nachrichtenposition auftritt
    # Gleichezeitig wird der Text für die Ausgabe vorbereitet
    lastCharacterPosition = 0       # Wird verwendet, um Abstände in der erhaltenen Nachricht festzustellen
    for currentPosition in retrievedMessages:
        bestMatchedCharacter = None
        occuranceOfBestMatchedCharacer = 0

        # Anzahl der gefundenen Zeichen für diese Position
        totalCountOfCharacterForCurrentPosition = 0
        for character in retrievedMessages[currentPosition].keys():
            totalCountOfCharacterForCurrentPosition += retrievedMessages[currentPosition][character]

        for character, occurance in retrievedMessages[currentPosition].items():
            # Speicherung des häufigsten Zeichens
            if occurance > occuranceOfBestMatchedCharacer:
                occuranceOfBestMatchedCharacer = occurance
                bestMatchedCharacter = character

            # Speicherung des Zeichens in dem Dictionary mit allen Möglichkeiten
            # Prüfung, ob bereits ein Zeichen für diese Stelle abgespeichert wurde
            if int(currentPosition) not in detailedInfoOfRetrievedMessage:
                detailedInfoOfRetrievedMessage[int(currentPosition)] = list()
                firstLine = ""
                detailedInfoOfRetrievedMessage[int(currentPosition)].append(firstLine)
                secondLine = "     ¯     "
                detailedInfoOfRetrievedMessage[int(currentPosition)].append(secondLine)

            # Errechnung der Prozentzahl
            percentage = totalCountOfCharacterForCurrentPosition / occurance
            percentage -= 1
            percentage = percentage * 100

            lineWithCurrentCharacter = " " + character + " -> " + "{0:03}".format(percentage) + "% \n\n"
            detailedInfoOfRetrievedMessage[int(currentPosition)].append(lineWithCurrentCharacter)

        # Überprüfung, ob vor dem aktuellen Zeichen ein oder mehrere Abstände sind
        for difference in range(lastCharacterPosition, int(currentPosition)):
            retrievedMessage += " "

        # Speicherung jenes Zeichens, welches am Häufigsten aufgetreten ist
        retrievedMessage += bestMatchedCharacter
        firstLineWithBestMatchedCharacter = "     " + bestMatchedCharacter + "     "
        detailedInfoOfRetrievedMessage[int(currentPosition)][0] = firstLineWithBestMatchedCharacter

        lastCharacterPosition = int(currentPosition)

    # Ausgabe des Ergebnisses
    # Überprüfung, ob ein Formatierungskonflikt vorliegt
    if countOfFormatConflicts == 0:
        print("Es liegen keine Widersprüchlichkeiten in der Formatierung des Textes vor.\n")
    elif countOfFormatConflicts == 1:
        print("Es wurde eine Widersprüchlichkeit in der Formatierung des Textes gefunden.\nDies kann ein Indiz für "
              "einen Änderungsversuch des Watermarks sein.\n")
    else:
        print("Es wurden", countOfFormatConflicts, "Widersprüchlichkeit in der Formatierung des Textes gefunden.\nDies "
                                                   "kann ein Indiz für einen Änderungsversuch des Watermarks sein.\n")

    # Überprüfung, ob die Nachricht eindeutig ausgelesen werden konnte
    # Ermittlung der Anzahl der höcshten Möglichkeiten für ein Zeichen
    highestCountOfPossibilities = 0
    for character in detailedInfoOfRetrievedMessage:
        if len(detailedInfoOfRetrievedMessage[character]) - 2 > highestCountOfPossibilities:
            highestCountOfPossibilities = len(detailedInfoOfRetrievedMessage[character]) - 2

    if highestCountOfPossibilities == 1:
        print("Die eingebettete Nachricht konnte eindeutig identifiziert werden.\n\n\tSie lautet:\t\t",
              retrievedMessage, "\n")
    else:
        print("Es wurden mehrdeutige eingebettete Nachrichtenteile gefunden.\nDies kann ein Indiz für einen "
              "Änderungsversuch des Watermarks sein.\n\n\tDie höchste Übereinstimmung der eingebetteten Nachricht "
              "ist:\n\t\t", retrievedMessage)

        # Ausgabe der detaillierten Informationen zu jeder Nachrichtenstelle
        print("\nNachfolgend sind alle auslesbaren Bestandteile mit ihrer jeweiligen Auftrittshäufigkeit "
              "aufgelistet:\n")
        sentencePosition = 0

        while sentencePosition < highestCountOfPossibilities:
            messagePosition = 0
            while messagePosition < (len(detailedInfoOfRetrievedMessage) - 1):
                # Überprüfung, ob die aktuelle sentencePosition in der Liste vorhanden ist
                if sentencePosition >= len(detailedInfoOfRetrievedMessage[messagePosition]):
                    # Für die aktuelle Position sind weniger Möglichkeiten vorhanden, als die Tabelle Zeilen aufweist
                    print("           ", end="|")
                messagePosition += 1

            # Ausgabe der detaillierten Information für die letzte Stelle
            # Überprüfung, ob die aktuelle sentencePosition in der Liste vorhanden ist
            if sentencePosition >= len(detailedInfoOfRetrievedMessage[messagePosition]):
                # Für die aktuelle Position sind weniger Möglichkeiten vorhanden, als die Tabelle Zeilen aufweist
                print("           ", end="|")
            sentencePosition += 1


def getContentOfFile(pathToInputFile):
    f = None
    content = None
    try:
        encodingOfDocument = "utf8"
        f = open(pathToInputFile, "r", encoding=encodingOfDocument)
        content = f.read()
    except UnicodeDecodeError:
        f.close()
        try:
            encodingOfDocument = "utf16"
            f = open(pathToInputFile, "r", encoding=encodingOfDocument)
            content = f.read()
        except UnicodeDecodeError:
            f.close()
            try:
                encodingOfDocument = "utf32"
                f = open(pathToInputFile, "r", encoding=encodingOfDocument)
                content = f.read()
            except UnicodeDecodeError:
                # Die Datei weist kein unterstütztes Kodierungsformat auf
                f.close()
                print("\nDas Kodierungsformat der Datei wird nicht unterstützt!\n"
                      "Die erlaubten Kodierungsmethoden sind:\n"
                      "\t- utf-8\n"
                      "\t- utf-16\n"
                      "\t- utf-32\n")
                exit(0)
    f.close()
    return content


def findRootNodeForPreOrderTraversal(doc):
    for token in doc:
        # Bei der Root-Node wird mit der Navigation durch den generierten Baum begonnen
        if token.dep_ == "ROOT":
            preOrderTraversal(token)


def preOrderTraversal(token):
    # Das Durchlaufen aller Kind-Objekte, sowie die Ausführung der Funktion soll nur ausgeführt werden, sofern es
    # sich nicht um ein Satzzeichen handelt
    if token.dep_ != "punct":
        for child in token.children:
            preOrderTraversal(child)

        # Es handelt sich um das letzte Element eines Astes des Baums bzw. um das nächstfolgende Objekt
        addDependencyOfTokenToGlobalString(token)


def addDependencyOfTokenToGlobalString(token):
    global dependeciesOfSentence
    dependeciesOfSentence = dependeciesOfSentence + token.dep_


def createHmacOfDependencyString(key):
    global dependeciesOfSentence
    dependeciesOfSentence = dependeciesOfSentence.encode()
    hashOfDependecies = hmac.new(key, dependeciesOfSentence, hashlib.sha256).digest()

    # Speicherung der ersten beiden Stellen des Binary-Arrays, jedoch ohne den prefix "0b"
    binaryResult = bin(hashOfDependecies[0])[2:].zfill(4) + bin(hashOfDependecies[1])[2:].zfill(4)
    return binaryResult[:7]


def getCharacterOfSentence(doc, keyAsByteArray):
    # Zurücksetzen der Variable, um sicher zu stellen, dass keine alten Beziehungen aus dem vorhergehenden Satz übernommen werden
    global dependeciesOfSentence
    dependeciesOfSentence = ""

    # Speicherung der Abhängigkeiten des aktuellen Satzes
    findRootNodeForPreOrderTraversal(doc)

    # Generierung des Abhängigkeits-Hashes für den aktuellen Satz
    resultedBits = createHmacOfDependencyString(keyAsByteArray)

    # Überprüfung, welchem Zeichen der aktuelle Satz entspricht
    matchedCharacter = GetSignToBinaryCode(resultedBits, characterEncoding.GetRootTreeNode())
    return matchedCharacter


def getPositionNumberOfSentence(doc, keyAsByteArray):
    # Zurücksetzen der Variable, um sicher zu stellen, dass keine alten Beziehungen aus dem vorhergehenden Satz übernommen werden
    global dependeciesOfSentence
    dependeciesOfSentence = ""

    # Speicherung der Abhängigkeiten des aktuellen Satzes
    findRootNodeForPreOrderTraversal(doc)

    # Generierung des Abhängigkeits-Hashes für den aktuellen Satz
    resultedBits = createHmacOfDependencyString(keyAsByteArray)

    # Überprüfung, welcher Position der aktuelle Satz entspricht
    matchedPosition = GetSignToBinaryCode(resultedBits, positionEncoding.GetRootTreeNode())
    return matchedPosition


def checkIfSentencesAreDifferent(originalSentenceDoc, changedSentenceDoc):
    if originalSentenceDoc.text == changedSentenceDoc.text or originalSentenceDoc.text == changedSentenceDoc.text + " ":
        # Die Sätze sind ident
        return False
    else:
        # Die Sätze unterscheiden sich
        return True


def getAllPositionsOfSentence(nlp, keyAsByteArray, watermarkingMethods, methodIsStatic, messageCharacterObject,
                              sentenceIdOfMarkerOrNoneWatermark, docWatermarkedSentence, docOfPositionSentence,
                              firstSentenceOfText=False, embedMethodSentenceWithWatermarked=None):
    # Überprüfung, ob bereits eine Position ausgelesen werden kann
    detectedPosition = checkIfPositionCanBeRetrieved(docOfPositionSentence, keyAsByteArray, messageCharacterObject)
    # Nur bei Verwendung der statischen Methode darf ein unveränderter Satz verwendet werden
    if methodIsStatic:
        if detectedPosition is not None:
            # Speichere den Satz mit Zeichen und Position als Möglichkeit ab
            saveSentenceToTemporaryFile(sentenceIdOfMarkerOrNoneWatermark, None, docOfPositionSentence.text,
                                        docWatermarkedSentence.text,
                                        embedMethodWatermarkedSentence=embedMethodSentenceWithWatermarked,
                                        relatedMessagePosition=detectedPosition)
        elif firstSentenceOfText:
            # In diesem Satz ist keine valide Position auslesbar und es handelt sich um den ersten Satz des Textes
            # Prüfe, ob das erste Bit dem Wert 0 entspricht, um diesen Satz als markerlosen Satz zu speichern
            if checkIfSentenceIsWithoutWatermark(docOfPositionSentence, keyAsByteArray):
                saveSentenceToTemporaryFile(sentenceIdOfMarkerOrNoneWatermark, None, docOfPositionSentence.text,
                                            valueOfSentenceStartsWithZero=True, relatedMessagePosition=detectedPosition)

    # Anwenden der diversen Watermarking Methoden, um die gewünschten Positionen einzubetten
    for methodToEmbedPosition in watermarkingMethods:
        changedPositionSentences = methodToEmbedPosition.process(docOfPositionSentence, nlp)
        # Überprüfung, ob durch die Anwendung der Methode eine Änderung des Satzes erreicht werden konnte
        if changedPositionSentences is not None:
            for changedPositionSentence in changedPositionSentences:
                # Neugenerierung des doc-Elementes mit dem veränderten Satz
                newDocOfPositionSentence = getProcessedTextOfDocument(nlp, changedPositionSentence)
                # Überprüfung, ob der Satz durch die Methode geändert werden konnte
                if checkIfSentencesAreDifferent(docOfPositionSentence, newDocOfPositionSentence):
                    # Überprüfung, ob die gewünschte Position eingebettet wurde
                    detectedPosition = checkIfPositionCanBeRetrieved(newDocOfPositionSentence, keyAsByteArray,
                                                                     messageCharacterObject)
                    if detectedPosition is not None:
                        # Speichere den Satz mit Zeichen und Position als Möglichkeit ab
                        saveSentenceToTemporaryFile(sentenceIdOfMarkerOrNoneWatermark, methodToEmbedPosition,
                                                    newDocOfPositionSentence.text, docWatermarkedSentence.text,
                                                    embedMethodWatermarkedSentence=embedMethodSentenceWithWatermarked,
                                                    relatedMessagePosition=detectedPosition)
                    elif firstSentenceOfText:
                        # In diesem Satz ist keine valide Position auslesbar und es handelt sich um den ersten Satz des
                        # Textes. Prüfe, ob das erste Bit dem Wert 0 entspricht, um diesen Satz als markerlosen Satz
                        # zu speichern
                        if checkIfSentenceIsWithoutWatermark(newDocOfPositionSentence, keyAsByteArray):
                            saveSentenceToTemporaryFile(sentenceIdOfMarkerOrNoneWatermark, methodToEmbedPosition,
                                                        newDocOfPositionSentence.text,
                                                        valueOfSentenceStartsWithZero=True,
                                                        relatedMessagePosition=detectedPosition)


def saveSentenceToTemporaryFile(sentenceIdOfMarkerOrNoneWatermark, embedMethodOfMarkerOrNoneWatermark,
                                markerOrNotWatermarkedSentence,
                                watermarkedSentence=None, embedMethodWatermarkedSentence=None,
                                valueOfSentenceStartsWithZero=False, relatedMessagePosition=None):
    global possibleWatermarkedSentences
    # Prüfung, ob die Satzposition noch nicht im Dictionary "possibleWatermarkedSentences" enthalten ist
    if sentenceIdOfMarkerOrNoneWatermark not in possibleWatermarkedSentences:
        possibleWatermarkedSentences[sentenceIdOfMarkerOrNoneWatermark] = list()

    # Prüfung, ob es sich um einen Satz mit eingebettetem Watermark handelt oder nicht
    if watermarkedSentence is None:
        # Es handelt sich um einen Satz ohne Watermark
        # Exportierung des Satzes in die temporäre Datei
        startPosition, endPosition = exportSentenceToTemporaryFile(markerOrNotWatermarkedSentence)
        possibleWatermarkedSentences[sentenceIdOfMarkerOrNoneWatermark].append(
            PossibleSentence(sentenceIdOfMarkerOrNoneWatermark, startPosition, endPosition,
                             embedMethodOfMarkerOrNoneWatermark,
                             valueOfSentenceStartsWithZero=valueOfSentenceStartsWithZero))
    else:
        # Es handelt sich um einen Marker- und eingebettenten Satz
        # Exportierung des Markers in die temporäre Datei
        startPosition, endPosition = exportSentenceToTemporaryFile(markerOrNotWatermarkedSentence)
        possibleWatermarkedSentences[sentenceIdOfMarkerOrNoneWatermark].append(
            PossibleSentence(sentenceIdOfMarkerOrNoneWatermark, startPosition, endPosition,
                             embedMethodOfMarkerOrNoneWatermark))

        # Exportierung des eingebetteten Satzes in die temporäre Datei
        startPosition, endPosition = exportSentenceToTemporaryFile(watermarkedSentence)
        possibleWatermarkedSentences[sentenceIdOfMarkerOrNoneWatermark][len(
            possibleWatermarkedSentences[sentenceIdOfMarkerOrNoneWatermark])- 1].\
            watermarkedSentencesOfCurrentMarker = PossibleSentence(sentenceIdOfMarkerOrNoneWatermark + 1,
                                                                   startPosition, endPosition,
                                                                   embedMethodWatermarkedSentence,
                                                                   relatedMessagePosition=relatedMessagePosition)


def checkIfAllMessagePartsAreSatisfied(messageToEmbed, methodIsStatic):
    global possibleWatermarkedSentences

    # Erstellung eines Dictionary, welches für jede Stelle der Message alle möglichen Sätze speichert
    messageWithRelatedSentences = dict()
    for i in range(len(messageToEmbed)):
        messageWithRelatedSentences[str(i)] = list()

    # Füllung des Dictionary mit den möglichen Sätzen
    for sentencesAtTextPosition in possibleWatermarkedSentences:
        for sentence in possibleWatermarkedSentences[sentencesAtTextPosition]:
            # Prüfung, ob es sich um einen Satz mit Watermarkfragment handelt
            if sentence.watermarkedSentencesOfCurrentMarker is not None:
                messageWithRelatedSentences[sentence.watermarkedSentencesOfCurrentMarker.relatedMessagePosition].\
                    append(sentence)

    # Auswahl der besten Sätze und Verwerfung von Überschneidungen
    # Für jene Nachrichtenteile, welche nur 1-Mal eingebettet werden konnten, gibt es nur einen Satz
    # Dieser Satz ist daher exklusiv diesem Nachrichtenteil zuzuordnen
    while True:
        listChanged = False     # Wird, True, sofern in diesem Durchlauf eine Löschung stattgefunden hat
        for currentMessagePosition in range(len(messageWithRelatedSentences)):
            # Prüfung, ob ein Nachrichtenteil nur 1-Mal referenziert ist
            if len(messageWithRelatedSentences[str(currentMessagePosition)]) == 1:
                # Löschung des Satzes aus allen anderen Listen
                for possibleSentenceOfCurrentMessagePosition in range(len(messageWithRelatedSentences)):
                    if possibleSentenceOfCurrentMessagePosition is not currentMessagePosition:
                        for sentenceOfList in messageWithRelatedSentences[str(
                                possibleSentenceOfCurrentMessagePosition)]:
                            if sentenceOfList.sentenceId == messageWithRelatedSentences[str(
                                    currentMessagePosition)][0].sentenceId:
                                # Löschung des Objektes aus der Liste
                                messageWithRelatedSentences[str(possibleSentenceOfCurrentMessagePosition)].pop(
                                    messageWithRelatedSentences[str(possibleSentenceOfCurrentMessagePosition)].index(
                                        sentenceOfList))
                                listChanged = True
        if not listChanged:
            break

    # Ist ein Satz innerhalb einer Liste öfter vertreten, so soll die geeignetste Einbettungs-Methode verwendet werden
    for currentMessagePosition in range(len(messageWithRelatedSentences)):
        indexSentenceOfListPosition = 0
        while indexSentenceOfListPosition < len(messageWithRelatedSentences[str(currentMessagePosition)]):
            # Generierung eines Ratings für den aktuellen Satz, um diesen vergleichen zu können
            scoreOfSentence = calculateScoreOfMarkerAndWatermarkedSentence(
                messageWithRelatedSentences[str(currentMessagePosition)][
                    indexSentenceOfListPosition].embedMethod,
                messageWithRelatedSentences[str(currentMessagePosition)][
                    indexSentenceOfListPosition].watermarkedSentencesOfCurrentMarker.embedMethod)

            # Iterierung über alle Objekte der Liste, um zu sehen, ob eine übereinstimmende sentenceId gefunden
            # werden kann
            indexsentenceOfListPositionCountercheck = 0
            while indexsentenceOfListPositionCountercheck < len(messageWithRelatedSentences[str(
                    currentMessagePosition)]):
                if messageWithRelatedSentences[str(currentMessagePosition)][
                    indexSentenceOfListPosition].sentenceId == \
                        messageWithRelatedSentences[str(currentMessagePosition)][
                            indexsentenceOfListPositionCountercheck].sentenceId:
                    # Überprüfung, ob es sich nicht um den gleichen Satz handelt
                    if messageWithRelatedSentences[str(currentMessagePosition)].index(
                            messageWithRelatedSentences[str(currentMessagePosition)][
                                indexSentenceOfListPosition]) != messageWithRelatedSentences[
                        str(currentMessagePosition)].index(
                            messageWithRelatedSentences[str(currentMessagePosition)][
                                indexsentenceOfListPositionCountercheck]):
                        # Generierung eines Ratings für den zu vergleichenden Satz
                        scoreOfCountercheckSentece = calculateScoreOfMarkerAndWatermarkedSentence(
                            messageWithRelatedSentences[str(currentMessagePosition)][
                                indexsentenceOfListPositionCountercheck].embedMethod,
                            messageWithRelatedSentences[str(currentMessagePosition)][
                                indexsentenceOfListPositionCountercheck].watermarkedSentencesOfCurrentMarker.embedMethod)

                        if scoreOfSentence > scoreOfCountercheckSentece:
                            # Der zu vergleichende Satz wird gelöscht
                            messageWithRelatedSentences[str(currentMessagePosition)].pop(
                                messageWithRelatedSentences[
                                    str(currentMessagePosition)].index(
                                    messageWithRelatedSentences[str(currentMessagePosition)][
                                        indexsentenceOfListPositionCountercheck]))
                            continue

                        elif scoreOfCountercheckSentece > scoreOfSentence:
                            # Der zu vergleichende Satz ersetzt den Anderen
                            messageWithRelatedSentences[str(currentMessagePosition)].pop(
                                messageWithRelatedSentences[
                                    str(currentMessagePosition)].index(
                                    messageWithRelatedSentences[str(currentMessagePosition)][
                                        indexSentenceOfListPosition]))
                            indexSentenceOfListPosition -= 1
                            break
                        else:
                            # Die beiden Sätze weisen den gleichen Rating auf
                            # Der Zufall entscheidet, welcher der beiden Sätze erhalten bleibt
                            if random.uniform(0, 1) == 0:
                                # Der zu vergleichende Satz wird gelöscht
                                messageWithRelatedSentences[str(currentMessagePosition)].pop(
                                    messageWithRelatedSentences[
                                        str(currentMessagePosition)].index(
                                        messageWithRelatedSentences[
                                            str(currentMessagePosition)][
                                            indexsentenceOfListPositionCountercheck]))
                                continue
                            else:
                                # Der zu vergleichende Satz ersetzt den Anderen
                                messageWithRelatedSentences[str(currentMessagePosition)].pop(
                                    messageWithRelatedSentences[
                                        str(currentMessagePosition)].index(
                                        messageWithRelatedSentences[
                                            str(currentMessagePosition)][
                                            indexSentenceOfListPosition]))
                                indexSentenceOfListPosition -= 1
                                break

                indexsentenceOfListPositionCountercheck += 1
            indexSentenceOfListPosition += 1

    # Ist ein Satz in einer anderen Liste ebenfalls enthalten, so muss der Satz aus der längeren Liste gelöscht werden
    # Sind die Listen gleich lang, ist die geeignetste Einbettungs-Methode entscheidend
    for currentMessagePosition in range(len(messageWithRelatedSentences)):
        # Iterierung über jeden Satz dieser Liste
        indexPossibleSentenceOfCurrentMessagePosition = 0
        while indexPossibleSentenceOfCurrentMessagePosition < len(
                messageWithRelatedSentences[str(currentMessagePosition)]):
            # Nur alle nachfolgenden Listen werden auf Übereinstimmungen überprüft, da die Überprüfung für alle
            # vorangegangenen Listen bereits erfolgt ist und darum keine korrespondierenden Sätze in diesen
            # enthalten sind
            currentMessagePositionToCheck = currentMessagePosition + 1
            while currentMessagePositionToCheck < len(messageWithRelatedSentences):
                # Iterierung über jeden Satz der aktuellen zu überprüfenden Liste
                indexPossibleSentenceOfCurrentMessagePositionToCheck = 0
                while indexPossibleSentenceOfCurrentMessagePositionToCheck < len(
                        messageWithRelatedSentences[str(currentMessagePositionToCheck)]):
                    # Überprüfung, ob die sentenceId beider aktuellen Sätze übereinstimmt
                    if messageWithRelatedSentences[str(currentMessagePosition)][
                        indexPossibleSentenceOfCurrentMessagePosition].sentenceId == \
                            messageWithRelatedSentences[str(currentMessagePositionToCheck)][
                                indexPossibleSentenceOfCurrentMessagePositionToCheck].sentenceId:
                        # Generierung der Ratings der beiden Sätze
                        possibleSentenceRating = calculateScoreOfMarkerAndWatermarkedSentence(
                            messageWithRelatedSentences[str(currentMessagePosition)][
                                indexPossibleSentenceOfCurrentMessagePosition].embedMethod,
                            messageWithRelatedSentences[str(currentMessagePosition)][
                                indexPossibleSentenceOfCurrentMessagePosition].watermarkedSentencesOfCurrentMarker.embedMethod)
                        possibleSentenceToCheckRating = calculateScoreOfMarkerAndWatermarkedSentence(
                            messageWithRelatedSentences[str(currentMessagePositionToCheck)][
                                indexPossibleSentenceOfCurrentMessagePositionToCheck].embedMethod,
                            messageWithRelatedSentences[str(currentMessagePositionToCheck)][
                                indexPossibleSentenceOfCurrentMessagePositionToCheck].watermarkedSentencesOfCurrentMarker.embedMethod)

                        possibleSentenceRating, possibleSentenceToCheckRating = adaptScoreToIncludeNumberOfPossibleOptions(
                            possibleSentenceRating, possibleSentenceToCheckRating,
                            len(messageWithRelatedSentences[str(currentMessagePosition)]),
                            len(messageWithRelatedSentences[str(currentMessagePositionToCheck)]))

                        # Der Satz mit dem schlechteren Ranking wird entfernt
                        if possibleSentenceRating > possibleSentenceToCheckRating:
                            # Der innere Satz wird gelöscht
                            messageWithRelatedSentences[str(currentMessagePositionToCheck)].pop(
                                messageWithRelatedSentences[
                                    str(currentMessagePositionToCheck)].index(
                                    messageWithRelatedSentences[str(currentMessagePositionToCheck)][
                                        indexPossibleSentenceOfCurrentMessagePositionToCheck]))
                            continue
                        elif possibleSentenceRating < possibleSentenceToCheckRating:
                            # Der äußere Satz wird gelöscht
                            messageWithRelatedSentences[str(currentMessagePosition)].pop(
                                messageWithRelatedSentences[
                                    str(currentMessagePosition)].index(
                                    messageWithRelatedSentences[str(currentMessagePosition)][
                                        indexPossibleSentenceOfCurrentMessagePosition]))
                            currentMessagePositionToCheck = len(messageWithRelatedSentences)
                            indexPossibleSentenceOfCurrentMessagePosition -= 1
                            break
                        else:
                            # Die beiden Sätze besitzen den gleichen Score, daher entscheidet der Zufall
                            if random.uniform(0, 1) == 0:
                                # Der zu vergleichende Satz wird gelöscht
                                messageWithRelatedSentences[str(currentMessagePositionToCheck)].pop(
                                    messageWithRelatedSentences[
                                        str(currentMessagePositionToCheck)].index(
                                        messageWithRelatedSentences[str(currentMessagePositionToCheck)][
                                            indexPossibleSentenceOfCurrentMessagePositionToCheck]))
                                continue
                            else:
                                # Der zu vergleichende Satz bleibt erhalten und der Andere wird gelöscht
                                messageWithRelatedSentences[str(currentMessagePosition)].pop(
                                    messageWithRelatedSentences[
                                        str(currentMessagePosition)].index(
                                        messageWithRelatedSentences[str(currentMessagePosition)][
                                            indexPossibleSentenceOfCurrentMessagePosition]))
                                currentMessagePositionToCheck = len(messageWithRelatedSentences)
                                indexPossibleSentenceOfCurrentMessagePosition -= 1
                                break

                    indexPossibleSentenceOfCurrentMessagePositionToCheck += 1
                currentMessagePositionToCheck += 1
            indexPossibleSentenceOfCurrentMessagePosition += 1

    # Marker-Sätze können nicht zugleich Sätze mit Watermark in einem anderen Satz-Pärchen sein
    # Aus diesem Grund werden diese Satzpaare gegenübergestellt und beste Pärchen bleibt erhalten
    for currentOuterMessagePosition in range(len(messageWithRelatedSentences)):
        # Iterierung über jeden Satz dieser Liste innerhalb der äußeren Schleife
        indexPossibleSentenceOfCurrentOuterMessagePosition = 0
        while indexPossibleSentenceOfCurrentOuterMessagePosition < len(
                messageWithRelatedSentences[str(currentOuterMessagePosition)]):
            outerSentenceRating = calculateScoreOfMarkerAndWatermarkedSentence(
                messageWithRelatedSentences[str(currentOuterMessagePosition)][
                    indexPossibleSentenceOfCurrentOuterMessagePosition].embedMethod,
                messageWithRelatedSentences[str(currentOuterMessagePosition)][
                    indexPossibleSentenceOfCurrentOuterMessagePosition].watermarkedSentencesOfCurrentMarker.embedMethod)

            # Iterierung über alle messageWithRelatedSentences-Objekte
            currentInnerMessagePosition = 0
            while currentInnerMessagePosition < len(messageWithRelatedSentences):
                # Iterierung über jeden Satz dieser Liste innerhalb der inneren Schleife
                indexPossibleSentenceOfCurrentInnerMessagePosition = 0
                while indexPossibleSentenceOfCurrentInnerMessagePosition < len(
                        messageWithRelatedSentences[str(currentInnerMessagePosition)]):

                    # Der äußere Satz soll ist den nachfolgenden Überprüfungen ausgenommen
                    if messageWithRelatedSentences[str(currentOuterMessagePosition)][
                        indexPossibleSentenceOfCurrentOuterMessagePosition].sentenceId != \
                            messageWithRelatedSentences[str(currentInnerMessagePosition)][
                                indexPossibleSentenceOfCurrentInnerMessagePosition].sentenceId:

                        # Überprüfung, ob der Satz mit Watermark des äußeren Satzes dem Markersatz des inneren
                        # Satzes entspricht
                        if messageWithRelatedSentences[str(currentOuterMessagePosition)][
                            indexPossibleSentenceOfCurrentOuterMessagePosition].watermarkedSentencesOfCurrentMarker.sentenceId == \
                                messageWithRelatedSentences[str(currentInnerMessagePosition)][
                                    indexPossibleSentenceOfCurrentInnerMessagePosition].sentenceId:

                            # Errechnung des Ratings des inneren Satzes
                            innerSentenceRating = calculateScoreOfMarkerAndWatermarkedSentence(
                                messageWithRelatedSentences[str(currentInnerMessagePosition)][
                                    indexPossibleSentenceOfCurrentInnerMessagePosition].embedMethod,
                                messageWithRelatedSentences[str(currentInnerMessagePosition)][
                                    indexPossibleSentenceOfCurrentInnerMessagePosition].watermarkedSentencesOfCurrentMarker.embedMethod)

                            temporaryRatingOfOuterSentence = outerSentenceRating
                            temporaryRatingOfOuterSentence, innerSentenceRating = adaptScoreToIncludeNumberOfPossibleOptions(
                                temporaryRatingOfOuterSentence, innerSentenceRating,
                                len(messageWithRelatedSentences[str(currentOuterMessagePosition)]),
                                len(messageWithRelatedSentences[str(currentInnerMessagePosition)]))

                            # Der Satz mit dem schlechteren Ranking wird entfernt
                            if temporaryRatingOfOuterSentence > innerSentenceRating:
                                # Der innere Satz wird gelöscht
                                messageWithRelatedSentences[str(currentInnerMessagePosition)].pop(
                                    messageWithRelatedSentences[str(currentInnerMessagePosition)].index(
                                        messageWithRelatedSentences[str(currentInnerMessagePosition)][
                                            indexPossibleSentenceOfCurrentInnerMessagePosition]))
                                continue
                            elif temporaryRatingOfOuterSentence < innerSentenceRating:
                                # Der äußere Satz wird gelöscht
                                messageWithRelatedSentences[str(currentOuterMessagePosition)].pop(
                                    messageWithRelatedSentences[str(currentOuterMessagePosition)].index(
                                        messageWithRelatedSentences[str(currentOuterMessagePosition)][
                                            indexPossibleSentenceOfCurrentOuterMessagePosition]))
                                currentInnerMessagePosition = len(messageWithRelatedSentences)
                                indexPossibleSentenceOfCurrentOuterMessagePosition -= 1
                                break
                            else:
                                # Beide Sätze besitzen den gleichen Score, darum entscheidet der Zufall
                                if random.uniform(0, 1) == 0:
                                    # Der innere Satz wird gelöscht
                                    messageWithRelatedSentences[str(currentInnerMessagePosition)].pop(
                                        messageWithRelatedSentences[str(currentInnerMessagePosition)].index(
                                            messageWithRelatedSentences[str(currentInnerMessagePosition)][
                                                indexPossibleSentenceOfCurrentInnerMessagePosition]))
                                    continue
                                else:
                                    # Der äußere Satz wird gelöscht
                                    messageWithRelatedSentences[str(currentOuterMessagePosition)].pop(
                                        messageWithRelatedSentences[str(currentOuterMessagePosition)].index(
                                            messageWithRelatedSentences[str(currentOuterMessagePosition)][
                                                indexPossibleSentenceOfCurrentOuterMessagePosition]))
                                    currentInnerMessagePosition = len(messageWithRelatedSentences)
                                    indexPossibleSentenceOfCurrentOuterMessagePosition -= 1
                                    break

                    indexPossibleSentenceOfCurrentInnerMessagePosition += 1
                currentInnerMessagePosition += 1
            indexPossibleSentenceOfCurrentOuterMessagePosition += 1

    # Prüfung, ob jedes Watermarkfragment eingebettet werden konnte
    for positionOfMessage in messageWithRelatedSentences:
        if not messageWithRelatedSentences[positionOfMessage]:
            # Die Nachricht kann nicht komplett eingebettet werden
            return None

    # Umwandlung des Dictionary "messageWithRelatedSentences" in ein Dictionary, in dem die sentenceId als Key fungiert
    watermarkedFragmentsOfText = dict()
    for positionOfMessage in range(len(messageWithRelatedSentences)):
        for sentenceOfPosition in range(len(messageWithRelatedSentences[str(positionOfMessage)])):
            watermarkedFragmentsOfText[
                messageWithRelatedSentences[str(positionOfMessage)][sentenceOfPosition].sentenceId] = \
            messageWithRelatedSentences[str(positionOfMessage)][sentenceOfPosition]

    # Soll die dynamische Einbettungsmethode verwendet werden, so müssen nun jene Sätze ohne Watermarkfragment bzw.
    # Marker ebenfalls zum Dictionary "watermarkedFragmentsOfText" hinzugefügt werden
    # Dabei wird der originale Satz herangezogen
    if not methodIsStatic:
        for sentenceId in possibleWatermarkedSentences:
            if sentenceId not in watermarkedFragmentsOfText:
                for sentenceWithoutWatermark in possibleWatermarkedSentences[sentenceId]:
                    if sentenceWithoutWatermark.embedMethod is None:
                        # Es handelt sich um den originalen Satz
                        watermarkedFragmentsOfText[sentenceId] = sentenceWithoutWatermark
                        break

    return watermarkedFragmentsOfText


def adaptScoreToIncludeNumberOfPossibleOptions(scoreOfSenteceA, scoreOfSentenceB, lengthOfListWithA, lengthOfListWithB):
    # Diese Funktion dient der Verbesserung des errechneten Scores für Listen mit weniger Möglichkeiten
    if lengthOfListWithA > lengthOfListWithB:
        # Überprüfung, ob in Liste B nur noch ein Element enhalten ist, um zu verhindern, dass dieser Satz gelöscht wird
        if lengthOfListWithB == 0:
            scoreOfSentenceB = 100
        else:
            scoreOfSentenceB += (lengthOfListWithA - lengthOfListWithB) * 4
    elif lengthOfListWithA < lengthOfListWithB:
        if lengthOfListWithA == 0:
            scoreOfSenteceA = 100
        else:
            scoreOfSenteceA += (lengthOfListWithB - lengthOfListWithA) * 4
    return scoreOfSenteceA, scoreOfSentenceB


def calculateScoreOfMarkerAndWatermarkedSentence(embedMethodOfMarker, embedMethodOfWatermark):
    # Das Rating eines Marker- und Watermarkingsatzpaares errechnet sich aus der Hälfte des Ratings beider Sätze
    return (getScoreOfSentence(embedMethodOfMarker) + getScoreOfSentence(embedMethodOfWatermark)) / 2


def getScoreOfSentence(usedEmbedMethod):
    if usedEmbedMethod is None:
        return 80
    elif usedEmbedMethod.classificationOfMethod == 1:
        return 10
    elif usedEmbedMethod.classificationOfMethod == 2:
        return 20
    elif usedEmbedMethod.classificationOfMethod == 3:
        return 30
    elif usedEmbedMethod.classificationOfMethod == 4:
        return 40
    elif usedEmbedMethod.classificationOfMethod == 5:
        return 50
    else:
        # Ungültige Klasse
        return 0


def createWatermarkedText(watermarkedFragmentsOfText, methodIsStatic):
    global possibleWatermarkedSentences

    currentSentenceId = 0
    if methodIsStatic:
        # Die statische Einbettungsmethode soll verwendet werden
        # Zusammenstellung des Textes mit enthaltenem Watermark
        while currentSentenceId < len(possibleWatermarkedSentences):
            # Überprüfung, ob ein Satz mit Watermarkfragment für die aktuelle sentenceId verfügbar ist
            if currentSentenceId in watermarkedFragmentsOfText:
                exportToWatermarkedDocument(watermarkedFragmentsOfText[currentSentenceId])
                currentSentenceId += 1
            else:
                # Es ist für diesen Satz kein Watermarkpärchen verfügbar
                # Überprüfung, ob ein Satz mit dieser sentenceId in "watermarkedFragmentsOfText" verfügbar ist
                if currentSentenceId in watermarkedFragmentsOfText:
                    # Überprüfung, ob der Wert des Satzes mit 0 beginnt
                    if watermarkedFragmentsOfText[currentSentenceId].valueOfSentenceStartsWithZero:
                        # Der Wert beginnt mit 0
                        exportToWatermarkedDocument(watermarkedFragmentsOfText[currentSentenceId])
                    else:
                        # Der Wert beginnt nicht mit 0
                        textCanNotBeWatermarked()
                else:
                    # Es ist kein Satz mit der gewünschten sentenceId in "watermarkedFragmentsOfText" enthalten
                    textCanNotBeWatermarked()
            currentSentenceId += 1
    else:
        # Die dynamische Einbettungsmethode soll verwendet werden
        # Zusammenstellung des Textes mit enthaltenem Watermark
        while currentSentenceId < len(watermarkedFragmentsOfText):
            exportToWatermarkedDocument(watermarkedFragmentsOfText[currentSentenceId])
            # Handelt es sich beim aktuellen Satz um ein Marker und Watermarksatz, so muss der counter zusätzlich
            # um 1 erhöht werden
            if watermarkedFragmentsOfText[currentSentenceId].watermarkedSentencesOfCurrentMarker is not None:
                currentSentenceId += 1
            currentSentenceId += 1


def textCanNotBeWatermarked():
    global pathToOutputFile
    print("\nDie Einbettung der gewünschten Nachricht in diesen Text ist nicht möglich!\n")

    # Löschung des Dokuments mit dem eingebetteten Watermark, sofern dieses bereits angelegt wurde
    if os.path.exists(pathToOutputFile):
        os.remove(pathToOutputFile)

    sys.exit(0)


def exportSentenceToTemporaryFile(sentence):
    global temporaryFileName
    global encodingOfDocument

    f = open(temporaryFileName, "a", encoding=encodingOfDocument)
    startPosition = f.tell()
    f.write(sentence)
    endPosition = f.tell()
    f.close()

    f = open(temporaryFileName, "r", encoding=encodingOfDocument)
    f.seek(startPosition)
    retrievedSentence = f.read(endPosition - startPosition)
    f.close()
    return startPosition, endPosition


def exportToWatermarkedDocument(sentence):
    global pathToOutputFile
    global temporaryFileName
    global encodingOfDocument

    # Fehlerkorrektur, falls nicht ein String, sondern eine Liste übergeben wurde
    if type(sentence) is list:
        return

    # Auslesen des Marker-Satzes oder eines Satzes ohne Watermark
    fTemporaryFile = open(temporaryFileName, "r", encoding=encodingOfDocument)
    fTemporaryFile.seek(sentence.startPosition)
    retrievedSentence = fTemporaryFile.read(sentence.endPosition - sentence.startPosition)
    fTemporaryFile.close()

    # Exportieren des Satzes in das finale Dokument
    f = open(pathToOutputFile, "a+", encoding=encodingOfDocument)
    # Überprüfung, ob das letzte Zeichen im finalen Dokument ein Abstand ist, sodass zwei Sätze nicht direkt
    # aneinander angehängt werden
    if f.tell() != 0:
        f.seek(f.tell() - 1, os.SEEK_SET)
        lastCharacter = f.read(1)
        if not lastCharacter.isspace():
            retrievedSentence = " " + retrievedSentence
    f.write(retrievedSentence)
    f.close()

    # Handelt es sich um einen Marker-Satz wird die Funktion nochmals mit dem markierten Satz aufgerufen
    if sentence.watermarkedSentencesOfCurrentMarker is not None:
        exportToWatermarkedDocument(sentence.watermarkedSentencesOfCurrentMarker)


def checkIfSentenceIsWithoutWatermark(doc, keyAsByteArray):
    # Zurücksetzen der Variable, um sicher zu stellen, dass keine alten Beziehungen aus dem vorhergehenden Satz übernommen werden
    global dependeciesOfSentence
    dependeciesOfSentence = ""

    # Speicherung der Abhängigkeiten des aktuellen Satzes
    findRootNodeForPreOrderTraversal(doc)

    # Generierung des Abhängigkeits-Hashes für den aktuellen Satz
    resultedBits = createHmacOfDependencyString(keyAsByteArray)

    # Überprüfung, ob das erste Bit dem Wert 0 entspricht
    if resultedBits[0] == '0':
        # Das erste Bit ist 0
        return True
    else:
        # Das erste Bit ist 1
        return False


def checkIfPositionCanBeRetrieved(doc, keyAsByteArray, messageCharacterObject):
    # Überprüfung, ob eine Position ausgelesen werden kann
    matchedPosition = getPositionNumberOfSentence(doc, keyAsByteArray)
    if matchedPosition is not None:
        # Prüfung, ob die Position der gewünschten Stelle entspricht
        if checkIfPositionMatches(messageCharacterObject.positionInMessage, matchedPosition):
            # Die Position des Zeichens ist eingebettet
            return matchedPosition
    return None


def checkIfPositionMatches(desiredPositions, matchedPosition):
    if matchedPosition in desiredPositions:
        # Die gewünschte Position stimmt überein
        return True
    else:
        return False


def getProcessedTextOfDocument(nlp, text):
    """
    Die Prozessierung reichert den Informationsgehalt von Sätzen deren Wörtern an.
    Dies betrifft unter anderem die Segmentierung des Textes in seine Wörter und Satzzeichen, sowie die Kennzeichnung
    der Satzglieder mittels statistischer Modelle.
    """
    return nlp(text)


if __name__ == '__main__':
    main()
