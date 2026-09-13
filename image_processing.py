"""
image_processing.py

Image preprocessing module for MediLens.AI.

Creates multiple image variants for EasyOCR:
- Original
- Contrast enhanced
- Sharpened
- Adaptive threshold
"""

import os

import cv2
import numpy as np


# ---------------------------------------------------------
# IMAGE PREPROCESSOR
# ---------------------------------------------------------

class ImagePreprocessor:

    def __init__(
        self,
        target_width=1000
    ):

        self.target_width = (
            target_width
        )

    def preprocess(
        self,
        image_path
    ):

        # -------------------------------------------------
        # CHECK FILE
        # -------------------------------------------------

        if not os.path.exists(
            image_path
        ):

            raise FileNotFoundError(
                f"Image file not found: "
                f"{image_path}"
            )

        # -------------------------------------------------
        # READ IMAGE
        # -------------------------------------------------

        image = cv2.imread(
            image_path
        )

        if image is None:

            raise ValueError(
                f"Unable to read image: "
                f"{image_path}"
            )

        # -------------------------------------------------
        # RESIZE
        # -------------------------------------------------

        h, w = image.shape[:2]

        if w < self.target_width:

            scale = (
                self.target_width
                /
                float(w)
            )

            new_h = int(
                h * scale
            )

            image = cv2.resize(

                image,

                (
                    self.target_width,
                    new_h
                ),

                interpolation=
                    cv2.INTER_CUBIC
            )

        # -------------------------------------------------
        # GRAYSCALE
        # -------------------------------------------------

        gray = cv2.cvtColor(

            image,

            cv2.COLOR_BGR2GRAY
        )

        # -------------------------------------------------
        # CLAHE
        # -------------------------------------------------

        clahe = cv2.createCLAHE(

            clipLimit=2.0,

            tileGridSize=(8, 8)
        )

        contrast_enhanced = (
            clahe.apply(gray)
        )

        # -------------------------------------------------
        # SHARPEN
        # -------------------------------------------------

        sharpen_kernel = np.array(
            [
                [0, -1, 0],
                [-1, 5, -1],
                [0, -1, 0]
            ]
        )

        sharpened = cv2.filter2D(

            contrast_enhanced,

            -1,

            sharpen_kernel
        )

        # -------------------------------------------------
        # ADAPTIVE THRESHOLD
        # -------------------------------------------------

        adaptive_thresh = (
            cv2.adaptiveThreshold(

                sharpened,

                255,

                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,

                cv2.THRESH_BINARY,

                11,

                2
            )
        )

        return {

            "original":
                image,

            "contrast_enhanced":
                contrast_enhanced,

            "sharpened":
                sharpened,

            "adaptive_thresh":
                adaptive_thresh,
        }


# ---------------------------------------------------------
# EASYOCR COMPATIBILITY FUNCTION
# ---------------------------------------------------------

def make_variants(
    image_path
):
    """
    Returns a list of:

        (variant_name, image)

    This is the function expected by
    medeye_ocr_engine.py.
    """

    processor = ImagePreprocessor()

    processed = processor.preprocess(
        image_path
    )

    return list(
        processed.items()
    )


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    print(
        "ImagePreprocessor ready."
    )