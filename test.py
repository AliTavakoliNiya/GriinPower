import re


def extract_valves_compartments(s):
    result = []
    # Split string into parts inside and outside parentheses
    parts = re.split(r'(\(.*?\))', s)

    for part in parts:
        if part.startswith('(') and part.endswith(')'):
            # Inside parentheses - extract decimal numbers
            nums = re.findall(r'\d+\.\d+|\d+', part)
            result.extend(nums)
        else:
            # Outside parentheses - replace 'x' with '.' and remove non-digit/dot
            cleaned = part.replace('x', '.')
            cleaned = re.sub(r'[^\d\.]', '', cleaned)
            # split by dots
            nums = [p for p in cleaned.split('.') if p]
            result.extend(nums)
    return ','.join(result)

# Testing
inputs = [
    "in1: 6.9x16.(3.60m).201",
    "in2: 6.961x1.5.10",
    "in3: 6.96x2.5.110"
]
# Test
for s in inputs:
    print(extract_numbers_final(s))
