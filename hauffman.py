import heapq
from collections import Counter

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(text):
    frequency = Counter(text)

    heap = [Node(char, freq) for char, freq in frequency.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)

        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right

        heapq.heappush(heap, merged)

    return heap[0]

def generate_codes(root, code="", codes=None):
    if codes is None:
        codes = {}

    if root is None:
        return codes

    if root.char is not None:
        codes[root.char] = code if code else "0"
        return codes

    generate_codes(root.left, code + "0", codes)
    generate_codes(root.right, code + "1", codes)

    return codes

def encode(text, codes):
    return ''.join(codes[char] for char in text)

def decode(encoded_text, root):
    result = []
    current = root

    for bit in encoded_text:
        if bit == '0':
            current = current.left
        else:
            current = current.right

        if current.char is not None:
            result.append(current.char)
            current = root

    return ''.join(result)

text = input("enter your text:")

root = build_huffman_tree(text)
codes = generate_codes(root)

encoded = encode(text, codes)
decoded = decode(encoded, root)

print("Original Text:", text)
print("\nCharacter Frequencies:")
for char, freq in Counter(text).items():
    print(repr(char), ":", freq)

print("\nHuffman Codes:")
for char, code in codes.items():
    print(repr(char), ":", code)

print("\nEncoded Text:", encoded)
print("Decoded Text:", decoded)

     
