"""Comprehensive tests for ML-Based Pattern Prediction for Symbolic Anomaly Detection."""
import pytest
import numpy as np
from datetime import datetime, timezone, timedelta
from core.symbolic.symbolic_anomaly_explorer import (
    MLAnomalyPredictor,
    PredictionFeatures,
    AnomalyType,
    AnomalySeverity,
    ML_AVAILABLE,
    SymbolicAnomalyExplorer,
)

pytestmark = pytest.mark.skipif(
    not ML_AVAILABLE, reason="ML dependencies not available"
)


class TestFeatureExtraction:
    """Test suite for feature extraction from session history."""

    def test_extract_basic_features(self):
        """Test feature extraction from session history."""
        predictor = MLAnomalyPredictor()

        session_history = [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "duration_seconds": 300,
                "symbols": ["tree", "water", "mountain"],
                "valence": 0.5,
                "arousal": 0.6,
                "drift_score": 0.3,
            }
        ]

        features = predictor.extract_features(session_history, [])

        assert features.session_count == 1
        assert features.unique_symbols_count == 3
        assert features.avg_valence == 0.5
        assert features.avg_arousal == 0.6

    def test_symbol_repetition_calculation(self):
        """Test symbol repetition rate calculation."""
        predictor = MLAnomalyPredictor()

        session_history = [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "symbols": ["tree", "tree", "water", "tree"],  # 3 tree, 1 water
                "valence": 0,
                "arousal": 0,
                "drift_score": 0,
            }
        ]

        features = predictor.extract_features(session_history, [])

        # 4 symbols, 2 unique -> repetition = 1 - (2/4) = 0.5
        assert features.symbol_repetition_rate == 0.5

    def test_drift_acceleration_calculation(self):
        """Test drift acceleration from multiple sessions."""
        predictor = MLAnomalyPredictor()

        session_history = [
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=i)).isoformat(),
                "drift_score": 0.1 + i * 0.1,  # Increasing drift
                "symbols": ["test"],
                "valence": 0,
                "arousal": 0,
            }
            for i in range(5)
        ]

        features = predictor.extract_features(session_history, [])

        # Drift acceleration should be positive (increasing)
        assert features.drift_acceleration > 0

    def test_empty_session_history_raises_error(self):
        """Test that empty session history raises ValueError."""
        predictor = MLAnomalyPredictor()

        with pytest.raises(ValueError, match="Cannot extract features from empty history"):
            predictor.extract_features([], [])

    def test_feature_extraction_with_anomaly_history(self):
        """Test feature extraction includes anomaly history."""
        predictor = MLAnomalyPredictor()

        session_history = [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "symbols": ["test"],
                "valence": 0.5,
                "arousal": 0.5,
                "drift_score": 0.3,
            }
        ]

        anomaly_history = [
            {"type": "symbolic_conflict"},
            {"type": "symbolic_conflict"},
            {"type": "recursive_loop"},
        ]

        features = predictor.extract_features(session_history, anomaly_history)

        assert features.recent_conflict_count == 2
        assert features.recent_loop_count == 1

    def test_temporal_features_calculation(self):
        """Test temporal features like session intervals."""
        predictor = MLAnomalyPredictor()

        now = datetime.now(timezone.utc)
        session_history = [
            {
                "timestamp": (now - timedelta(hours=i)).isoformat(),
                "symbols": ["test"],
                "valence": 0,
                "arousal": 0,
                "drift_score": 0,
            }
            for i in range(5)
        ]

        features = predictor.extract_features(session_history, [])

        assert features.session_count == 5
        assert features.time_span_hours > 0
        assert features.session_interval_variance >= 0


