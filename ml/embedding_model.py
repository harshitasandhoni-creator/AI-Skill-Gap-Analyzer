
"""
Embedding model module.

Loads a pretrained Sentence Transformer and converts
skills or text into numerical embeddings.
"""

import numpy as np
from sentence_transformers import SentenceTransformer

from ml.config import (
    MODEL_NAME,
    EMBEDDING_DIMENSION
)


class EmbeddingModel:

    def __init__(self):

        self.model_name = MODEL_NAME
        self.model = None

    # -----------------------------------------------
    # 1. Load pretrained model
    # -----------------------------------------------

    def load_model(self):

        """
        Load the pretrained Sentence Transformer.

        The model is loaded only once and reused.
        """

        if self.model is None:

            print("Loading embedding model...")

            self.model = SentenceTransformer(
                self.model_name
            )

            print("Embedding model loaded successfully.")

        return self.model

    # -----------------------------------------------
    # 2. Generate embedding for one text
    # -----------------------------------------------

    def generate_embedding(self, text):

        """
        Convert a single text into a numerical vector.

        Returns:
            numpy array of shape (384,)
        """

        if not isinstance(text, str) or not text.strip():

            raise ValueError(
                "Input text must be a non-empty string."
            )

        model = self.load_model()

        embedding = model.encode(
            text.strip(),
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embedding

    # -----------------------------------------------
    # 3. Generate embeddings for multiple texts
    # -----------------------------------------------

    def generate_embeddings(self, texts):

        """
        Convert multiple texts into numerical vectors.

        Returns:
            numpy array of shape (number_of_texts, 384)
        """

        if not isinstance(texts, (list, tuple)):

            raise TypeError(
                "Input must be a list or tuple of strings."
            )

        if not texts:

            return np.empty(
                (0, EMBEDDING_DIMENSION),
                dtype=np.float32
            )

        if not all(
            isinstance(text, str) and text.strip()
            for text in texts
        ):

            raise ValueError(
                "All inputs must be non-empty strings."
            )

        model = self.load_model()

        embeddings = model.encode(
            list(texts),
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )

        return embeddings

    # -----------------------------------------------
    # 4. Calculate cosine similarity
    # -----------------------------------------------

    def calculate_similarity(
        self,
        embedding1,
        embedding2
    ):

        """
        Calculate cosine similarity between two embeddings.

        Returns:
            float between -1 and 1
        """

        embedding1 = np.asarray(
            embedding1,
            dtype=np.float32
        )

        embedding2 = np.asarray(
            embedding2,
            dtype=np.float32
        )

        if embedding1.shape != embedding2.shape:

            raise ValueError(
                "Both embeddings must have the same dimensions."
            )

        if embedding1.ndim != 1:

            raise ValueError(
                "Expected two one-dimensional embeddings."
            )

        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)

        if norm1 == 0 or norm2 == 0:

            raise ValueError(
                "Cannot calculate similarity for a zero vector."
            )

        similarity = np.dot(
            embedding1,
            embedding2
        ) / (norm1 * norm2)

        return float(similarity)

    # -----------------------------------------------
    # 5. Calculate similarity between two texts
    # -----------------------------------------------

    def compare_texts(self, text1, text2):

        """
        Generate embeddings and compare two text inputs.
        """

        embedding1 = self.generate_embedding(text1)

        embedding2 = self.generate_embedding(text2)

        similarity = self.calculate_similarity(
            embedding1,
            embedding2
        )

        return similarity


# -----------------------------------------------
# 6. Standalone testing
# -----------------------------------------------

if __name__ == "__main__":

    embedding_model = EmbeddingModel()

    # Example skills
    skills = [
        "Machine Learning",
        "Artificial Intelligence",
        "Python Programming",
        "Database Management",
        "Data Analysis"
    ]

    print("\nGenerating embeddings...")

    embeddings = embedding_model.generate_embeddings(
        skills
    )

    print("\nEMBEDDING INFORMATION")

    print("Number of skills:", len(skills))

    print("Embedding shape:", embeddings.shape)

    print("First embedding dimensions:", embeddings[0][:10])

    # Compare two related skills
    similarity = embedding_model.compare_texts(
        "Machine Learning",
        "Artificial Intelligence"
    )

    print("\nSEMANTIC SIMILARITY")

    print(
        "Machine Learning vs Artificial Intelligence:",
        round(similarity, 4)
    )

    # Compare two different skills
    similarity2 = embedding_model.compare_texts(
        "Python Programming",
        "Database Management"
    )

    print(
        "Python Programming vs Database Management:",
        round(similarity2, 4)
    )
