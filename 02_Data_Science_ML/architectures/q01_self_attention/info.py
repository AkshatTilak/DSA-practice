INFO = {
    'difficulty': 'Hard',
    'link': 'https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/',
    'description': 'Calculate scaled dot-product self-attention weights and final contextual projections.',
    'groups': ['Deep Learning', 'Transformers'],
    'starter_code': 'import numpy as np\n\ndef scaled_dot_product_attention(Q: np.ndarray, K: np.ndarray, V: np.ndarray) -> tuple[np.ndarray, np.ndarray]:\n    # Returns (output, attention_weights)\n    pass',
    'solutions': 'def scaled_dot_product_attention_optimal(Q, K, V):\n    dk = Q.shape[-1]\n    scores = np.dot(Q, K.T) / np.sqrt(dk)\n    # Stable Softmax\n    exp_scores = np.exp(scores - np.max(scores, axis=-1, keepdims=True))\n    attention_weights = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)\n    output = np.dot(attention_weights, V)\n    return output, attention_weights',
    'test_code': 'def test_attention():\n    pass',
    'readme_content': '# Self-Attention\nScaled Query Key interactions matrix weights.',
}