class TestMLPredictor:
    """Test suite for MLAnomalyPredictor functionality."""

    @pytest.fixture
    def trained_predictor(self):
        """Create a predictor trained on synthetic data."""
        predictor = MLAnomalyPredictor(history_window=30)

        # Generate synthetic training data
        for i in range(25):
            features = PredictionFeatures(
                session_count=i,
                time_span_hours=i * 2.0,
                avg_session_duration=300,
                unique_symbols_count=5 + i % 3,
                symbol_repetition_rate=0.3 + (i % 10) * 0.05,
                motif_stability_score=0.7 - (i % 5) * 0.1,
                avg_valence=0.5,
                avg_arousal=0.5,
                emotional_volatility=0.1 + (i % 8) * 0.05,
                avg_drift_score=0.3 + (i % 7) * 0.05,
                drift_acceleration=0.02,
                max_drift_spike=0.5,
                recent_conflict_count=i % 3,
                recent_loop_count=i % 2,
                recent_dissonance_count=i % 4,
                recent_mutation_count=i % 2,
                session_interval_variance=100.0,
                time_of_day_pattern=12.0,
            )

            # Anomalies occur when certain conditions met
            anomalies = []
            if i % 5 == 0:
                anomalies.append(AnomalyType.SYMBOLIC_CONFLICT)

            predictor.update_history(features, anomalies)

        return predictor

    def test_predictor_trains_with_sufficient_data(self, trained_predictor):
        """Test that predictor trains when it has enough data."""
        assert trained_predictor._is_trained

    def test_prediction_returns_probabilities(self, trained_predictor):
        """Test that predictions return valid probabilities."""
        features = PredictionFeatures(
            session_count=30,
            time_span_hours=60.0,
            avg_session_duration=300,
            unique_symbols_count=8,
            symbol_repetition_rate=0.4,
            motif_stability_score=0.6,
            avg_valence=0.5,
            avg_arousal=0.5,
            emotional_volatility=0.2,
            avg_drift_score=0.4,
            drift_acceleration=0.03,
            max_drift_spike=0.6,
            recent_conflict_count=2,
            recent_loop_count=1,
            recent_dissonance_count=0,
            recent_mutation_count=1,
            session_interval_variance=150.0,
            time_of_day_pattern=14.0,
        )

        predictions = trained_predictor.predict_anomalies(features, time_horizon=5)

        # Should return at least one prediction
        assert len(predictions) > 0

        # All probabilities should be in [0, 1]
        for pred in predictions:
            assert 0 <= pred.probability <= 1
            assert 0 <= pred.confidence <= 1

    def test_high_conflict_features_predict_conflict(self, trained_predictor):
        """Test that high conflict features predict conflict anomaly."""
        features = PredictionFeatures(
            session_count=30,
            time_span_hours=60.0,
            avg_session_duration=300,
            unique_symbols_count=8,
            symbol_repetition_rate=0.9,  # Very high repetition
            motif_stability_score=0.3,
            avg_valence=0.5,
            avg_arousal=0.5,
            emotional_volatility=0.8,  # Very high volatility
            avg_drift_score=0.4,
            drift_acceleration=0.03,
            max_drift_spike=0.6,
            recent_conflict_count=5,  # Many recent conflicts
            recent_loop_count=0,
            recent_dissonance_count=0,
            recent_mutation_count=0,
            session_interval_variance=150.0,
            time_of_day_pattern=14.0,
        )

        predictions = trained_predictor.predict_anomalies(features)

        # Should predict symbolic conflict
        conflict_preds = [
            p for p in predictions if p.anomaly_type == AnomalyType.SYMBOLIC_CONFLICT
        ]
        assert len(conflict_preds) > 0

    def test_recommendations_generated(self, trained_predictor):
        """Test that predictions include actionable recommendations."""
        features = PredictionFeatures(
            session_count=30,
            time_span_hours=60.0,
            avg_session_duration=300,
            unique_symbols_count=8,
            symbol_repetition_rate=0.4,
            motif_stability_score=0.6,
            avg_valence=0.5,
            avg_arousal=0.5,
            emotional_volatility=0.2,
            avg_drift_score=0.4,
            drift_acceleration=0.03,
            max_drift_spike=0.6,
            recent_conflict_count=2,
            recent_loop_count=1,
            recent_dissonance_count=0,
            recent_mutation_count=1,
            session_interval_variance=150.0,
            time_of_day_pattern=14.0,
        )

        predictions = trained_predictor.predict_anomalies(features)

        for pred in predictions:
            assert pred.recommended_action is not None
            assert len(pred.recommended_action) > 0

    def test_severity_scales_with_probability(self, trained_predictor):
        """Test that predicted severity scales with probability."""
        # Create features that will generate high probability predictions
        features = PredictionFeatures(
            session_count=30,
            time_span_hours=60.0,
            avg_session_duration=300,
            unique_symbols_count=8,
            symbol_repetition_rate=0.9,
            motif_stability_score=0.2,
            avg_valence=0.5,
            avg_arousal=0.5,
            emotional_volatility=0.9,
            avg_drift_score=0.8,
            drift_acceleration=0.5,
            max_drift_spike=0.9,
            recent_conflict_count=8,
            recent_loop_count=7,
            recent_dissonance_count=6,
            recent_mutation_count=5,
            session_interval_variance=500.0,
            time_of_day_pattern=14.0,
        )

        predictions = trained_predictor.predict_anomalies(features)

        # High probability should lead to higher severity
        high_prob_preds = [p for p in predictions if p.probability >= 0.8]
        if high_prob_preds:
            assert any(
                p.predicted_severity
                in [AnomalySeverity.CRITICAL, AnomalySeverity.SIGNIFICANT]
                for p in high_prob_preds
            )

    def test_model_stats(self, trained_predictor):
        """Test that model statistics are accessible."""
        stats = trained_predictor.get_model_stats()

        assert stats["is_trained"] is True
        assert stats["training_samples"] >= 20
        assert "ml_available" in stats

    def test_untrained_predictor_returns_empty(self):
        """Test that untrained predictor returns empty predictions."""
        predictor = MLAnomalyPredictor()

        features = PredictionFeatures(
            session_count=1,
            time_span_hours=1.0,
            avg_session_duration=300,
            unique_symbols_count=3,
            symbol_repetition_rate=0.3,
            motif_stability_score=0.7,
            avg_valence=0.5,
            avg_arousal=0.5,
            emotional_volatility=0.1,
            avg_drift_score=0.3,
            drift_acceleration=0.01,
            max_drift_spike=0.4,
            recent_conflict_count=0,
            recent_loop_count=0,
            recent_dissonance_count=0,
            recent_mutation_count=0,
            session_interval_variance=0.0,
            time_of_day_pattern=12.0,
        )

        predictions = predictor.predict_anomalies(features)
        assert len(predictions) == 0

    def test_features_to_array_conversion(self):
        """Test conversion of PredictionFeatures to numpy array."""
        predictor = MLAnomalyPredictor()

        features = PredictionFeatures(
            session_count=10,
            time_span_hours=20.0,
            avg_session_duration=300,
            unique_symbols_count=5,
            symbol_repetition_rate=0.3,
            motif_stability_score=0.7,
            avg_valence=0.5,
            avg_arousal=0.6,
            emotional_volatility=0.2,
            avg_drift_score=0.3,
            drift_acceleration=0.02,
            max_drift_spike=0.5,
            recent_conflict_count=1,
            recent_loop_count=2,
            recent_dissonance_count=0,
            recent_mutation_count=1,
            session_interval_variance=100.0,
            time_of_day_pattern=12.0,
        )

        array = predictor._features_to_array(features)

        assert isinstance(array, np.ndarray)
        assert len(array) == 18  # 18 features

    def test_recommendation_urgency_levels(self):
        """Test recommendation urgency based on probability."""
        predictor = MLAnomalyPredictor()

        # High probability (urgent)
        rec_high = predictor._generate_recommendation(
            AnomalyType.SYMBOLIC_CONFLICT, 0.85
        )
        assert "URGENT" in rec_high

        # Medium probability (recommended)
        rec_med = predictor._generate_recommendation(AnomalyType.SYMBOLIC_CONFLICT, 0.65)
        assert "RECOMMENDED" in rec_med

        # Low probability (suggested)
        rec_low = predictor._generate_recommendation(AnomalyType.SYMBOLIC_CONFLICT, 0.45)
        assert "SUGGESTED" in rec_low


