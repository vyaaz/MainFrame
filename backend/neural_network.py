"""
Neural Network for Description Quality Scoring
Built from scratch - no PyTorch, TensorFlow, or ML frameworks.

This model rates component descriptions on a scale of 0-1:
- Low score (0-0.4): Needs more detail
- Medium score (0.4-0.7): Acceptable but could be improved
- High score (0.7-1.0): Good, detailed description

Architecture:
- Input: Bag-of-words text representation
- Hidden Layer 1: 64 neurons, ReLU activation
- Hidden Layer 2: 32 neurons, ReLU activation
- Output: 1 neuron, Sigmoid activation (quality score)
"""

import numpy as np
import json
import os

# ============================================================
# ACTIVATION FUNCTIONS (implemented from scratch)
# ============================================================

def relu(x):
    """ReLU activation: max(0, x)"""
    return np.maximum(0, x)

def relu_derivative(x):
    """Derivative of ReLU for backpropagation"""
    return (x > 0).astype(float)

def sigmoid(x):
    """Sigmoid activation: 1 / (1 + e^-x)"""
    # Clip to prevent overflow
    x = np.clip(x, -500, 500)
    return 1 / (1 + np.exp(-x))

def sigmoid_derivative(x):
    """Derivative of sigmoid for backpropagation"""
    s = sigmoid(x)
    return s * (1 - s)


# ============================================================
# TEXT PREPROCESSING (simple tokenizer from scratch)
# ============================================================

class SimpleTokenizer:
    """
    A simple bag-of-words tokenizer built from scratch.
    Converts text to fixed-size numerical vectors.
    """

    def __init__(self, vocab_size=500):
        self.vocab_size = vocab_size
        self.word_to_idx = {}
        self.idx_to_word = {}
        self.word_counts = {}

    def _clean_text(self, text):
        """Basic text cleaning"""
        text = text.lower()
        # Keep only alphanumeric and spaces
        cleaned = ""
        for char in text:
            if char.isalnum() or char.isspace():
                cleaned += char
            else:
                cleaned += " "
        return cleaned.split()

    def fit(self, texts):
        """Build vocabulary from training texts"""
        # Count word frequencies
        for text in texts:
            words = self._clean_text(text)
            for word in words:
                self.word_counts[word] = self.word_counts.get(word, 0) + 1

        # Sort by frequency and take top vocab_size
        sorted_words = sorted(self.word_counts.items(), key=lambda x: x[1], reverse=True)
        for idx, (word, _) in enumerate(sorted_words[:self.vocab_size]):
            self.word_to_idx[word] = idx
            self.idx_to_word[idx] = word

    def transform(self, text):
        """Convert text to bag-of-words vector"""
        vector = np.zeros(self.vocab_size)
        words = self._clean_text(text)

        for word in words:
            if word in self.word_to_idx:
                vector[self.word_to_idx[word]] += 1

        # Normalize
        if np.sum(vector) > 0:
            vector = vector / np.sum(vector)

        # Add text features
        features = self._extract_features(text)
        return np.concatenate([vector, features])

    def _extract_features(self, text):
        """Extract additional features from text"""
        words = self._clean_text(text)

        features = [
            len(text) / 200.0,  # Normalized length (longer = more detail)
            len(words) / 30.0,  # Word count normalized
            len(set(words)) / max(len(words), 1),  # Vocabulary diversity
            sum(1 for w in words if len(w) > 6) / max(len(words), 1),  # Complex words ratio
            1.0 if any(w in words for w in ['validate', 'check', 'verify', 'process', 'handle']) else 0.0,  # Action words
            1.0 if any(w in words for w in ['user', 'customer', 'client', 'admin']) else 0.0,  # User-focused
            1.0 if any(w in words for w in ['database', 'store', 'save', 'retrieve', 'query']) else 0.0,  # Data words
            1.0 if any(w in words for w in ['display', 'show', 'render', 'output', 'present']) else 0.0,  # Output words
        ]
        return np.array(features)

    @property
    def input_size(self):
        return self.vocab_size + 8  # vocab + 8 features


