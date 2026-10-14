"""Rule-based priority classification engine and experimental ML predictor for emergency reports.

ACADEMIC DISCLAIMER:
This is a heuristic educational rule-engine for triage demonstration only.
It is NOT a certified emergency dispatch system and does not replace human professional judgement.
"""

import re
from typing import Tuple, List, Dict, Any

# Configurable disaster baseline severity weights (0 - 50)
DISASTER_BASE_WEIGHTS: Dict[str, int] = {
    "Earthquake": 40,
    "Fire": 35,
    "Flood": 35,
    "Medical Emergency": 30,
    "Road Accident": 25,
    "Other": 15,
}

# Configurable keyword dictionaries with point weights
CRITICAL_KEYWORDS: Dict[str, int] = {
    "trapped": 40,
    "casualty": 45,
    "casualties": 45,
    "fatal": 45,
    "fatality": 45,
    "dead": 40,
    "death": 40,
    "unconscious": 35,
    "explosion": 35,
    "collapsed": 35,
    "collapse": 35,
    "drowning": 35,
    "massive fire": 35,
    "severe burn": 30,
    "heart attack": 35,
    "suffocation": 30,
    "multiple victims": 40,
    "critically injured": 35,
    "toxic leak": 35,
    "gas leak": 30,
}

HIGH_KEYWORDS: Dict[str, int] = {
    "injured": 25,
    "injury": 20,
    "burns": 25,
    "dense smoke": 20,
    "spreading": 20,
    "rising water": 25,
    "crushed": 25,
    "fracture": 20,
    "elderly": 15,
    "infant": 20,
    "children": 20,
    "hospital needed": 25,
    "electric shock": 25,
    "bleeding": 20,
    "chemical": 20,
    "short circuit": 15,
}

MEDIUM_KEYWORDS: Dict[str, int] = {
    "blocked road": 15,
    "road blocked": 15,
    "property damage": 15,
    "submerged vehicles": 20,
    "power outage": 15,
    "tree fallen": 15,
    "traffic halted": 15,
    "water logging": 15,
    "minor injury": 10,
    "structural crack": 15,
}

MITIGATING_KEYWORDS: Dict[str, int] = {
    "no injuries": -25,
    "no casualties": -30,
    "minor": -15,
    "controlled": -20,
    "under control": -25,
    "contained": -20,
    "cleared": -20,
    "safe": -15,
    "drill": -40,
    "false alarm": -40,
    "inspection": -25,
}


def classify_incident_priority(
    disaster_type: str,
    title: str,
    description: str,
    has_trapped_or_injured: bool = False,
    is_hazard_spreading: bool = False,
    has_structural_collapse: bool = False,
) -> Tuple[str, int, List[str]]:
    """Evaluates an incident report and returns (priority_label, total_score, reasons).

    Priority Levels:
      - Critical: score >= 70 (Red)
      - High: score >= 45 (Orange)
      - Medium: score >= 20 (Yellow)
      - Low: score < 20 (Green)
    """
    total_score = 0
    reasons: List[str] = []

    # 1. Base disaster type score
    base_score = DISASTER_BASE_WEIGHTS.get(disaster_type, 15)
    total_score += base_score
    reasons.append(f"Baseline category '{disaster_type}': +{base_score} pts")

    # 2. Text analysis over title + description
    combined_text = f"{title} {description}".lower()

    # Match critical keywords
    matched_critical = []
    for kw, pts in CRITICAL_KEYWORDS.items():
        if re.search(r"\b" + re.escape(kw) + r"\b", combined_text):
            total_score += pts
            matched_critical.append(f"'{kw}' (+{pts})")
            if len(matched_critical) >= 3:
                break
    if matched_critical:
        reasons.append(f"Critical triggers detected: {', '.join(matched_critical)}")

    # Match high severity keywords
    matched_high = []
    for kw, pts in HIGH_KEYWORDS.items():
        if re.search(r"\b" + re.escape(kw) + r"\b", combined_text):
            total_score += pts
            matched_high.append(f"'{kw}' (+{pts})")
            if len(matched_high) >= 3:
                break
    if matched_high:
        reasons.append(f"High risk indicators detected: {', '.join(matched_high)}")

    # Match medium keywords
    matched_med = []
    for kw, pts in MEDIUM_KEYWORDS.items():
        if re.search(r"\b" + re.escape(kw) + r"\b", combined_text):
            total_score += pts
            matched_med.append(f"'{kw}' (+{pts})")
            if len(matched_med) >= 2:
                break
    if matched_med:
        reasons.append(f"Medium risk indicators: {', '.join(matched_med)}")

    # Mitigating keywords (deduct points)
    matched_mitigating = []
    for kw, pts in MITIGATING_KEYWORDS.items():
        if re.search(r"\b" + re.escape(kw) + r"\b", combined_text):
            total_score += pts  # pts is negative
            matched_mitigating.append(f"'{kw}' ({pts})")
            if len(matched_mitigating) >= 2:
                break
    if matched_mitigating:
        reasons.append(f"Mitigating factors: {', '.join(matched_mitigating)}")

    # 3. Explicit form checkboxes
    if has_trapped_or_injured:
        total_score += 35
        reasons.append("Reporter flagged trapped persons / casualties (+35 pts)")

    if is_hazard_spreading:
        total_score += 20
        reasons.append("Reporter flagged rapidly spreading emergency (+20 pts)")

    if has_structural_collapse:
        total_score += 25
        reasons.append("Reporter flagged building / structural collapse (+25 pts)")

    # Score clamping
    total_score = max(0, min(100, total_score))

    # Priority determination
    if total_score >= 70:
        priority = "Critical"
    elif total_score >= 45:
        priority = "High"
    elif total_score >= 20:
        priority = "Medium"
    else:
        priority = "Low"

    reasons.append(f"Calculated Total Severity Score: {total_score}/100 -> Assigned '{priority}'")
    return priority, total_score, reasons


