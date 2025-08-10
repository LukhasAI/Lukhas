"""
Test suite for LUKHAS entropy radar system.

This test module validates the entropy analysis, visualization,
and anomaly detection capabilities of the EntropyRadar system.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from core.entropy import EntropyRadar


class TestEntropyRadar:
    """Test basic entropy radar functionality."""

    def test_initialization(self):
        """Test entropy radar initialization."""
        radar = EntropyRadar(spike_threshold=0.9, drop_threshold=0.3)

        assert radar.spike_threshold == 0.9
        assert radar.drop_threshold == 0.3
        assert radar.sid_map == {}
        assert radar.entropy_map == {}

    def test_shannon_entropy_calculation(self):
        """Test Shannon entropy calculation."""
        radar = EntropyRadar()

        # Test with uniform distribution (high entropy)
        uniform_values = ["a", "b", "c", "d", "e"]
        entropy_uniform = radar.shannon_entropy(uniform_values)
        assert entropy_uniform > 2.0  # Should be close to log2(5) ≈ 2.32

        # Test with skewed distribution (low entropy)
        skewed_values = ["a", "a", "a", "a", "b"]
        entropy_skewed = radar.shannon_entropy(skewed_values)
        assert entropy_skewed < 1.0

        # Test with single value (zero entropy)
        single_values = ["a", "a", "a"]
        entropy_single = radar.shannon_entropy(single_values)
        assert entropy_single == 0.0

        # Test with empty list
        entropy_empty = radar.shannon_entropy([])
        assert entropy_empty == 0.0


class TestSIDCollection:
    """Test SID hash collection functionality."""

    def test_sid_collection(self, tmp_path):
        """Test collecting SID hashes from Python files."""
        # Create test Python files with SID hashes
        test_file1 = tmp_path / "module1.py"
        test_file1.write_text(
            """
sid_hash = "abc123def456"
another_var = "not a sid"
sid_hash = "789xyz"
"""
        )

        test_file2 = tmp_path / "module2.py"
        test_file2.write_text(
            """
class MyClass:
    sid_hash = "fedcba987"

def func():
    sid_hash = "112233"
