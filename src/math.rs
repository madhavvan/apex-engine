// src/math.rs

// This function calculates how "close" two vectors are.
// Returns 1.0 if identical, 0.0 if unrelated.
pub fn cosine_similarity(a: &[f32], b: &[f32]) -> f32 {
    // 1. Basic check: vectors must be same length
    if a.len() != b.len() {
        return 0.0;
    }

    // 2. Calculate Dot Product (multiply matching numbers and sum them)
    let dot_product: f32 = a.iter()
                            .zip(b.iter())
                            .map(|(x, y)| x * y)
                            .sum();

    // 3. Calculate Magnitudes (length of the vector)
    let magnitude_a: f32 = a.iter().map(|x| x * x).sum::<f32>().sqrt();
    let magnitude_b: f32 = b.iter().map(|x| x * x).sum::<f32>().sqrt();

    // 4. Prevent division by zero
    if magnitude_a == 0.0 || magnitude_b == 0.0 {
        return 0.0;
    }

    // 5. The Formula
    dot_product / (magnitude_a * magnitude_b)
}