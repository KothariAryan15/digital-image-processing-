
def arithmetic_encoding(text):
    frequency = {}
    for char in text:
        frequency[char] = frequency.get(char, 0) + 1

    total = len(text)
    low_range = 0.0
    ranges = {}

    for char, freq in sorted(frequency.items()):
        high_range = low_range + freq / total
        ranges[char] = (low_range, high_range)
        low_range = high_range

    low = 0.0
    high = 1.0

    for char in text:
        range_width = high - low

        char_low, char_high = ranges[char]

        high = low + range_width * char_high
        low = low + range_width * char_low

    encoded_value = (low + high) / 2
    return encoded_value, ranges

text = input("enter the text:")

encoded_value, ranges = arithmetic_encoding(text)

print("Original Text:", text)

print("\nCharacter Probability Ranges:")
for char, (low, high) in ranges.items():
    print(char, ":", low, "-", high)

print("\nArithmetic Encoded Value:", encoded_value)
