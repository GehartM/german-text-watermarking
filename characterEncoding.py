from treeNode import TreeNode
from collections import defaultdict
from treeNodeTravelThrewTreeNodes import TravelThrewTreeNodes


# In characterEncoding wird die Zugehörigkeit der Ecodierung zu ihrem Wert festgelegt.
# Dabei wurde den 10 häufigsten Buchstaben in der deutschen Sprache mehr Darstellungsmöglichkeiten zugewiesen.

characterEncoding = defaultdict(list, {
    'A': ['1000001', '1011111', '1101001'],
    'B': ['1000010'],
    'C': ['1000011'],
    'D': ['1000100'],
    'E': ['1000101', '1100000', '1101010'],
    'F': ['1000110'],
    'G': ['1000111'],
    'H': ['1001000', '1100001', '1101011'],
    'I': ['1001001', '1100010', '1101100'],
    'J': ['1001010'],
    'K': ['1001011'],
    'L': ['1001100', '1100011', '1101101'],
    'M': ['1001101'],
    'N': ['1001110', '1100100', '1101110'],
    'O': ['1001111'],
    'P': ['1010000'],
    'Q': ['1010001'],
    'R': ['1010010', '1100101', '1101111'],
    'S': ['1010011', '1100110', '1110000'],
    'T': ['1010100', '1100111', '1110001'],
    'U': ['1010101', '1101000', '1110010'],
    'V': ['1010110'],
    'W': ['1010111'],
    'X': ['1011000'],
    'Y': ['1011001'],
    'Z': ['1011010'],
    'ß': ['1011011'],
    'Ä': ['1011100'],
    'Ö': ['1011101'],
    'Ü': ['1011110'],
    '0': ['1110011'],
    '1': ['1110100'],
    '2': ['1110101'],
    '3': ['1110110'],
    '4': ['1110111'],
    '5': ['1111000'],
    '6': ['1111001'],
    '7': ['1111010'],
    '8': ['1111011'],
    '9': ['1111100']
})


# Erstellung des Ursprungsobjektes des Baums
rootTreeNode = TreeNode()


# Hinzufügen aller Äste des Baums, um am Ende dieser die zugehörigen Buchstaben bzw. Ziffern zu speichern.
for sign, possibleEncodings in characterEncoding.items():
    # Iteration über jede Kodierungsmöglichkeit
    for encoding in possibleEncodings:
        TravelThrewTreeNodes(rootTreeNode, encoding, sign)


def GetRootTreeNode():
    global rootTreeNode
    return rootTreeNode