"""
        )

        # Create a file without SIDs
        test_file3 = tmp_path / "no_sids.py"
        test_file3.write_text('print("No SIDs here")')

        radar = EntropyRadar()
        sid_map = radar.collect_sid_hashes(str(tmp_path))

        assert "module1" in sid_map
        assert "module2" in sid_map
        assert "no_sids" not in sid_map  # Should not appear if no SIDs

        assert len(sid_map["module1"]) == 2
        assert "abc123def456" in sid_map["module1"]
        assert "789xyz" in sid_map["module1"]

        assert len(sid_map["module2"]) == 2
        assert "fedcba987" in sid_map["module2"]

    def test_module_entropy_calculation(self):
        """Test entropy calculation for modules."""
        radar = EntropyRadar()

        # Manually set SID map
        radar.sid_map = {
            "high_entropy": ["abc", "def", "ghi", "jkl", "mno"],
            "low_entropy": ["abc", "abc", "abc", "def"],
            "zero_entropy": ["xyz", "xyz", "xyz"],
        }

        entropy_map = radar.calculate_module_entropy()

        assert entropy_map["high_entropy"] > entropy_map["low_entropy"]
        assert entropy_map["low_entropy"] > entropy_map["zero_entropy"]
        assert entropy_map["zero_entropy"] == 0.0

        # Check normalized values exist
        assert "high_entropy_normalized" in entropy_map
        assert entropy_map["high_entropy_normalized"] == 1.0


class TestLogParsing:
    """Test log parsing functionality."""

    def create_test_log(self, tmp_path, log_type="entropy_snapshot"):
        """Create a test JSONL log file."""
        log_file = tmp_path / "test_logs.jsonl"

        records = []
        base_time = datetime.now()

        if log_type == "entropy_snapshot":
            for i in range(10):
                records.append(
                    {
                        "timestamp": (base_time + timedelta(minutes=i)).isoformat(),
                        "entropy_snapshot": {
                            "entropy_delta": 0.1 * i,
                            "memory_trace_count": i * 10,
                            "affect_trace_count": i * 5,
                        },
                        "source_component": "test_module",
                    }
                )
        elif log_type == "metadata":
            for i in range(10):
                records.append(
                    {
                        "timestamp": (base_time + timedelta(minutes=i)).isoformat(),
                        "metadata": {
                            "emotion_score": 0.05 * i,
                            "category": f"subsystem_{i % 3}",
                        },
                    }
                )
        elif log_type == "drift_score":
            for i in range(10):
                records.append(
                    {
                        "timestamp": (base_time + timedelta(minutes=i)).isoformat(),
                        "entropy": 0.1 * i,
                        "drift_score": 0.05 * i,
                        "affect_vector": {
                            "joy": 0.5 + 0.05 * i,
                            "fear": 0.3 - 0.02 * i,
                        },
                    }
                )

        with open(log_file, "w") as f:
            for record in records:
                f.write(json.dumps(record) + "\n")

        return log_file

    def test_parse_entropy_logs(self, tmp_path):
        """Test parsing different log formats."""
        # Test entropy snapshot format
        log_file = self.create_test_log(tmp_path, "entropy_snapshot")
        radar = EntropyRadar()
        df = radar.parse_entropy_logs(str(log_file))

        assert len(df) == 10
        assert "timestamp" in df.columns
        assert "entropy" in df.columns
        assert "subsystem" in df.columns

        # Test metadata format
        log_file = self.create_test_log(tmp_path, "metadata")
        df = radar.parse_entropy_logs(str(log_file))

        assert len(df) == 10
        assert df["subsystem"].nunique() == 3

        # Test drift score format
        log_file = self.create_test_log(tmp_path, "drift_score")
        df = radar.parse_entropy_logs(str(log_file))

        assert len(df) == 10
        assert "volatility" in df.columns
        assert df["volatility"].iloc[-1] > df["volatility"].iloc[0]

    def test_parse_empty_log(self, tmp_path):
        """Test parsing empty log file."""
        log_file = tmp_path / "empty.jsonl"
        log_file.write_text("")

        radar = EntropyRadar()
        df = radar.parse_entropy_logs(str(log_file))

        assert df.empty

    def test_parse_corrupted_log(self, tmp_path):
        """Test parsing log with corrupted entries."""
        log_file = tmp_path / "corrupted.jsonl"
        with open(log_file, "w") as f:
            f.write('{"timestamp": "2025-01-01T00:00:00", "entropy": 0.5}\n')
            f.write("NOT VALID JSON\n")
            f.write('{"timestamp": "2025-01-01T00:01:00", "entropy": 0.6}\n')
            f.write('{"no_timestamp": true}\n')

        radar = EntropyRadar()
        df = radar.parse_entropy_logs(str(log_file))

        assert len(df) == 2  # Only valid records with timestamps


class TestTimeSeries:
    """Test time series analysis functionality."""

    def test_generate_time_series(self):
        """Test time series generation with rolling averages."""
        radar = EntropyRadar()

        # Create test data
        times = pd.date_range("2025-01-01", periods=20, freq="1min")
        df = pd.DataFrame(
            {
                "timestamp": times,
                "entropy": np.random.rand(20) * 0.5 + 0.3,
                "volatility": np.random.rand(20) * 0.3,
                "drift_score": np.random.rand(20) * 0.2,
                "subsystem": ["sys1", "sys2"] * 10,
            }
        )

        ts_df = radar.generate_time_series(df)

        # Check rolling columns were added
        assert "entropy_rolling" in ts_df.columns
        assert "volatility_rolling" in ts_df.columns
        assert "drift_rolling" in ts_df.columns

        # Check derivatives
        assert "entropy_derivative" in ts_df.columns

        # Check time features
        assert "hour" in ts_df.columns
        assert "day_of_week" in ts_df.columns

        # Check cumulative entropy
        assert "entropy_cumulative" in ts_df.columns
        assert (
            ts_df["entropy_cumulative"].iloc[-1] > ts_df["entropy_cumulative"].iloc[0]
        )

    def test_time_series_single_point(self):
        """Test time series with single data point."""
        radar = EntropyRadar()

        df = pd.DataFrame(
            {
                "timestamp": [datetime.now()],
                "entropy": [0.5],
                "volatility": [0.2],
                "drift_score": [0.1],
                "subsystem": ["test"],
            }
        )

        ts_df = radar.generate_time_series(df)

        # Should handle single point gracefully
        assert len(ts_df) == 1
        assert ts_df["entropy_rolling"].iloc[0] == ts_df["entropy"].iloc[0]


class TestInflectionDetection:
    """Test inflection point detection."""

    def test_detect_entropy_spikes(self):
        """Test detection of entropy spikes."""
        radar = EntropyRadar(spike_threshold=0.8)

        # Create data with clear spikes
        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2025-01-01", periods=10, freq="1min"),
                "entropy": [0.5, 0.6, 0.9, 0.5, 0.4, 0.95, 0.5, 0.6, 0.7, 0.85],
                "subsystem": ["test"] * 10,
            }
        )

        inflections = radar.detect_inflection_points(df)

        spikes = inflections["entropy_spikes"]
        assert len(spikes) == 3  # Values > 0.8
        assert spikes[0]["entropy_value"] == 0.9
        assert spikes[0]["type"] == "ΛENTROPY_SPIKE"

    def test_detect_entropy_drops(self):
        """Test detection of entropy drops."""
        radar = EntropyRadar(drop_threshold=0.3)

        # Create data with clear drops
        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2025-01-01", periods=5, freq="1min"),
                "entropy": [0.8, 0.4, 0.9, 0.5, 0.1],
                "subsystem": ["test"] * 5,
            }
        )

        inflections = radar.detect_inflection_points(df)

        drops = inflections["entropy_drops"]
        assert len(drops) == 2  # Drops > 0.3
        assert drops[0]["entropy_change"] == 0.4
        assert drops[1]["entropy_change"] == 0.4

    def test_detect_stable_phases(self):
        """Test detection of stable phases."""
        radar = EntropyRadar()

        # Create data with stable region
        stable_values = [0.5] * 10
        variable_values = [0.3, 0.7, 0.4, 0.8, 0.2]

        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2025-01-01", periods=25, freq="1min"),
                "entropy": variable_values
                + stable_values
                + variable_values
                + stable_values,
                "subsystem": ["test"] * 25,
            }
        )

        inflections = radar.detect_inflection_points(df)

        stable = inflections["stable_phases"]
        assert len(stable) >= 1
        assert stable[0]["entropy_variance"] < 0.05


class TestVisualization:
    """Test visualization generation."""

    def test_generate_entropy_radar_chart(self, tmp_path):
        """Test radar chart generation."""
        radar = EntropyRadar()

        # Set up test data
        radar.entropy_map = {f"module_{i}": np.random.rand() * 2 for i in range(10)}

        output_path = tmp_path / "test_radar.png"
        result_path = radar.generate_entropy_radar(str(output_path))

        assert Path(result_path).exists()
        assert Path(result_path).stat().st_size > 0

    def test_render_trend_graphs(self, tmp_path):
        """Test trend graph rendering."""
        radar = EntropyRadar()

        # Create test time series
        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2025-01-01", periods=50, freq="1min"),
                "entropy": np.sin(np.linspace(0, 4 * np.pi, 50)) * 0.3 + 0.5,
                "volatility": np.random.rand(50) * 0.3,
                "drift_score": np.random.rand(50) * 0.2,
                "subsystem": ["sys1", "sys2"] * 25,
            }
        )

        # Generate time series features
        df = radar.generate_time_series(df)
        radar.detect_inflection_points(df)

        # Test SVG output
        output_path = tmp_path / "test_trends"
        result_path = radar.render_trend_graphs(df, str(output_path), "svg")

        svg_path = Path(output_path).with_suffix(".svg")
        assert svg_path.exists()
        assert svg_path.stat().st_size > 0


class TestExport:
    """Test summary export functionality."""

    def test_export_json_summary(self, tmp_path):
        """Test JSON summary export."""
        radar = EntropyRadar()

        # Set up test data
        radar.entropy_map = {"module1": 1.5, "module2": 0.8}
        radar.time_series_df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2025-01-01", periods=10, freq="1min"),
                "entropy": np.random.rand(10),
                "volatility": np.random.rand(10),
                "drift_score": np.random.rand(10),
                "subsystem": ["sys1", "sys2"] * 5,
            }
        )
        radar.inflection_points = {
            "entropy_spikes": [{"timestamp": "2025-01-01", "type": "spike"}]
        }

        output_path = tmp_path / "summary"
        result_path = radar.export_summary(str(output_path), "json")

        # Verify file was created
        json_path = Path(result_path)
        assert json_path.exists()

        # Verify content
        with open(json_path) as f:
            data = json.load(f)
            assert "module_entropy" in data
            assert "time_series_stats" in data
            assert data["time_series_stats"]["data_points"] == 10

    def test_export_markdown_summary(self, tmp_path):
        """Test Markdown summary export."""
        radar = EntropyRadar()

        # Set up minimal test data
        radar.entropy_map = {"high_entropy": 0.9, "low_entropy": 0.2}
        radar.inflection_points = {
            "entropy_spikes": [
                {
                    "timestamp": "2025-01-01T00:00:00",
                    "entropy_value": 0.9,
                    "subsystem": "test",
                    "type": "ΛSPIKE",
                }
            ]
        }

        output_path = tmp_path / "summary"
        result_path = radar.export_summary(str(output_path), "markdown")

        # Verify file was created
        md_path = Path(result_path)
        assert md_path.exists()

        # Verify content
        content = md_path.read_text()
        assert "# 🎯 LUKHAS Entropy Analysis Report" in content
        assert "high_entropy" in content
        assert "ΛSPIKE" in content


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_data_handling(self):
        """Test handling of empty data."""
        radar = EntropyRadar()

        # Empty DataFrame
        df = pd.DataFrame()
        ts_df = radar.generate_time_series(df)
        assert ts_df.empty

        inflections = radar.detect_inflection_points(df)
        assert all(len(v) == 0 for v in inflections.values())

    def test_missing_log_file(self):
        """Test handling of missing log file."""
        radar = EntropyRadar()

        with pytest.raises(FileNotFoundError):
            radar.parse_entropy_logs("/nonexistent/path/file.jsonl")

    def test_radar_chart_no_data(self, tmp_path):
        """Test radar chart generation with no data."""
        radar = EntropyRadar()

        output_path = tmp_path / "empty_radar.png"
        result = radar.generate_entropy_radar(str(output_path))

        # Should return the path even if no chart was generated
        assert result == str(output_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
