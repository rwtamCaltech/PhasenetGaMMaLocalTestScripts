"""Unit tests for the postprocess module (extract_picks, calc_metrics, calc_timestamp)."""

import os
import tempfile

import numpy as np
import pytest

from postprocess import extract_picks, calc_metrics, calc_timestamp


class TestExtractPicks:
    """Tests for the extract_picks function."""

    @pytest.mark.unit
    def test_basic_pick_extraction(self, sample_predictions):
        """extract_picks should find P and S picks from clear prediction peaks."""
        picks = extract_picks(
            sample_predictions,
            file_names=["test_file.mseed"],
            begin_times=["2019-07-06T02:15:00.000+00:00"],
            station_ids=[["STA01"]],
            dt=0.01,
        )
        assert len(picks) >= 2, "Should detect at least P and S picks"

        phase_types = [p["phase_type"] for p in picks]
        assert "P" in phase_types, "Should detect a P-phase pick"
        assert "S" in phase_types, "Should detect an S-phase pick"

    @pytest.mark.unit
    def test_pick_fields(self, sample_predictions):
        """Each pick should have the required fields."""
        picks = extract_picks(sample_predictions, dt=0.01)
        required_fields = [
            "file_name", "station_id", "begin_time",
            "phase_index", "phase_time", "phase_score", "phase_type", "dt",
        ]
        for pick in picks:
            for field in required_fields:
                assert field in pick, f"Pick missing field: {field}"

    @pytest.mark.unit
    def test_default_file_names(self, sample_predictions):
        """When file_names is None, defaults should be generated."""
        picks = extract_picks(sample_predictions, dt=0.01)
        assert all(p["file_name"] == "0000" for p in picks)

    @pytest.mark.unit
    def test_default_station_ids(self, sample_predictions):
        """When station_ids is None, defaults should be generated."""
        picks = extract_picks(sample_predictions, dt=0.01)
        assert all(p["station_id"] == "0000" for p in picks)

    @pytest.mark.unit
    def test_default_begin_times(self, sample_predictions):
        """When begin_times is None, epoch time should be used."""
        picks = extract_picks(sample_predictions, dt=0.01)
        for pick in picks:
            assert "1970-01-01" in pick["begin_time"]

    @pytest.mark.unit
    def test_pick_time_ordering(self, sample_predictions):
        """P-wave pick should come before S-wave pick (P arrives first)."""
        picks = extract_picks(sample_predictions, dt=0.01)
        p_picks = [p for p in picks if p["phase_type"] == "P"]
        s_picks = [p for p in picks if p["phase_type"] == "S"]
        if p_picks and s_picks:
            assert p_picks[0]["phase_index"] < s_picks[0]["phase_index"]

    @pytest.mark.unit
    def test_phase_score_range(self, sample_predictions):
        """Phase scores should be between 0 and 1."""
        picks = extract_picks(sample_predictions, dt=0.01)
        for pick in picks:
            assert 0 <= pick["phase_score"] <= 1.0

    @pytest.mark.unit
    def test_phase_index_near_expected(self, sample_predictions):
        """Pick indices should be near the injected peaks (500 for P, 1200 for S)."""
        picks = extract_picks(sample_predictions, dt=0.01)
        p_indices = [p["phase_index"] for p in picks if p["phase_type"] == "P"]
        s_indices = [p["phase_index"] for p in picks if p["phase_type"] == "S"]
        assert any(abs(idx - 500) <= 5 for idx in p_indices), \
            f"P pick index should be near 500, got {p_indices}"
        assert any(abs(idx - 1200) <= 5 for idx in s_indices), \
            f"S pick index should be near 1200, got {s_indices}"

    @pytest.mark.unit
    def test_no_picks_for_noise(self):
        """A pure noise prediction (low values) should yield no picks."""
        preds = np.random.uniform(0, 0.1, (1, 3000, 1, 3)).astype(np.float32)
        preds[:, :, :, 0] = 0.9
        picks = extract_picks(preds, dt=0.01)
        assert len(picks) == 0

    @pytest.mark.unit
    def test_bytes_file_names(self, sample_predictions):
        """Byte-encoded file names should be decoded properly."""
        picks = extract_picks(
            sample_predictions,
            file_names=[b"test_file.mseed"],
            dt=0.01,
        )
        assert all(p["file_name"] == "test_file.mseed" for p in picks)

    @pytest.mark.unit
    def test_multiple_batches(self):
        """Multiple batches should each produce independent picks."""
        Nb, Nt, Ns, Nc = 3, 3000, 1, 3
        preds = np.zeros((Nb, Nt, Ns, Nc), dtype=np.float32)
        preds[:, :, :, 0] = 0.9
        for b in range(Nb):
            peak_loc = 300 + b * 500
            p_signal = np.exp(-0.5 * ((np.arange(Nt) - peak_loc) / 5) ** 2)
            preds[b, :, 0, 1] = p_signal
        picks = extract_picks(preds, dt=0.01)
        file_names = set(p["file_name"] for p in picks)
        assert len(file_names) == Nb


class TestCalcTimestamp:
    """Tests for the calc_timestamp function."""

    @pytest.mark.unit
    def test_basic_timestamp(self):
        result = calc_timestamp("2019-07-06T02:15:00.000", 5.12)
        assert result == "2019-07-06T02:15:05.120"

    @pytest.mark.unit
    def test_zero_offset(self):
        result = calc_timestamp("2019-07-06T02:15:00.000", 0.0)
        assert result == "2019-07-06T02:15:00.000"

    @pytest.mark.unit
    def test_fractional_seconds(self):
        result = calc_timestamp("2019-07-06T02:15:00.000", 0.01)
        assert result == "2019-07-06T02:15:00.010"

    @pytest.mark.unit
    def test_large_offset_crosses_minute(self):
        result = calc_timestamp("2019-07-06T02:15:50.000", 15.0)
        assert result == "2019-07-06T02:16:05.000"


class TestCalcMetrics:
    """Tests for the calc_metrics function."""

    @pytest.mark.unit
    def test_perfect_detection(self):
        """Perfect detection: all true picks detected, no false positives."""
        precision, recall, f1 = calc_metrics(nTP=10, nP=10, nT=10)
        assert precision == 1.0
        assert recall == 1.0
        assert f1 == 1.0

    @pytest.mark.unit
    def test_half_precision(self):
        """Half the positive picks are true positives."""
        precision, recall, f1 = calc_metrics(nTP=5, nP=10, nT=5)
        assert precision == 0.5
        assert recall == 1.0

    @pytest.mark.unit
    def test_half_recall(self):
        """Only half the true picks are detected."""
        precision, recall, f1 = calc_metrics(nTP=5, nP=5, nT=10)
        assert precision == 1.0
        assert recall == 0.5

    @pytest.mark.unit
    def test_f1_calculation(self):
        """F1 should be the harmonic mean of precision and recall."""
        precision, recall, f1 = calc_metrics(nTP=6, nP=10, nT=8)
        expected_p = 6 / 10
        expected_r = 6 / 8
        expected_f1 = 2 * expected_p * expected_r / (expected_p + expected_r)
        assert np.isclose(f1, expected_f1)