# ============================================================
# NEURAL NETWORK (built from scratch)
# ============================================================

class DescriptionQualityNetwork:
    """
    A feedforward neural network for scoring description quality.
    Implements forward pass, backpropagation, and gradient descent from scratch.
    """

    def __init__(self, input_size, hidden1_size=64, hidden2_size=32):
        self.input_size = input_size
        self.hidden1_size = hidden1_size
        self.hidden2_size = hidden2_size

        # Initialize weights using Xavier initialization
        self.W1 = np.random.randn(input_size, hidden1_size) * np.sqrt(2.0 / input_size)
        self.b1 = np.zeros((1, hidden1_size))

        self.W2 = np.random.randn(hidden1_size, hidden2_size) * np.sqrt(2.0 / hidden1_size)
        self.b2 = np.zeros((1, hidden2_size))

        self.W3 = np.random.randn(hidden2_size, 1) * np.sqrt(2.0 / hidden2_size)
        self.b3 = np.zeros((1, 1))

        # For storing intermediate values during forward pass (needed for backprop)
        self.cache = {}

    def forward(self, X):
        """
        Forward pass through the network.
        X: input features (batch_size, input_size)
        Returns: quality score (batch_size, 1)
        """
        # Layer 1
        self.cache['Z1'] = np.dot(X, self.W1) + self.b1
        self.cache['A1'] = relu(self.cache['Z1'])

        # Layer 2
        self.cache['Z2'] = np.dot(self.cache['A1'], self.W2) + self.b2
        self.cache['A2'] = relu(self.cache['Z2'])

        # Output layer
        self.cache['Z3'] = np.dot(self.cache['A2'], self.W3) + self.b3
        self.cache['A3'] = sigmoid(self.cache['Z3'])

        return self.cache['A3']

    def backward(self, X, y, learning_rate=0.01):
        """
        Backpropagation to compute gradients and update weights.
        X: input features
        y: true labels (quality scores)
        """
        m = X.shape[0]  # batch size

        # Output layer gradients
        dZ3 = self.cache['A3'] - y  # derivative of binary cross-entropy + sigmoid
        dW3 = (1/m) * np.dot(self.cache['A2'].T, dZ3)
        db3 = (1/m) * np.sum(dZ3, axis=0, keepdims=True)

        # Layer 2 gradients
        dA2 = np.dot(dZ3, self.W3.T)
        dZ2 = dA2 * relu_derivative(self.cache['Z2'])
        dW2 = (1/m) * np.dot(self.cache['A1'].T, dZ2)
        db2 = (1/m) * np.sum(dZ2, axis=0, keepdims=True)

        # Layer 1 gradients
        dA1 = np.dot(dZ2, self.W2.T)
        dZ1 = dA1 * relu_derivative(self.cache['Z1'])
        dW1 = (1/m) * np.dot(X.T, dZ1)
        db1 = (1/m) * np.sum(dZ1, axis=0, keepdims=True)

        # Update weights using gradient descent
        self.W3 -= learning_rate * dW3
        self.b3 -= learning_rate * db3
        self.W2 -= learning_rate * dW2
        self.b2 -= learning_rate * db2
        self.W1 -= learning_rate * dW1
        self.b1 -= learning_rate * db1

    def compute_loss(self, y_pred, y_true):
        """Binary cross-entropy loss"""
        epsilon = 1e-15  # prevent log(0)
        y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
        loss = -np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))
        return loss

    def train(self, X, y, epochs=1000, learning_rate=0.01, verbose=True):
        """Train the network"""
        losses = []

        for epoch in range(epochs):
            # Forward pass
            y_pred = self.forward(X)

            # Compute loss
            loss = self.compute_loss(y_pred, y)
            losses.append(loss)

            # Backward pass
            self.backward(X, y, learning_rate)

            if verbose and epoch % 100 == 0:
                print(f"Epoch {epoch}, Loss: {loss:.4f}")

        return losses

    def predict(self, X):
        """Predict quality score for input"""
        return self.forward(X)

    def save(self, filepath):
        """Save model weights to file"""
        np.savez(filepath,
                 W1=self.W1, b1=self.b1,
                 W2=self.W2, b2=self.b2,
                 W3=self.W3, b3=self.b3)

    def load(self, filepath):
        """Load model weights from file"""
        data = np.load(filepath)
        self.W1 = data['W1']
        self.b1 = data['b1']
        self.W2 = data['W2']
        self.b2 = data['b2']
        self.W3 = data['W3']
        self.b3 = data['b3']


