# Die PossibleSentence-Klasse wird verwendet, um Informationen zu Markersätzen oder Sätze ohne Watermark zu speichern


class PossibleSentence:
    def __init__(self, sentenceId, startPosition, endPosition, embedMethod, relatedMessagePosition=None,
                 valueOfSentenceStartsWithZero=False):
        self.sentenceId = sentenceId            # Stellt die Position des Satzes im originalen Dokument dar
        self.startPosition = startPosition      # Speichert den Beginn des Satzes innerhalb der temporären Datei
        self.endPosition = endPosition          # Speichert das Ende des Satzes innerhalb der temporären Datei
        self.embedMethod = embedMethod          # Speichert die verwendete Methode zum Einbetten des Watermarks.
                                                # Hält den Wert "None", sollte es sich um den unveränderten Satz handeln
        self.relatedMessagePosition = relatedMessagePosition        # Hält die Position des eingebetteten Zeichens,
                                                                    # sofern es sich um ein Watermarkfragment ist
        self.watermarkedSentencesOfCurrentMarker = None             # Ist das aktuelle PossibleSentence-Objekt ein
                                                                    # Marker, der zugehörige Satz mit eingebettetem
                                                                    # Watermark gespeichert
        self.valueOfSentenceStartsWithZero = valueOfSentenceStartsWithZero      # Ist True, wenn der Wert des Satzes
                                                                                # mit 0 beginnt, ansonsten ist der
                                                                                # Wert False
