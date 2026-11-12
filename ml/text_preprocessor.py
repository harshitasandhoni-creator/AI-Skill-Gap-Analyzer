
"""
Text preprocessing module for the semantic matching system.

Cleans resume text before skill extraction,
embedding generation, and job-role matching.
"""

import re

from ml.config import (
    LOWERCASE_TEXT,
    REMOVE_EXTRA_WHITESPACE
)


class TextPreprocessor:

    def __init__(self):
        """Initialize the text preprocessor."""
        pass

    # -----------------------------------------------
    # 1. Validate input
    # -----------------------------------------------

    def validate_text(self, text):
        """
        Check whether the input is valid text.

        Returns:
            bool: True if valid, otherwise False.
        """

        return isinstance(text, str) and bool(text.strip())

    # -----------------------------------------------
    # 2. Normalize text
    # -----------------------------------------------

    def normalize_text(self, text):
        """
        Convert text into a consistent format.
        """

        if not self.validate_text(text):
            return ""

        # Remove null characters
        text = text.replace("\x00", " ")

        # Convert to lowercase
        if LOWERCASE_TEXT:
            text = text.lower()

        # Normalize different line endings
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        return text

    # -----------------------------------------------
    # 3. Clean special characters
    # -----------------------------------------------

    def clean_special_characters(self, text):
        """
        Remove unnecessary characters while preserving
        useful technical symbols.
        """

        if not text:
            return ""

        # Preserve:
        # Letters, digits, whitespace, +, #, ., /, -, _
        text = re.sub(
            r"[^a-zA-Z0-9\s+#./_-]",
            " ",
            text
        )

        return text

    # -----------------------------------------------
    # 4. Remove extra whitespace
    # -----------------------------------------------

    def remove_extra_whitespace(self, text):
        """
        Remove repeated spaces and unnecessary line breaks.
        """

        if not text:
            return ""

        if REMOVE_EXTRA_WHITESPACE:

            # Replace multiple spaces/tabs with one space
            text = re.sub(r"[ \t]+", " ", text)

            # Limit multiple line breaks
            text = re.sub(r"\n+", "\n", text)

            # Remove spaces around line breaks
            text = re.sub(r" *\n *", "\n", text)

            # Remove leading and trailing spaces
            text = text.strip()

        return text

    # -----------------------------------------------
    # 5. Complete preprocessing pipeline
    # -----------------------------------------------

    def preprocess(self, text):
        """
        Execute all preprocessing operations.

        Returns:
            str: Cleaned resume text.
        """

        if not self.validate_text(text):
            return ""

        text = self.normalize_text(text)

        text = self.clean_special_characters(text)

        text = self.remove_extra_whitespace(text)

        return text


# -----------------------------------------------
# 6. Standalone testing
# -----------------------------------------------

if __name__ == "__main__":

    preprocessor = TextPreprocessor()

    sample_resume = """
    Name: Rahul Sharma

    Skills:
    Python, C++, SQL, Machine Learning,
    Scikit-Learn, TensorFlow, Node.js

    Projects:
    Built a Machine Learning model using Python.
    Worked with CI/CD pipelines and REST APIs.
    """

    cleaned_text = preprocessor.preprocess(sample_resume)

    print("ORIGINAL TEXT:")
    print(sample_resume)

    print("\nCLEANED TEXT:")
    print(cleaned_text)
