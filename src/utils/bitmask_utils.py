# Fixed interests and bitmask utilities

INTERESTS = [
    "Running", "Cycling", "Yoga", "Walking", "Working out", "Trekking", "Aerobics",
    "Swimming", "Pets", "Foodie", "Vegan", "News", "Social Service", "Entrepreneurship",
    "Home Decor", "Investments", "Fashion", "Writing", "Cooking", "Singing", "Photography",
    "Instruments", "Painting", "DIY", "Dancing", "Acting"
]

# Map each interest to a unique bit (0 to 25)
INTEREST_MAP = {interest: 1 << i for i, interest in enumerate(INTERESTS)}

def compute_bitmask(interests: list[str]) -> int:
    """Compute the bitmask for a list of interest strings."""
    bitmask = 0
    for interest in interests:
        if interest in INTEREST_MAP:
            bitmask |= INTEREST_MAP[interest]
    return bitmask

def hamming_similarity(mask1: int, mask2: int) -> int:
    """Compute the Hamming similarity (number of common set bits) between two bitmasks."""
    return bin(mask1 & mask2).count("1")

def decode_bitmask(bitmask: int) -> list[str]:
    """Decode a bitmask into a list of interest strings."""
    return [interest for interest, value in INTEREST_MAP.items() if bitmask & value]
