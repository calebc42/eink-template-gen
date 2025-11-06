"""
Simple noise generation for organic patterns
Pure Python implementation - no external dependencies
"""

import math


def simple_noise_2d(x, y, seed=0):
    """
    Generate smooth pseudo-random noise using hash-based interpolation.
    Returns a value between 0.0 and 1.0.

    Args:
        x: X coordinate (can be fractional)
        y: Y coordinate (can be fractional)
        seed: Random seed for reproducibility

    Returns:
        float: Noise value between 0.0 and 1.0
    """
    # Integer coordinates
    xi = int(math.floor(x))
    yi = int(math.floor(y))

    # Fractional coordinates
    xf = x - xi
    yf = y - yi

    # Smooth interpolation (smoothstep function)
    u = xf * xf * (3.0 - 2.0 * xf)
    v = yf * yf * (3.0 - 2.0 * yf)

    # Hash function for pseudo-random gradients
    def hash_2d(x, y):
        h = ((x * 374761393) + (y * 668265263) + seed) & 0x7FFFFFFF
        h = (h ^ (h >> 13)) * 1274126177
        return (h & 0x7FFFFFFF) / 2147483647.0

    # Get corner values
    aa = hash_2d(xi, yi)
    ab = hash_2d(xi, yi + 1)
    ba = hash_2d(xi + 1, yi)
    bb = hash_2d(xi + 1, yi + 1)

    # Bilinear interpolation
    x1 = aa * (1 - u) + ba * u
    x2 = ab * (1 - u) + bb * u

    return x1 * (1 - v) + x2 * v


def fractal_noise_2d(x, y, octaves=4, persistence=0.5, lacunarity=2.0, seed=0):
    """
    Generate fractal (multi-octave) noise for more natural-looking patterns.

    Args:
        x, y: Coordinates
        octaves: Number of noise layers to combine
        persistence: How much each octave contributes (amplitude multiplier)
        lacunarity: Frequency multiplier for each octave
        seed: Random seed

    Returns:
        float: Noise value between 0.0 and 1.0
    """
    total = 0.0
    frequency = 1.0
    amplitude = 1.0
    max_value = 0.0  # For normalization

    for _ in range(octaves):
        total += simple_noise_2d(x * frequency, y * frequency, seed) * amplitude
        max_value += amplitude
        amplitude *= persistence
        frequency *= lacunarity

    return total / max_value


def turbulence_2d(x, y, octaves=4, seed=0):
    """
    Generate turbulence (absolute value of noise) for marble-like patterns.

    Args:
        x, y: Coordinates
        octaves: Number of octaves
        seed: Random seed

    Returns:
        float: Turbulence value between 0.0 and 1.0
    """
    total = 0.0
    frequency = 1.0
    amplitude = 1.0
    max_value = 0.0

    for _ in range(octaves):
        noise_val = simple_noise_2d(x * frequency, y * frequency, seed)
        total += abs(noise_val - 0.5) * 2.0 * amplitude
        max_value += amplitude
        amplitude *= 0.5
        frequency *= 2.0

    return total / max_value
