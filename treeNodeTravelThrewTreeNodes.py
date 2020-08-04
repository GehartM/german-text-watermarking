def TravelThrewTreeNodes(currentTreeNode, leftDirections, encodedSign):
    # Überprüfung, ob die letzte Stelle erreicht wurde. Sollte dies nicht der Fall sein so wird weiter durch den
    # Baum navigiert
    if not len(leftDirections) == 1:
        # Speicherung der nächsten Richtung
        nextDirection = leftDirections[0]

        # Löschen der aktuellen Richtung von den übrigen Richtungen
        leftDirections = leftDirections[1:]

        # Überprüfung, ob vom aktuellen TreeNode in Richtung 0 navigiert werden soll
        if nextDirection == '0':
            if not CheckIfChildrenTreeNodeAlreadyExists(currentTreeNode.zero):
                # Die gewünschte Richtung existiert noch nicht, daher wird ein neuer TreeNode für diese
                # Richtung erstellt
                currentTreeNode.AddTreeNode(True)

            TravelThrewTreeNodes(currentTreeNode.zero, leftDirections, encodedSign)
        elif nextDirection == '1':
            if not CheckIfChildrenTreeNodeAlreadyExists(currentTreeNode.one):
                # Die gewünschte Richtung existiert noch nicht, daher wird ein neuer TreeNode für diese Richtung
                # erstellt
                currentTreeNode.AddTreeNode(False)

            TravelThrewTreeNodes(currentTreeNode.one, leftDirections, encodedSign)

    else:
        # Es wurde die letzte Stelle erreicht. Damit kann das kodierte Zeichen an seine vorgesehene Stelle gespeichert
        # werden
        # Überprüfung, ob vom aktuellen TreeNode in Richtung 0 navigiert werden soll
        if leftDirections == '0':
            # Erstelle einen neuen TreeNode für diese Richtung und speichere als Wert das kodierte Zeichen
            currentTreeNode.AddTreeNode(True, encodedSign)
        elif leftDirections == '1':
            # Erstelle einen neuen TreeNode für diese Richtung und speichere als Wert das kodierte Zeichen
            currentTreeNode.AddTreeNode(False, encodedSign)


def CheckIfChildrenTreeNodeAlreadyExists(childrenTreeNode):
    # Existiert das abzufragende Kind-Objekt bereits, so wird True zurückgegeben
    if childrenTreeNode is not None:
        return True
    else:
        return False
