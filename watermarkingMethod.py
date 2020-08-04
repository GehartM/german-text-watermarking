from abc import ABC, abstractmethod


class WatermarkingMethod(ABC):
    def __init__(self, methodName, classificationOfMethod):
        self.name = methodName                                  # Hält den Namen der Methode
        self.classificationOfMethod = classificationOfMethod    # Speichert die Klassifizierung dieser Methode

    @abstractmethod
    def initializeMethod(self, nlp):
        pass

    @abstractmethod
    def process(self, docOfSentence, nlp, optionalObject=None):
        pass

    def getName(self):
        return self.name

    def getClassification(self):
        return self.classificationOfMethod
