from treeNode import TreeNode
from collections import defaultdict
from treeNodeTravelThrewTreeNodes import TravelThrewTreeNodes


# In positionEncoding wird die Zugehörigkeit der Ecodierung zu ihrem Wert festgelegt.
# Dieser Wert entspricht der Position des Buchstabens der nächsten Zeile.
positionEncoding = defaultdict(list, {
    '0': ['1000001', '1011111'],
    '1': ['1000010', '1100000'],
    '2': ['1000011', '1100001'],
    '3': ['1000100', '1100010'],
    '4': ['1000101', '1100011'],
    '5': ['1000110', '1100100'],
    '6': ['1000111', '1100101'],
    '7': ['1001000', '1100110'],
    '8': ['1001001', '1100111'],
    '9': ['1001010', '1101000'],
    '10': ['1001011', '1101001'],
    '11': ['1001100', '1101010'],
    '12': ['1001101', '1101011'],
    '13': ['1001110', '1101100'],
    '14': ['1001111', '1101101'],
    '15': ['1010000', '1101110'],
    '16': ['1010001', '1101111'],
    '17': ['1010010', '1110000'],
    '18': ['1010011', '1110001'],
    '19': ['1010100', '1110010'],
    '20': ['1010101', '1110011'],
    '21': ['1010110', '1110100'],
    '22': ['1010111', '1110101'],
    '23': ['1011000', '1110110'],
    '24': ['1011001', '1110111'],
    '25': ['1011010', '1111000'],
    '26': ['1011011', '1111001'],
    '27': ['1011100', '1111010'],
    '28': ['1011101', '1111011'],
    '29': ['1011110', '1111100']
})


# Erstellung des Ursprungsobjektes des Baums
rootTreeNode = TreeNode()


# Hinzufügen aller Äste des Baums, um am Ende dieser die Position zu speichern.
for position, possibleEncodings in positionEncoding.items():
    # Iteration über jede Kodierungsmöglichkeit
    for encoding in possibleEncodings:
        TravelThrewTreeNodes(rootTreeNode, encoding, position)


def GetRootTreeNode():
    global rootTreeNode
    return rootTreeNode
