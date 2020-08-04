class TreeNode:
    def __init__(self, value=None):
        self.zero = None        # Hält das nächste TreeNode-Objekt in Richtung 0
        self.one = None         # Hält das nächste TreeNode-Objekt in Richtung 1
        self.value = value      # Hält den Wert des aktuellen TreeNode-Objektes

    def AddTreeNode(self, newTreeNodeIsZero, value=None):
        if newTreeNodeIsZero:
            self.zero = TreeNode(value)
        else:
            self.one = TreeNode(value)
