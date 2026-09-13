"""
drug_lookup_medeye.py

MediLens.AI medicine database matching engine.

Matching priority:
    1. Exact canonical medicine name
    2. Exact brand/alias
    3. Strong fuzzy match
    4. Reject weak or ambiguous matches

Safety principle:
    A weak OCR reading must NOT be confidently converted into
    a medicine name.

The module keeps the older match_term() interface so the existing
MediLens OCR engine continues to work without requiring partial edits.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from rapidfuzz import fuzz, process


# =========================================================
# CONFIGURATION
# =========================================================

DEFAULT_DATABASE = "drugs_expanded_fixed.csv"

# Strong fuzzy threshold.
# We intentionally prefer rejecting an uncertain medicine over
# guessing a wrong medicine.
DEFAULT_MIN_SCORE = 75.0

# Difference required between the best and second-best candidate
# for a normal fuzzy match.
DEFAULT_AMBIGUITY_MARGIN = 10.0

# Very short OCR strings are dangerous for fuzzy matching.
SHORT_QUERY_LENGTH = 5

# For short queries, require a stronger score.
SHORT_QUERY_MIN_SCORE = 88.0


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize_text(text: Any) -> str:
    """
    Normalize text for reliable medicine matching.

    Examples:
        "OKACET"       -> "okacet"
        "Okacet-10"    -> "okacet 10"
        "Cetirizine®"  -> "cetirizine"
    """

    if text is None:
        return ""

    try:
        if pd.isna(text):
            return ""
    except Exception:
        pass

    text = str(text)

    # Unicode normalization.
    text = unicodedata.normalize("NFKC", text)

    text = text.lower().strip()

    # Replace common trademark symbols.
    text = text.replace("®", " ")
    text = text.replace("™", " ")

    # Keep letters/numbers and convert punctuation to spaces.
    text = re.sub(r"[^a-z0-9]+", " ", text)

    # Collapse whitespace.
    text = re.sub(r"\s+", " ", text).strip()

    return text


def clean_value(value: Any) -> str:
    """Return a safe printable string for database values."""

    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass

    return str(value).strip()


# =========================================================
# NOISE FILTER
# =========================================================

def looks_like_noise(text: str) -> bool:
    """
    Reject obviously useless OCR text.

    Examples:
        ""
        "6"
        "12345"
        "@@@"
        "x"
    """

    normalized = normalize_text(text)

    if not normalized:
        return True

    if len(normalized) < 2:
        return True

    compact = normalized.replace(" ", "")

    # Only numbers.
    if compact.isdigit():
        return True

    # No alphabetic characters.
    if not re.search(r"[a-z]", compact):
        return True

    return False


# =========================================================
# DRUG MATCHER
# =========================================================

class DrugMatcher:
    """
    Fast medicine lookup engine for MediLens.AI.

    The database is indexed once during initialization.

    Each search term stores:
        - canonical medicine name
        - whether the term is canonical or alias
        - complete medicine information
    """

    def __init__(
        self,
        csv_path: str = DEFAULT_DATABASE,
        min_score: float = DEFAULT_MIN_SCORE,
        ambiguity_margin: float = DEFAULT_AMBIGUITY_MARGIN,
    ):
        self.csv_path = csv_path
        self.min_score = float(min_score)
        self.ambiguity_margin = float(ambiguity_margin)

        self.drugs_df = self._load_database(csv_path)

        # Normalized search term -> metadata.
        self.search_index: Dict[str, Dict[str, Any]] = {}

        # Unique normalized search terms used by RapidFuzz.
        self.all_search_terms: List[str] = []

        # Fast exact canonical lookup.
        self.canonical_index: Dict[str, Dict[str, Any]] = {}

        # Fast exact alias lookup.
        self.alias_index: Dict[str, Dict[str, Any]] = {}

        self._build_index()

        print(
            f"✅ Loaded {len(self.drugs_df)} medicines "
            f"with {len(self.all_search_terms)} searchable names/aliases."
        )

    # =====================================================
    # DATABASE LOADING
    # =====================================================

    def _find_database(self, csv_path: str) -> Path:
        """
        Find the database without depending on the current
        working directory.

        Search order:
            1. User-provided path
            2. Project directory
            3. Directory containing this file
        """

        requested = Path(csv_path)

        candidates = []

        if requested.is_absolute():
            candidates.append(requested)
        else:
            candidates.extend(
                [
                    Path.cwd() / requested,
                    Path(__file__).resolve().parent / requested,
                ]
            )

        for candidate in candidates:
            if candidate.exists() and candidate.is_file():
                return candidate.resolve()

        raise FileNotFoundError(
            "\nMedicine database not found.\n\n"
            f"Requested file: {csv_path}\n\n"
            "Make sure the CSV is present in the project folder."
        )

    def _load_database(self, csv_path: str) -> pd.DataFrame:
        """Load and validate the medicine CSV."""

        database_path = self._find_database(csv_path)

        try:
            df = pd.read_csv(database_path)
        except Exception as exc:
            raise RuntimeError(
                f"Could not read medicine database: {database_path}\n"
                f"Error: {exc}"
            ) from exc

        # Remove completely empty rows.
        df = df.dropna(how="all").copy()

        if "name" not in df.columns:
            raise ValueError(
                "Medicine database must contain a 'name' column."
            )

        # Normalize column names.
        df.columns = [
            str(column).strip()
            for column in df.columns
        ]

        # Make sure medicine names are valid.
        df["name"] = df["name"].apply(clean_value)

        df = df[df["name"] != ""].reset_index(drop=True)

        if df.empty:
            raise ValueError(
                "Medicine database contains no valid medicine names."
            )

        return df

    # =====================================================
    # INDEX BUILDING
    # =====================================================

    def _register_term(
        self,
        term: Any,
        row_dict: Dict[str, Any],
        term_type: str,
    ) -> None:
        """
        Add one canonical name or alias to the search index.
        """

        normalized = normalize_text(term)

        if not normalized:
            return

        if looks_like_noise(normalized):
            return

        metadata = {
            "info": row_dict,
            "term": clean_value(term),
            "normalized_term": normalized,
            "term_type": term_type,
            "medicine_name": clean_value(row_dict.get("name")),
        }

        # Do not allow an alias/canonical collision to silently
        # overwrite an existing entry.
        if normalized in self.search_index:

            existing = self.search_index[normalized]

            # Canonical name gets priority over alias.
            if (
                existing["term_type"] == "alias"
                and term_type == "canonical"
            ):
                self.search_index[normalized] = metadata

            return

        self.search_index[normalized] = metadata
        self.all_search_terms.append(normalized)

    def _build_index(self) -> None:
        """Build all exact and fuzzy-search indexes."""

        for _, row in self.drugs_df.iterrows():

            row_dict = row.to_dict()

            medicine_name = clean_value(row_dict.get("name"))

            if not medicine_name:
                continue

            normalized_name = normalize_text(medicine_name)

            # ---------------------------------------------
            # Canonical medicine name
            # ---------------------------------------------

            self._register_term(
                medicine_name,
                row_dict,
                "canonical",
            )

            if normalized_name:
                self.canonical_index[normalized_name] = row_dict

            # ---------------------------------------------
            # Brand aliases
            # ---------------------------------------------

            aliases_value = row_dict.get("aliases", "")

            aliases_text = clean_value(aliases_value)

            if aliases_text:

                # Database format is comma-separated aliases.
                aliases = [
                    alias.strip()
                    for alias in aliases_text.split(",")
                    if alias.strip()
                ]

                for alias in aliases:

                    normalized_alias = normalize_text(alias)

                    if not normalized_alias:
                        continue

                    self._register_term(
                        alias,
                        row_dict,
                        "alias",
                    )

                    # Only store if it does not conflict with a
                    # canonical medicine name.
                    if (
                        normalized_alias not in self.canonical_index
                        and normalized_alias not in self.alias_index
                    ):
                        self.alias_index[normalized_alias] = row_dict

    # =====================================================
    # RESULT HELPERS
    # =====================================================

    @staticmethod
    def _no_match(
        method: str = "NO_MATCH",
        score: float = 0.0,
        margin: float = 0.0,
        candidates: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:

        return {
            "accepted": False,
            "matched_name": None,
            "score": float(score),
            "margin": float(margin),
            "method": method,
            "info": None,
            "candidates": candidates or [],
        }

    # =====================================================
    # EXACT MATCH
    # =====================================================

    def _exact_match(
        self,
        normalized_query: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Check canonical name first, then alias.

        Canonical names have higher priority.
        """

        # ---------------------------------------------
        # Exact canonical medicine
        # ---------------------------------------------

        if normalized_query in self.canonical_index:

            info = self.canonical_index[normalized_query]

            return {
                "accepted": True,
                "matched_name": clean_value(info.get("name")),
                "score": 100.0,
                "margin": 100.0,
                "method": "EXACT_CANONICAL",
                "info": info,
                "candidates": [
                    {
                        "name": clean_value(info.get("name")),
                        "score": 100.0,
                        "matched_on": "canonical_name",
                    }
                ],
            }

        # ---------------------------------------------
        # Exact brand alias
        # ---------------------------------------------

        if normalized_query in self.alias_index:

            info = self.alias_index[normalized_query]

            return {
                "accepted": True,
                "matched_name": clean_value(info.get("name")),
                "score": 100.0,
                "margin": 100.0,
                "method": "EXACT_ALIAS",
                "info": info,
                "candidates": [
                    {
                        "name": clean_value(info.get("name")),
                        "score": 100.0,
                        "matched_on": "alias",
                    }
                ],
            }

        return None

    # =====================================================
    # FUZZY MATCH
    # =====================================================

    def _fuzzy_match(
        self,
        normalized_query: str,
    ) -> Dict[str, Any]:
        """
        Perform conservative fuzzy matching.

        Uses RapidFuzz WRatio and then protects against
        ambiguous results.
        """

        if len(normalized_query) < 3:
            return self._no_match(
                method="TOO_SHORT"
            )

        matches = process.extract(
            normalized_query,
            self.all_search_terms,
            scorer=fuzz.WRatio,
            limit=8,
        )

        if not matches:
            return self._no_match()

        # -------------------------------------------------
        # Collapse aliases belonging to the same medicine.
        #
        # Example:
        #   cetzine -> Cetirizine
        #   okacet  -> Cetirizine
        #
        # We want medicine-level candidates rather than
        # several entries for the same medicine.
        # -------------------------------------------------

        medicine_candidates: Dict[str, Dict[str, Any]] = {}

        for term, score, _ in matches:

            metadata = self.search_index.get(term)

            if not metadata:
                continue

            info = metadata["info"]

            medicine_name = clean_value(
                info.get("name")
            )

            if not medicine_name:
                continue

            medicine_key = normalize_text(
                medicine_name
            )

            candidate = medicine_candidates.get(
                medicine_key
            )

            if candidate is None:

                medicine_candidates[medicine_key] = {
                    "name": medicine_name,
                    "score": float(score),
                    "matched_on": metadata["term_type"],
                    "matched_term": metadata["term"],
                    "info": info,
                }

            else:

                # Keep the strongest term belonging to
                # this medicine.
                if float(score) > candidate["score"]:

                    candidate["score"] = float(score)
                    candidate["matched_on"] = (
                        metadata["term_type"]
                    )
                    candidate["matched_term"] = (
                        metadata["term"]
                    )

        if not medicine_candidates:
            return self._no_match()

        candidates_sorted = sorted(
            medicine_candidates.values(),
            key=lambda item: item["score"],
            reverse=True,
        )

        best = candidates_sorted[0]

        best_score = float(best["score"])

        second_score = (
            float(candidates_sorted[1]["score"])
            if len(candidates_sorted) > 1
            else 0.0
        )

        margin = best_score - second_score

        display_candidates = [
            {
                "name": candidate["name"],
                "score": round(
                    candidate["score"],
                    2,
                ),
                "matched_on": candidate["matched_on"],
                "matched_term": candidate["matched_term"],
            }
            for candidate in candidates_sorted[:5]
        ]

        # -------------------------------------------------
        # Short OCR text requires stronger evidence.
        # -------------------------------------------------

        required_score = self.min_score

        if len(normalized_query.replace(" ", "")) <= SHORT_QUERY_LENGTH:
            required_score = max(
                required_score,
                SHORT_QUERY_MIN_SCORE,
            )

        # -------------------------------------------------
        # Weak fuzzy match
        # -------------------------------------------------

        if best_score < required_score:

            return self._no_match(
                method="LOW_CONFIDENCE",
                score=best_score,
                margin=margin,
                candidates=display_candidates,
            )

        # -------------------------------------------------
        # Ambiguous fuzzy match
        #
        # Do not guess if two different medicines are
        # extremely close.
        # -------------------------------------------------

        if (
            len(candidates_sorted) > 1
            and margin < self.ambiguity_margin
        ):

            return self._no_match(
                method="AMBIGUOUS_MATCH",
                score=best_score,
                margin=margin,
                candidates=display_candidates,
            )

        # -------------------------------------------------
        # Strong fuzzy match
        # -------------------------------------------------

        return {
            "accepted": True,
            "matched_name": best["name"],
            "score": best_score,
            "margin": margin,
            "method": "FUZZY_MATCH",
            "info": best["info"],
            "matched_term": best["matched_term"],
            "matched_on": best["matched_on"],
            "candidates": display_candidates,
        }

    # =====================================================
    # PUBLIC MATCH METHOD
    # =====================================================

    def match(
        self,
        query_term: str,
    ) -> Dict[str, Any]:
        """
        Main medicine matching function.

        Pipeline:
            normalize
                ↓
            noise rejection
                ↓
            exact canonical
                ↓
            exact alias
                ↓
            fuzzy matching
                ↓
            ambiguity protection
                ↓
            accepted/rejected
        """

        if query_term is None:
            return self._no_match(
                method="NO_MATCH"
            )

        if looks_like_noise(query_term):
            return self._no_match(
                method="OCR_NOISE"
            )

        normalized_query = normalize_text(
            query_term
        )

        if len(normalized_query) < 3:
            return self._no_match(
                method="TOO_SHORT"
            )

        # ---------------------------------------------
        # Exact match first.
        # ---------------------------------------------

        exact = self._exact_match(
            normalized_query
        )

        if exact is not None:
            return exact

        # ---------------------------------------------
        # Fuzzy match.
        # ---------------------------------------------

        return self._fuzzy_match(
            normalized_query
        )

    # =====================================================
    # OLD COMPATIBILITY METHOD
    # =====================================================

    def match_term(
        self,
        query_term: str,
        min_score: Optional[float] = None,
        ambiguity_margin: Optional[float] = None,
    ):
        """
        Backward-compatible method used by the existing
        medeye_ocr_engine.py.

        Returns:
            drug_info, match_score, match_status
        """

        old_min_score = self.min_score
        old_margin = self.ambiguity_margin

        try:

            if min_score is not None:
                self.min_score = float(min_score)

            if ambiguity_margin is not None:
                self.ambiguity_margin = float(
                    ambiguity_margin
                )

            result = self.match(
                query_term
            )

            if result["accepted"]:

                return (
                    result["info"],
                    result["score"],
                    result["method"],
                )

            return (
                None,
                result["score"],
                result["method"],
            )

        finally:

            self.min_score = old_min_score
            self.ambiguity_margin = old_margin


# =========================================================
# DIRECT TEST
# =========================================================

if __name__ == "__main__":

    print()
    print("=" * 65)
    print("MEDILENS.AI — MEDICINE MATCHER TEST")
    print("=" * 65)

    try:

        matcher = DrugMatcher()

        test_queries = [
            "Cetirizine",
            "Okacet",
            "Cetzine",
            "Cetirizne",
            "Cetzte",
            "Okacat",
            "Oacet",
            "6",
            "0",
            "xyznotamedicine",
        ]

        for query in test_queries:

            result = matcher.match(query)

            print()
            print(f"Query: {query}")
            print(f"Accepted: {result['accepted']}")
            print(f"Medicine: {result['matched_name']}")
            print(f"Score: {result['score']:.2f}")
            print(f"Method: {result['method']}")
            print(f"Margin: {result['margin']:.2f}")

            if result.get("candidates"):
                print("Candidates:")

                for candidate in result["candidates"][:3]:

                    print(
                        f"  - {candidate['name']} "
                        f"({candidate['score']:.2f}%)"
                    )

        print()
        print("=" * 65)
        print("MATCHER TEST COMPLETE")
        print("=" * 65)

    except Exception as exc:

        print()
        print("❌ Matcher test failed:")
        print(exc)