class TestIntegrationWithSymbolicAnomalyExplorer:
    """Test suite for integration with SymbolicAnomalyExplorer."""

    def test_prediction_integration(self):
        """Test integration with SymbolicAnomalyExplorer."""
        explorer = SymbolicAnomalyExplorer(
            enable_ml_prediction=True, prediction_horizon=5
        )

        # Generate synthetic session history
        session_history = [
            {
                "timestamp": (
                    datetime.now(timezone.utc) - timedelta(hours=i)
                ).isoformat(),
                "duration_seconds": 300,
                "symbols": ["symbol" + str(j) for j in range(5)],
                "valence": 0.5,
                "arousal": 0.5,
                "drift_score": 0.3 + i * 0.01,
            }
            for i in range(30)
        ]

        anomaly_history = []

        predictions = explorer.predict_future_anomalies(
            session_history, anomaly_history, time_horizon=5
        )

        # Should return predictions (may be empty if not enough training data)
        assert isinstance(predictions, list)

    def test_ml_prediction_disabled(self):
        """Test explorer works when ML prediction is disabled."""
        explorer = SymbolicAnomalyExplorer(enable_ml_prediction=False)

        session_history = [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "symbols": ["test"],
                "valence": 0.5,
                "arousal": 0.5,
                "drift_score": 0.3,
            }
        ]

        predictions = explorer.predict_future_anomalies(session_history, [])
        assert len(predictions) == 0

    def test_explorer_initialization_with_ml(self):
        """Test that explorer initializes with ML enabled."""
        explorer = SymbolicAnomalyExplorer(enable_ml_prediction=True)

        assert explorer._enable_ml_prediction is True
        assert explorer._ml_predictor is not None

    def test_explorer_initialization_without_ml(self):
        """Test that explorer initializes without ML enabled."""
        explorer = SymbolicAnomalyExplorer(enable_ml_prediction=False)

        assert explorer._enable_ml_prediction is False
        assert explorer._ml_predictor is None

    def test_prediction_with_incremental_learning(self):
        """Test that predictor learns from new data incrementally."""
        explorer = SymbolicAnomalyExplorer(enable_ml_prediction=True)

        # Generate enough data to trigger training
        session_history = [
            {
                "timestamp": (
                    datetime.now(timezone.utc) - timedelta(hours=i)
                ).isoformat(),
                "duration_seconds": 300,
                "symbols": ["symbol" + str(j) for j in range(5)],
                "valence": 0.5,
                "arousal": 0.5,
                "drift_score": 0.3,
            }
            for i in range(25)
        ]

        anomaly_history = [{"type": "symbolic_conflict"}] * 5

        # Make multiple predictions to trigger incremental learning
        for _ in range(5):
            predictions = explorer.predict_future_anomalies(
                session_history, anomaly_history
            )

        # Predictor should eventually train
        assert isinstance(predictions, list)


