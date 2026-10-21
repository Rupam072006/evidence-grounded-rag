# Dataset Partitioning, Validation Splits, and Grounding Contracts

## Metadata
- **document_id:** DOC-012
- **title:** Dataset Partitioning, Validation Splits, and Grounding Contracts
- **source:** data/documents/train_test_split.md
- **source_type:** technical_guide
- **version:** 1.0.0
- **created_at:** 2026-01-10T08:00:00Z
- **updated_at:** 2026-01-15T10:30:00Z
- **topic:** Train-Test Split and Grounding

## 1. Overview
Partitioning data into distinct, non-overlapping subsets is the cornerstone of empirical machine learning and statistical validation. Without rigorous partition boundaries, evaluations suffer from data leakage and optimistic bias, rendering production performance unpredictable. Analogous to dataset partitioning, Retrieval-Augmented Generation systems establish strict grounding boundaries: generated answers must be strictly grounded in retrieved evidence. Claims that fall outside retrieved passages are marked unsupported, guaranteeing answers reflect verified documentation rather than ungrounded model hallucination.

## 2. Main Concepts

### Training, Validation, and Test Partitions
Standard statistical pipelines divide available data into three dedicated subsets:
1. **Training Set (e.g., 70%):** Used directly by the learning algorithm to adjust model weights and internal parameters.
2. **Validation Set (e.g., 15%):** Used during model development to tune hyperparameters (such as regularization strength, learning rate, or tree depth) and perform early stopping without contaminating test sets.
3. **Test Set (e.g., 15%):** Held out completely until model finalization. Evaluated once to estimate true generalization error on unseen real-world distributions.

### Why Datasets Are Split
Empirical machine learning seeks to minimize generalization error rather than training error. Complex high-capacity models can easily memorize noise or idiosyncratic patterns present in training samples. Evaluating on an isolated test partition guarantees that reported performance reflects genuine inductive learning.

### Data Leakage and Prevention
Data leakage occurs when information from outside the training partition inadvertently influences model training:
- **Pre-split Transformation Leakage:** Normalizing features, imputing missing values, or fitting vectorizers on the full dataset before splitting leaks statistical properties (such as mean and variance) from test sets into training steps.
- **Temporal Leakage:** In time-series tasks, randomly shuffling splits leaks future events into past predictions. Temporal data must be partitioned chronologically.
- **Group Leakage:** Splitting repeated observations from the same subject across train and test sets leads to memorization of subject-specific traits. Grouped or stratified splits prevent this artifact.

## 3. Explanation of Important Terms
- **Stratified Splitting:** Partitioning datasets such that each split preserves the original class label proportions.
- **K-Fold Cross-Validation:** Dividing training data into $K$ equal folds, iteratively training on $K-1$ folds and evaluating on the remaining fold to obtain robust variance estimates.
- **Answer Generation Grounding Contract:** In AegisCore, generated answers must be strictly grounded in retrieved evidence. When retrieved evidence is insufficient or absent, the system emits a canonical refusal rather than interpolating assumptions.

## 4. Practical Example
The following Python script illustrates safe dataset splitting with standard pipeline isolation to prevent leakage:

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
import numpy as np

# Synthetic features and target
X = np.random.randn(100, 5)
y = X[:, 0] * 2.5 + np.random.randn(100) * 0.1

# 1. First split out test set
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 2. Fit preprocessor ONLY on training partition to avoid leakage
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 3. Train model on scaled train data
model = Ridge(alpha=1.0)
model.fit(X_train_scaled, y_train)
print(f"R2 Test Score: {model.score(X_test_scaled, y_test):.4f}")
```

## 5. Limitations or Common Mistakes
- **Fitting Scalers Globally:** Calling `fit_transform` across the entire dataset before calling `train_test_split` is the most widespread source of subtle data leakage.
- **Random Shuffling on Time-Series:** Using standard random splits on chronological data yields artificially inflated metrics that fail in production.
- **Violating Grounding Boundaries:** In RAG systems, allowing generators to supplement missing retrieved facts with internal parametric assumptions breaks source traceability and verification guarantees.

## 6. Source References
- Scikit-learn Cross-Validation and Data Splitting: https://scikit-learn.org/stable/modules/cross_validation.html
- Kaufman, S., et al. (2012). Leakage in Data Mining: Formulation, Detection, and Avoidance. ACM Transactions on KDD.
- Google Machine Learning Crash Course on Overfitting: https://developers.google.com/machine-learning/crash-course/overfitting

