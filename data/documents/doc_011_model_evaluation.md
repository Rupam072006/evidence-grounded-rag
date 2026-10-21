# Model Evaluation Metrics and Performance Assessment

## Metadata
- **document_id:** DOC-011
- **title:** Model Evaluation Metrics and Performance Assessment
- **source:** data/documents/model_evaluation.md
- **source_type:** technical_guide
- **version:** 1.0.0
- **created_at:** 2026-01-10T08:00:00Z
- **updated_at:** 2026-01-15T10:30:00Z
- **topic:** Model Evaluation

## 1. Overview
Evaluating predictive models rigorously is essential to ensure reliability, generalization, and safety before deployment in production environments. Quantitative metrics expose tradeoffs between false positives and false negatives, calibration discrepancies, and variance across data partitions. In retrieval and generation pipelines, evaluation governs both retrieval relevance and generative context synthesis. During context construction, the total token budget allocated for context passages is capped at 1,500 tokens (approximately 6,000 characters) to bound context overhead and preserve inference efficiency.

## 2. Main Concepts

### Confusion Matrix
A confusion matrix summarizes classification decisions across true classes and predicted classes:
- **True Positives (TP):** Positive instances correctly predicted as positive.
- **False Positives (FP):** Negative instances incorrectly predicted as positive (Type I error).
- **True Negatives (TN):** Negative instances correctly predicted as negative.
- **False Negatives (FN):** Positive instances incorrectly predicted as negative (Type II error).

### Classification Metrics
- **Accuracy:** The proportion of total correct predictions: $\frac{TP + TN}{TP + TN + FP + FN}$. Misleading when classes are heavily imbalanced.
- **Precision:** The proportion of predicted positive instances that are truly positive: $\frac{TP}{TP + FP}$. Crucial when false alarms incur high costs.
- **Recall (Sensitivity):** The proportion of actual positive instances correctly retrieved: $\frac{TP}{TP + FN}$. Essential in compliance and critical search where missed items are catastrophic.
- **F1-Score:** The harmonic mean of precision and recall: $2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$. Provides a single balanced score for imbalanced distributions.

### Regression Metrics
- **Mean Absolute Error (MAE):** Average magnitude of errors $\frac{1}{n} \sum |y_i - \hat{y}_i|$. Robust to extreme outliers.
- **Mean Squared Error (MSE):** Average of squared residuals $\frac{1}{n} \sum (y_i - \hat{y}_i)^2$. Penalizes large discrepancies severely.
- **Root Mean Squared Error (RMSE):** $\sqrt{\text{MSE}}$, expressing error in the original units of the dependent variable.
- **R-squared ($R^2$):** Coefficient of determination representing the proportion of variance explained by the model.

## 3. Explanation of Important Terms
- **Specificity:** True negative rate $\frac{TN}{TN + FP}$, measuring ability to reject negative instances.
- **ROC-AUC:** Area under the Receiver Operating Characteristic curve, measuring ranking discrimination across classification thresholds.
- **Context Budget Cap:** In RAG platforms like AegisCore, context passages retrieved for answer generation must fit within allocated inference windows. The total token budget allocated for context passages is capped at 1,500 tokens (approximately 6,000 characters).

## 4. Practical Example
The following Python script computes a comprehensive classification report and confusion matrix using scikit-learn:

```python
from sklearn.metrics import classification_report, confusion_matrix, f1_score
import numpy as np

# Ground-truth labels and model predictions
y_true = np.array([1, 0, 1, 1, 0, 1, 0, 0, 1, 0])
y_pred = np.array([1, 0, 1, 0, 0, 1, 1, 0, 1, 0])

# Compute confusion matrix
cm = confusion_matrix(y_true, y_pred)
print("Confusion Matrix:")
print(cm)

# Compute macro F1 and detailed report
macro_f1 = f1_score(y_true, y_pred, average="macro")
print(f"\nMacro F1: {macro_f1:.4f}")
print("\nClassification Report:")
print(classification_report(y_true, y_pred, target_names=["Negative", "Positive"]))
```

## 5. Limitations or Common Mistakes
- **Relying Exclusively on Accuracy:** In datasets where 99% of samples belong to one class, a trivial model predicting only the majority class scores 99% accuracy while exhibiting 0% recall on the minority class.
- **Unbounded Context Size:** Allowing retrieved evidence to expand arbitrarily causes prompt bloat, exceeds model context windows, and degrades generation accuracy. AegisCore explicitly mitigates this with its 1,500 token (6,000 character) limit.
- **Evaluating on Training Data:** Computing metrics on training samples yields over-optimistic results due to memorization.

## 6. Source References
- Scikit-learn Model Evaluation Metrics: https://scikit-learn.org/stable/modules/model_evaluation.html
- Powers, D. M. (2011). Evaluation: from precision, recall and F-measure to ROC, informedness, markedness and correlation: https://arxiv.org/abs/2010.16061
- Google Machine Learning Guide on Classification: https://developers.google.com/machine-learning/crash-course/classification/precision-and-recall