# -----------------------------------------------------------------------------
# Optional Scikit-learn Prototype Module (Academic Future Enhancement Demonstration)
# -----------------------------------------------------------------------------
class MLSeverityClassifier:
    """Demonstration prototype showing future ML-assisted severity classification

    using scikit-learn Naive Bayes / Logistic Regression.
    """

    def __init__(self):
        self.model = None
        self.vectorizer = None
        self._is_trained = False
        self._initialize_sample_model()

    def _initialize_sample_model(self):
        """Train a lightweight in-memory classifier with synthetic academic emergency corpus."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.naive_bayes import MultinomialNB
            from sklearn.pipeline import Pipeline

            # Academic demonstration corpus
            training_texts = [
                "building collapsed trapped victims under debris multiple deaths",
                "massive fire spreading rapidly hospital intensive care unit casualties",
                "severe flash flood drowning people trapped on rooftop water rising",
                "major road accident bus overturned multiple injured severe bleeding",
                "unconscious elderly person cardiac arrest CPR required immediately",
                "fire inside commercial kitchen smoke spreading firefighters on scene",
                "car collided with electric pole power cable snapped driver conscious injured",
                "flood water entered ground floor residential street blocked",
                "minor vehicle collision fender bender traffic slowed no injuries",
                "tree branch fell on sidewalk pedestrian path partially blocked",
                "water pipe leakage small puddle on road traffic passing safely",
                "controlled scheduled fire drill conducted in college campus all safe",
            ]
            training_labels = [
                "Critical",
                "Critical",
                "Critical",
                "High",
                "Critical",
                "High",
                "High",
                "Medium",
                "Low",
                "Medium",
                "Low",
                "Low",
            ]

            self.pipeline = Pipeline(
                [
                    ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
                    ("clf", MultinomialNB(alpha=0.5)),
                ]
            )
            self.pipeline.fit(training_texts, training_labels)
            self._is_trained = True
        except Exception:
            self._is_trained = False

    def predict(self, text: str) -> Dict[str, Any]:
        """Predict severity priority using scikit-learn demonstration pipeline."""
        if not self._is_trained:
            return {
                "available": False,
                "message": "Scikit-learn model offline or uninitialized",
            }

        try:
            prediction = self.pipeline.predict([text])[0]
            probabilities = self.pipeline.predict_proba([text])[0]
            classes = self.pipeline.classes_
            confidence = float(max(probabilities))
            return {
                "available": True,
                "prediction": prediction,
                "confidence": round(confidence * 100, 1),
                "model": "Scikit-Learn MultinomialNB Pipeline (TF-IDF)",
            }
        except Exception as e:
            return {"available": False, "error": str(e)}


# Singleton instance for future enhancement exploration
ml_classifier = MLSeverityClassifier()