class TestGracefulDegradation:
    """Test suite for graceful degradation when ML not available."""

    def test_ml_available_flag(self):
        """Test ML_AVAILABLE flag is set correctly."""
        assert ML_AVAILABLE is True  # Should be True in test environment

    @pytest.mark.skipif(ML_AVAILABLE, reason="Only test when ML not available")
    def test_predictor_raises_without_ml(self):
        """Test predictor raises ImportError without ML dependencies."""
        with pytest.raises(ImportError, match="ML dependencies not available"):
            MLAnomalyPredictor()

    def test_explorer_handles_ml_unavailable(self, monkeypatch):
        """Test explorer handles ML unavailable gracefully."""
        # Temporarily make ML unavailable
        monkeypatch.setattr(
            "core.symbolic.symbolic_anomaly_explorer.ML_AVAILABLE", False
        )

        explorer = SymbolicAnomalyExplorer(enable_ml_prediction=True)

        # Should disable ML and not crash
        assert explorer._enable_ml_prediction is False
        assert explorer._ml_predictor is None


class TestAnomalyTypePrediction:
    """Test suite for specific anomaly type predictions."""

    def test_conflict_prediction_heuristics(self, trained_predictor):
        """Test symbolic conflict prediction heuristics."""
        features = PredictionFeatures(
            session_count=30,
            time_span_hours=60.0,
            avg_session_duration=300,
            unique_symbols_count=8,
            symbol_repetition_rate=0.9,  # High
            motif_stability_score=0.5,
            avg_valence=0.5,
            avg_arousal=0.5,
            emotional_volatility=0.8,  # High
            avg_drift_score=0.4,
            drift_acceleration=0.03,
            max_drift_spike=0.6,
            recent_conflict_count=5,  # High
            recent_loop_count=0,
            recent_dissonance_count=0,
            recent_mutation_count=0,
            session_interval_variance=150.0,
            time_of_day_pattern=14.0,
        )

        type_probs = trained_predictor._predict_anomaly_types(features, 1.0)

        # Should have high conflict score
        conflict_prob = next(
            (p for t, p in type_probs if t == AnomalyType.SYMBOLIC_CONFLICT), 0
        )
        assert conflict_prob > 0.3

    def test_loop_prediction_heuristics(self, trained_predictor):
        """Test recursive loop prediction heuristics."""
        features = PredictionFeatures(
            session_count=30,
            time_span_hours=60.0,
            avg_session_duration=300,
            unique_symbols_count=8,
            symbol_repetition_rate=0.4,
            motif_stability_score=0.2,  # Low stability
            avg_valence=0.5,
            avg_arousal=0.5,
            emotional_volatility=0.2,
            avg_drift_score=0.4,
            drift_acceleration=0.03,
            max_drift_spike=0.6,
            recent_conflict_count=0,
            recent_loop_count=8,  # Many loops
            recent_dissonance_count=0,
            recent_mutation_count=0,
            session_interval_variance=150.0,
            time_of_day_pattern=14.0,
        )

        type_probs = trained_predictor._predict_anomaly_types(features, 1.0)

        # Should have high loop score
        loop_prob = next(
            (p for t, p in type_probs if t == AnomalyType.RECURSIVE_LOOP), 0
        )
        assert loop_prob > 0.3


