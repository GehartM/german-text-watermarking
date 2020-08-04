from spacy.matcher import PhraseMatcher  # Import the PhraseMatcher Class
from watermarkingMethod import WatermarkingMethod


class Abbreviations(WatermarkingMethod):
    abbreviationObject = None
    writtenOutAbbreviationObject = None

    # Dictionary mit den möglichen Abkürzungen
    possibleAbbreviations = dict({
        "a.a.O.": "am angegebenen Ort",
        "Abb.": "Abbildung",
        "Abh.": "Abhandlung",
        "Abk.": "Abkürzung",
        "allg.": "allgemein",
        "bes.": "besonders",
        "bzw.": "beziehungsweise",
        "eigtl.": "eigentlich",
        "geb.": "geboren",
        "gegr.": "gegründet",
        "Ggs.": "Gegensatz",
        "jmd.": "jemand",
        "jmdm.": "jemandem",
        "jmdn.": "jemanden",
        "jmds.": "jemandes",
        "scherzh.": "scherzhaft",
        "u.": "und",
        "übertr.": "übertragen",
        "ugs.": "umgangssprachlich",
        "urspr.": "ursprünglich",
        "usw.": "und so weiter",
        "zzt.": "zurzeit",
        "Mz.": "Mehrzahl",
        "Lit.": "Literatur",
        "afrik.": "afrikanisch",
        "amerik.": "amerikanisch",
        "argent.": "argentinisch",
        "bayr.": "bayrisch",
        "chin.": "chinesisch",
        "dt.": "deutsch",
        "europ.": "europäisch",
        "frz.": "beziehungsweise",
        "jap.": "japanisch",
        "ndrl.": "niederländisch",
        "norw.": "norwegisch",
        "österr.": "österreichisch",
        "Österr.": "Österreich",
        "portug.": "portugiesisch",
        "schweiz.": "schweizerisch",
        "skand.": "skandinavisch",
        "tschech.": "tschechisch",
        "USA": "Vereinigte Staaten von Amerika",
        "Jh.": "Jahrhundert",
        "kath.": "katholisch",
        "lat.": "lateinisch",
        "luth.": "lutherisch",
        "Myth.": "Mythologie",
        "n. Chr.": "nach Christus",
        "relig.": "religiös",
        "Relig.": "Religion",
        "v. Chr.": "vor Christus",
        "Anat.": "Anatomie",
        "Archit.": "Architektur",
        "Astron.": "Astronomie",
        "Biol.": "Biologie",
        "Chem.": "Chemie",
        "Geol.": "Geologie",
        "Math.": "Mathematik",
        "Med.": "Medizin",
        "Phys.": "Physik",
        "Psych.": "Psychologie",
        "Soziol.": "Soziologie",
        "Wiss.": "Wissenschaft",
        "Zool.": "Zoologie",
        "Bankw.": "Bankwesen",
        "Bgb.": "Bergbau",
        "Elektr.": "Elektrotechnik",
        "Forstw.": "Forstwesen",
        "Landw.": "Landwirtschaft",
        "Rechtsw.": "Rechtswesen",
        "Tech.": "Technik",
        "Wirtsch.": "Wirtschaft",
        "Dr.": "Doktor",
        "a.D.": "außer Dienst",
        "Abk.-Verz.": "Abkürzungsverzeichnis",
        "MHz": "Megahertz",
        "lfd. J.": "laufenden Jahres",
        "d.M.": "dieses Monats",
        "Jgg.": "Jahrgänge",
        "a.E.": "am Ende",
        "Abs.": "Absatz",
        "Abschn.": "Abschnitt",
        "Alt.": "Alternative",
        "Anl.": "Anlage",
        "Anm.": "Anmerkung",
        "Art.": "Artikel",
        "Aufl.": "Auflage",
        "Beschl. v.": "Beschluss vom",
        "Bsp.": "Beispiel",
        "bspw.": "beispielsweise",
        "bzgl.": "bezüglich",
        "ca.": "circa",
        "dgl.": "dergleichen",
        "etc.": "et cetera",
        "evtl.": "eventuell",
        "gem.": "gemäß",
        "ggf.": "gegebenenfalls",
        "grds.": "grundsätzlich",
        "i.A.": "im Auftrag",
        "i.d.F.": "in der Fassung",
        "i.d.R.": "in der Regel",
        "i.E.": "im Ergebnis",
        "i.R.v.": "im Rahmen von",
        "i.Ü.": "im Übrigen",
        "i.V.": "in Vertretung",
        "inkl.": "inklusive",
        "insb.": "insbesondere",
        "m.E.": "meines Erachtens",
        "m.w.N.": "mit weiteren Nachweisen",
        "max.": "maximal",
        "MwSt.": "Mehrwertsteuer",
        "n.F.": "neue Fassung",
        "Nr.": "Nummer",
        "o.a.": "oben angegeben",
        "o.g.": "oben genannt",
        "p.a.": "pro anno",
        "Pos.": "Position",
        "rd.": "rund",
        "S.": "Seite",
        "s.a.": "siehe auch",
        "s.o.": "siehe oben",
        "s.u.": "siehe unten",
        "sog.": "sogenannt",
        "Tab.": "Tabelle",
        "Tel.": "Telefon",
        "Tsd.": "Tausend",
        "u.a.": "unter anderem",
        "u.Ä.": "und Ähnliches",
        "u.E.": "unseres Erachtens",
        "u.U.": "unter Umständen",
        "Urt. v.": "Urteil vom",
        "u.v.m.": "und vieles mehr",
        "v.a.": "vor allem",
        "vgl.": "vergleiche",
        "Vorb.": "Vorbemerkung",
        "vs.": "versus",
        "z.B.": "zum Beispiel",
        "z.T.": "zum Teil",
        "zit.": "zitiert",
        "zzgl.": "zuzüglich"
    })

    def __init__(self):
        super().__init__("Abkürzungen", 4)

    def initializeMethod(self, nlp):
        # Initialisierung eines neuen Objektes der Matchter-Klasse
        abbreviationMatcher = PhraseMatcher(nlp.vocab)
        writtenOutAbbreviationMatcher = PhraseMatcher(nlp.vocab)

        # Definierung der Abkürzung
        abbreviationPattern = [
            nlp(text) for text in self.possibleAbbreviations.keys()
        ]
        writtenOutAbbreviationPattern = [
            nlp(text) for text in self.possibleAbbreviations.values()
        ]

        # Hinzufügen der Muster zu dem Matcher-Objekt
        abbreviationMatcher.add("ABBREVIATION", None, *abbreviationPattern)
        writtenOutAbbreviationMatcher.add("WRITTENOUTABBREVIATION", None, *writtenOutAbbreviationPattern)
        self.abbreviationObject = abbreviationMatcher
        self.writtenOutAbbreviationObject = writtenOutAbbreviationMatcher


    def process(self, docOfSentence, nlp, optionalObject=None):
        allAbbreviationMatches = self.abbreviationObject(docOfSentence)
        allWrittenOutAbbreviationMatches = self.writtenOutAbbreviationObject(docOfSentence)
        possibleSentences = list()

        # Iteration über alle Übereinstimmungen
        for match_id, start, end in allAbbreviationMatches:
            # Überprüfung, ob sich vor und nach dem Match ein Leerzeichen befindet, um ausschließen zu können, dass es ein Match innerhalb eines Wortes ist
            if not self.checkIfMatchIsIndependent(docOfSentence, start, end):
                continue
            possibleSentences.append(self.changeSentence(docOfSentence, start, end, True))

        # Iteration über alle Übereinstimmungen
        for match_id, start, end in allWrittenOutAbbreviationMatches:
            # Überprüfung, ob sich vor und nach dem Match ein Leerzeichen befindet, um ausschließen zu können, dass es ein Match innerhalb eines Wortes ist
            if not self.checkIfMatchIsIndependent(docOfSentence, start, end):
                continue
            possibleSentences.append(self.changeSentence(docOfSentence, start, end, False))

        # Rückgabe aller Änderungen
        if not possibleSentences:
            return None
        else:
            return possibleSentences


    def checkIfMatchIsIndependent(self, docOfSentence, start, end):
        # Überprüfung, ob sich vor und nach dem Match ein Leerzeichen befindet, um ausschließen zu können, dass es ein Match innerhalb eines Wortes ist
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

            try:
                # Überprüfung, ob die Übereinstimmung nicht am Satzende steht
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

    def changeSentence(self, docOfSentence, start, end, isAbbreviation):
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
        changeMatchWith = ""
        if isAbbreviation:
            # Überprüfung, ob das Wort im Dictionary existiert
            if matchedWord in self.possibleAbbreviations:
                changeMatchWith = self.possibleAbbreviations[matchedWord]
            else:
                return None
        else:
            # Überprüfung, ob das Wort im Dictionary existiert
            if matchedWord in self.possibleAbbreviations.values():
                changeMatchWith = list(self.possibleAbbreviations.keys())[list(self.possibleAbbreviations.values()).index(matchedWord)]
            else:
                return None

        # Überprüfung, ob nach der Übereinstimmung ein Satzzeichen steht
        # In diesem Fall darf kein zusätzlicher Abstand nach der Übereinstimmung eingefügt werden
        if docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != "." and \
                docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != "," \
                and docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != ";" \
                and docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != "?" \
                and docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != "!":
            changeMatchWith += " "

        # Überprüfung, ob die Übereinstimmung am Anfang des Satzes steht
        if docOfSentence[start].idx == 0:
            # Der erste Buchstabe muss groß geschrieben werden
            changeMatchWith = changeMatchWith[0].capitalize() + changeMatchWith[1:len(changeMatchWith)]

        # Überprüfung, ob die Übereinstimmung am Ende des Satzes steht
        if (len(docOfSentence) - 1) == docOfSentence[end].idx:
            # Die Übereinstimmung befindet sich am Ende des Satzes
            if docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != "." and \
            docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != "," and \
            docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != ";" and \
            docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != "?" and \
            docOfSentence.text[docOfSentence[start].idx + len(docOfSentence[start:end].text)] != "!":
                changeMatchWith = changeMatchWith[0:len(changeMatchWith) - 1] + "."

        # Einfügen der Abänderung in den Satz
        changedSentence = changedSentence[:docOfSentence[start].idx] + changeMatchWith + changedSentence[
                                                                                         docOfSentence[end].idx:]
        return changedSentence