# ============================================================
# TRAINING DATA
# ============================================================

# Training examples: (description, quality_score)
# Score: 0.0-0.3 = poor, 0.4-0.6 = okay, 0.7-1.0 = good

TRAINING_DATA = [
    # Poor descriptions (low scores)
    ("input", 0.1),
    ("form", 0.1),
    ("data", 0.1),
    ("output", 0.1),
    ("logic", 0.1),
    ("user", 0.15),
    ("login", 0.15),
    ("button", 0.15),
    ("api", 0.15),
    ("db", 0.1),
    ("display", 0.15),
    ("process", 0.15),
    ("validate", 0.2),
    ("check data", 0.2),
    ("get user", 0.2),
    ("show results", 0.25),
    ("save data", 0.25),
    ("user form", 0.25),
    ("login form", 0.3),
    ("api call", 0.3),

    # Medium descriptions (medium scores)
    ("user login form", 0.4),
    ("validate user input", 0.45),
    ("save to database", 0.45),
    ("display results to user", 0.5),
    ("fetch data from api", 0.5),
    ("check if email is valid", 0.55),
    ("store user information", 0.5),
    ("show list of products", 0.55),
    ("process payment request", 0.55),
    ("authenticate user credentials", 0.6),
    ("retrieve customer orders", 0.55),
    ("render dashboard view", 0.5),
    ("validate form fields", 0.5),
    ("query product catalog", 0.55),

    # Good descriptions (high scores)
    ("user submits email and password through login form", 0.75),
    ("validate email format and check password strength requirements", 0.8),
    ("store user profile data in PostgreSQL with encrypted passwords", 0.85),
    ("display paginated list of orders with filtering and sorting options", 0.85),
    ("fetch real-time inventory data from warehouse management API", 0.8),
    ("process credit card payment through Stripe API with error handling", 0.9),
    ("authenticate user using JWT tokens and refresh token rotation", 0.9),
    ("render interactive dashboard showing sales metrics and trends", 0.85),
    ("validate shipping address against postal service API", 0.8),
    ("query customer purchase history with date range filtering", 0.8),
    ("user enters shipping details including address validation feedback", 0.85),
    ("calculate order total with tax, discounts, and shipping costs", 0.85),
    ("display product recommendations based on browsing history", 0.8),
    ("store session data in Redis cache with automatic expiration", 0.85),
    ("process batch import of product catalog from CSV file", 0.8),
    ("validate and sanitize user input to prevent XSS attacks", 0.9),
    ("render confirmation page with order summary and tracking info", 0.85),
    ("fetch and aggregate data from multiple microservices", 0.85),
    ("handle file upload with progress indicator and validation", 0.85),
    ("display real-time notifications using WebSocket connection", 0.9),
]


# ============================================================
# MAIN MODEL CLASS
# ============================================================

