def GetSignToBinaryCode(binaryCode, rootTreeNode):
    currentTreeNode = rootTreeNode

    try:
        for bit in binaryCode:
            # Prüfung, ob das Bit dem Wert 0 oder 1 entspricht, um in die entsprechende Richtung zu navigieren
            if bit == '0':
                currentTreeNode = currentTreeNode.zero
            else:
                currentTreeNode = currentTreeNode.one
    except:
        # Es wurde versucht auf ein nicht existentes TreeNode-Objekt zuzugreifen
        # Aus diesem Grund gibt es zu dem aktuellen binären Code hinterlegtes Zeichen
        return None

    # Der Wert des aktullen TreeNode-Objektes wird zurückgegeben
    # Dieser entspricht entweder dem zugewiesenen Zeichen oder dem Wert None, sofern kein Zeichen für diesen binären
    # Code hinterlegt wurde
    if currentTreeNode is not None:
        return currentTreeNode.value
    else:
        return None