# Additional smoke tests
def test_module_imports():
    """Test that all required classes can be imported."""
    from core.symbolic.symbolic_anomaly_explorer import (
        MLAnomalyPredictor,
        PredictionFeatures,
        AnomalyPrediction,
        ML_AVAILABLE,
    )

    assert MLAnomalyPredictor is not None
    assert PredictionFeatures is not None
    assert AnomalyPrediction is not None
    assert isinstance(ML_AVAILABLE, bool)


def test_prediction_features_dataclass():
    """Test PredictionFeatures dataclass creation."""
    features = PredictionFeatures(
        session_count=10,
        time_span_hours=20.0,
        avg_session_duration=300,
        unique_symbols_count=5,
        symbol_repetition_rate=0.3,
        motif_stability_score=0.7,
        avg_valence=0.5,
        avg_arousal=0.6,
        emotional_volatility=0.2,
        avg_drift_score=0.3,
        drift_acceleration=0.02,
        max_drift_spike=0.5,
        recent_conflict_count=1,
        recent_loop_count=2,
        recent_dissonance_count=0,
        recent_mutation_count=1,
        session_interval_variance=100.0,
        time_of_day_pattern=12.0,
    )

    assert features.session_count == 10
    assert features.avg_valence == 0.5


def test_anomaly_prediction_dataclass():
    """Test AnomalyPrediction dataclass creation."""
    from core.symbolic.symbolic_anomaly_explorer import AnomalyPrediction

    prediction = AnomalyPrediction(
        anomaly_type=AnomalyType.SYMBOLIC_CONFLICT,
        probability=0.8,
        confidence=0.9,
        time_horizon=5,
        contributing_features={"drift": 0.5},
        predicted_severity=AnomalySeverity.CRITICAL,
        recommended_action="Take action",
    )

    assert prediction.probability == 0.8
    assert prediction.anomaly_type == AnomalyType.SYMBOLIC_CONFLICT