class DescriptionScorer:
    """
    Main class for scoring component descriptions.
    Combines tokenizer and neural network.
    """

    def __init__(self):
        self.tokenizer = SimpleTokenizer(vocab_size=200)
        self.model = None
        self.is_trained = False

    def train(self, epochs=2000, learning_rate=0.05):
        """Train the model on the built-in dataset"""
        print("Training Description Quality Model...")
        print("=" * 50)

        # Prepare training data
        texts = [item[0] for item in TRAINING_DATA]
        scores = np.array([[item[1]] for item in TRAINING_DATA])

        # Fit tokenizer
        self.tokenizer.fit(texts)

        # Transform texts to features
        X = np.array([self.tokenizer.transform(text) for text in texts])

        # Initialize model
        self.model = DescriptionQualityNetwork(
            input_size=self.tokenizer.input_size,
            hidden1_size=64,
            hidden2_size=32
        )

        # Train
        losses = self.model.train(X, scores, epochs=epochs, learning_rate=learning_rate)

        self.is_trained = True
        print("=" * 50)
        print(f"Training complete! Final loss: {losses[-1]:.4f}")

        return losses

    def score(self, description):
        """
        Score a single description.
        Returns: (score, feedback)
        """
        if not self.is_trained:
            self.train()

        # Transform and predict
        X = self.tokenizer.transform(description).reshape(1, -1)
        score = float(self.model.predict(X)[0, 0])

        # Generate feedback
        if score < 0.35:
            feedback = "Needs much more detail. Describe what data is involved and what happens."
        elif score < 0.5:
            feedback = "Too brief. Add specifics about the action, data, or user interaction."
        elif score < 0.65:
            feedback = "Okay, but could be more specific. Consider adding technical details."
        elif score < 0.8:
            feedback = "Good description with clear intent."
        else:
            feedback = "Excellent! Detailed and specific description."

        return {
            "score": round(score, 2),
            "percentage": round(score * 100),
            "feedback": feedback,
            "quality": "poor" if score < 0.35 else "needs_work" if score < 0.5 else "okay" if score < 0.65 else "good" if score < 0.8 else "excellent"
        }

    def score_batch(self, descriptions):
        """Score multiple descriptions"""
        return [self.score(desc) for desc in descriptions]

    def save(self, directory="model_weights"):
        """Save model to disk"""
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Save weights
        self.model.save(f"{directory}/weights.npz")

        # Save tokenizer vocab
        with open(f"{directory}/tokenizer.json", "w") as f:
            json.dump({
                "word_to_idx": self.tokenizer.word_to_idx,
                "vocab_size": self.tokenizer.vocab_size
            }, f)

        print(f"Model saved to {directory}/")

    def load(self, directory="model_weights"):
        """Load model from disk"""
        # Load tokenizer
        with open(f"{directory}/tokenizer.json", "r") as f:
            data = json.load(f)
            self.tokenizer.word_to_idx = data["word_to_idx"]
            self.tokenizer.idx_to_word = {v: k for k, v in self.tokenizer.word_to_idx.items()}
            self.tokenizer.vocab_size = data["vocab_size"]

        # Initialize and load model
        self.model = DescriptionQualityNetwork(
            input_size=self.tokenizer.input_size,
            hidden1_size=64,
            hidden2_size=32
        )
        self.model.load(f"{directory}/weights.npz")
        self.is_trained = True

        print(f"Model loaded from {directory}/")


# ============================================================
# SINGLETON INSTANCE
# ============================================================

_scorer_instance = None

def get_scorer():
    """Get or create the global scorer instance"""
    global _scorer_instance
    if _scorer_instance is None:
        _scorer_instance = DescriptionScorer()
        _scorer_instance.train(epochs=2000, learning_rate=0.05)
    return _scorer_instance


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("DESCRIPTION QUALITY NEURAL NETWORK")
    print("Built from scratch - no ML frameworks!")
    print("=" * 60 + "\n")

    scorer = DescriptionScorer()
    scorer.train(epochs=2000, learning_rate=0.05)

    print("\n" + "=" * 60)
    print("TESTING THE MODEL")
    print("=" * 60 + "\n")

    test_descriptions = [
        "login",
        "user form",
        "validate input data",
        "user submits login credentials",
        "user enters email and password through secure login form with validation",
        "fetch and display paginated product catalog with filtering options",
    ]

    for desc in test_descriptions:
        result = scorer.score(desc)
        print(f"Description: \"{desc}\"")
        print(f"  Score: {result['percentage']}% ({result['quality']})")
        print(f"  Feedback: {result['feedback']}")
        print()
