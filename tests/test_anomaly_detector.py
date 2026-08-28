"""Tests for the anomaly detection engine."""

from congo_brain.models.budget import Budget, Transaction
from congo_brain.services.ai.anomaly_detector import detect_anomalies


def _make_transaction(
    txn_id: int = 1,
    budget_id: int = 1,
    amount: float = 1000.0,
    description: str = "Paiement normal",
    reference_number: str = "REF-001",
) -> Transaction:
    transaction = Transaction(
        budget_id=budget_id,
        amount=amount,
        description=description,
        transaction_type="expense",
        reference_number=reference_number,
        is_anomaly=False,
        anomaly_score=0.0,
        anomaly_reason=None,
    )
    transaction.id = txn_id
    return transaction


def _make_budget(
    budget_id: int = 1,
    allocated: float = 1_000_000.0,
    spent: float = 500_000.0,
    ministry: str = "Test Ministry",
) -> Budget:
    budget = Budget(
        ministry=ministry,
        sector="Test",
        allocated_amount=allocated,
        spent_amount=spent,
        fiscal_year=2026,
    )
    budget.id = budget_id
    return budget


class TestAnomalyDetector:
    def test_empty_transactions(self) -> None:
        result = detect_anomalies([])
        assert result == []

    def test_normal_transactions_no_anomalies(self) -> None:
        txns = [
            _make_transaction(1, 1, 1000.0, "Paiement normal"),
            _make_transaction(2, 1, 1200.0, "Achat fournitures"),
            _make_transaction(3, 1, 900.0, "Service rendu"),
        ]
        result = detect_anomalies(txns)
        assert len(result) == 0

    def test_keyword_detection(self) -> None:
        txns = [
            _make_transaction(1, 1, 1000.0, "Paiement normal"),
            _make_transaction(2, 1, 1200.0, "Paiement suspect pour services"),
            _make_transaction(3, 1, 900.0, "Achat standard"),
        ]
        result = detect_anomalies(txns)
        flagged_ids = {t.id for t in result}
        assert 2 in flagged_ids

    def test_keyword_multiple_matches(self) -> None:
        txns = [
            _make_transaction(1, 1, 1000.0, "Transaction confidentielle et irregulier"),
        ]
        result = detect_anomalies(txns)
        assert len(result) == 1
        assert result[0].anomaly_score > 0

    def test_budget_overbudget_detection(self) -> None:
        txns = [
            _make_transaction(1, 1, 50000.0, "Paiement normal"),
            _make_transaction(2, 1, 60000.0, "Depassement budget"),
        ]
        budgets = [_make_budget(1, allocated=100000.0, spent=200000.0)]  # over budget
        result = detect_anomalies(txns, budgets=budgets)
        assert len(result) == 2  # both flagged for overbudget

    def test_budget_ratio_detection(self) -> None:
        txns = [
            _make_transaction(1, 1, 90000.0, "Gros achat"),  # 90% of budget
        ]
        budgets = [_make_budget(1, allocated=100000.0, spent=90000.0)]
        result = detect_anomalies(txns, budgets=budgets)
        assert len(result) == 1
        assert result[0].anomaly_score > 0

    def test_anomaly_score_range(self) -> None:
        txns = [
            _make_transaction(1, 1, 1000.0, "Transaction suspect fictif"),
            _make_transaction(2, 1, 1200.0, "Achat normal"),
            _make_transaction(3, 1, 900.0, "Service rendu"),
        ]
        result = detect_anomalies(txns)
        for t in result:
            assert 0.0 <= t.anomaly_score <= 1.0

    def test_anomalies_sorted_by_score_desc(self) -> None:
        txns = [
            _make_transaction(1, 1, 1000.0, "suspect secret"),
            _make_transaction(2, 1, 1200.0, "Achat normal"),
            _make_transaction(3, 1, 900.0, "Service rendu"),
        ]
        result = detect_anomalies(txns)
        if len(result) > 1:
            scores = [t.anomaly_score for t in result]
            assert scores == sorted(scores, reverse=True)

    def test_custom_threshold(self) -> None:
        txns = [
            _make_transaction(1, 1, 1000.0, "Normal"),
            _make_transaction(2, 1, 1200.0, "Normal"),
            _make_transaction(3, 1, 900.0, "Normal"),
            _make_transaction(4, 1, 500000.0, "Normal"),  # outlier
        ]
        # Very high threshold should flag fewer anomalies
        result_strict = detect_anomalies(txns, threshold=4.0)
        result_loose = detect_anomalies(txns, threshold=1.0)
        assert len(result_strict) <= len(result_loose)

    def test_anomaly_reason_is_string(self) -> None:
        txns = [
            _make_transaction(1, 1, 1000.0, "Transaction suspect"),
            _make_transaction(2, 1, 1200.0, "Normal"),
            _make_transaction(3, 1, 900.0, "Normal"),
        ]
        result = detect_anomalies(txns)
        for t in result:
            assert isinstance(t.anomaly_reason, str)
            assert len(t.anomaly_reason) > 0
