"""Integration tests for GaMMa utilities: convert_picks_csv and from_seconds."""

import os

import numpy as np
import pandas as pd
import pytest

from gamma.utils import convert_picks_csv, from_seconds


class TestFromSeconds:
    """Tests for the from_seconds timestamp conversion."""

    @pytest.mark.unit
    def test_epoch_zero(self):
        result = from_seconds(0)
        assert result == "1970-01-01T00:00:00.000"

    @pytest.mark.unit
    def test_known_timestamp(self):
        # 2019-07-06T02:15:00.000 UTC
        ts = 1562379300.0
        result = from_seconds(ts)
        assert "2019-07-06" in result
        assert "02:15:00" in result

    @pytest.mark.unit
    def test_fractional_seconds(self):
        ts = 1562379300.123
        result = from_seconds(ts)
        assert ".123" in result


class TestConvertPicksCsv:
    """Integration tests for convert_picks_csv."""

    @pytest.fixture
    def sample_picks_and_stations(self):
        """Create minimal picks and stations DataFrames for testing."""
        picks = pd.DataFrame({
            "id": ["STA1_P", "STA1_S", "STA2_P", "STA2_S"],
            "timestamp": pd.to_datetime([
                "2019-07-06T02:15:00.000",
                "2019-07-06T02:15:05.000",
                "2019-07-06T02:15:01.000",
                "2019-07-06T02:15:07.000",
            ], utc=True),
            "type": ["P", "S", "P", "S"],
            "prob": [0.9, 0.8, 0.85, 0.75],
            "amp": [1e-5, 2e-5, 1.5e-5, 3e-5],
        })

        stations = pd.DataFrame({
            "id": ["STA1_P", "STA1_S", "STA2_P", "STA2_S"],
            "x(km)": [0.0, 0.0, 10.0, 10.0],
            "y(km)": [0.0, 0.0, 5.0, 5.0],
            "z(km)": [0.0, 0.0, -0.5, -0.5],
        })

        config = {
            "dims": ["x(km)", "y(km)", "z(km)"],
            "use_amplitude": True,
        }
        return picks, stations, config

    @pytest.mark.integration
    def test_output_shapes(self, sample_picks_and_stations):
        """convert_picks_csv should return arrays of consistent sizes."""
        picks, stations, config = sample_picks_and_stations
        data, locs, phase_type, phase_weight, pick_idx, pick_station_id = \
            convert_picks_csv(picks, stations, config)

        n = len(picks)
        assert data.shape[0] == n
        assert data.shape[1] == 2  # time + amplitude
        assert locs.shape == (n, 3)  # x, y, z
        assert len(phase_type) == n
        assert phase_weight.shape == (n, 1)
        assert len(pick_idx) == n
        assert len(pick_station_id) == n

    @pytest.mark.integration
    def test_phase_types_lowered(self, sample_picks_and_stations):
        """Phase types should be lowercased."""
        picks, stations, config = sample_picks_and_stations
        _, _, phase_type, _, _, _ = convert_picks_csv(picks, stations, config)
        assert all(pt in ["p", "s"] for pt in phase_type)

    @pytest.mark.integration
    def test_amplitude_log_transform(self, sample_picks_and_stations):
        """Amplitude column should be log10(amp * 100)."""
        picks, stations, config = sample_picks_and_stations
        data, _, _, _, _, _ = convert_picks_csv(picks, stations, config)
        expected_amp = np.log10(picks["amp"].values * 1e2)
        np.testing.assert_allclose(data[:, 1], expected_amp, rtol=1e-5)

    @pytest.mark.integration
    def test_without_amplitude(self, sample_picks_and_stations):
        """Without amplitude, data should only have time column."""
        picks, stations, config = sample_picks_and_stations
        config["use_amplitude"] = False
        data, _, _, _, _, _ = convert_picks_csv(picks, stations, config)
        assert data.shape[1] == 1  # time only

    @pytest.mark.integration
    def test_nan_stations_filtered(self):
        """Picks with missing station coordinates should be filtered out."""
        picks = pd.DataFrame({
            "id": ["STA1_P", "MISSING_P"],
            "timestamp": pd.to_datetime([
                "2019-07-06T02:15:00.000",
                "2019-07-06T02:15:01.000",
            ], utc=True),
            "type": ["P", "P"],
            "prob": [0.9, 0.8],
            "amp": [1e-5, 2e-5],
        })
        stations = pd.DataFrame({
            "id": ["STA1_P"],
            "x(km)": [0.0],
            "y(km)": [0.0],
            "z(km)": [0.0],
        })
        config = {"dims": ["x(km)", "y(km)", "z(km)"], "use_amplitude": True}
        data, locs, phase_type, phase_weight, pick_idx, pick_station_id = \
            convert_picks_csv(picks, stations, config)
        # MISSING_P has no station match, so should be filtered
        assert data.shape[0] == 1


class TestGammaPicksDataIntegrity:
    """Integration test that loads real picks.csv and station data to verify format compatibility."""

    @pytest.fixture
    def real_data_paths(self, gamma_dir):
        picks_csv = os.path.join(gamma_dir, "picks.csv")
        station_csv = os.path.join(gamma_dir, "tests", "SCSN_station_response.csv")
        if not os.path.exists(picks_csv) or not os.path.exists(station_csv):
            pytest.skip("Real test data not available")
        return picks_csv, station_csv

    @pytest.mark.integration
    def test_load_real_picks(self, real_data_paths):
        """Real picks.csv should load without errors and have expected columns."""
        picks_csv, _ = real_data_paths
        picks = pd.read_csv(picks_csv)
        required_cols = ["station_id", "phase_time", "phase_score", "phase_type"]
        for col in required_cols:
            assert col in picks.columns, f"Missing column: {col}"
        assert len(picks) > 0

    @pytest.mark.integration
    def test_load_real_stations(self, real_data_paths):
        """Real station CSV should load and have expected columns."""
        _, station_csv = real_data_paths
        stations = pd.read_csv(station_csv)
        required_cols = ["id", "latitude", "longitude", "elevation(m)"]
        for col in required_cols:
            assert col in stations.columns, f"Missing column: {col}"
        assert len(stations) > 0

    @pytest.mark.integration
    def test_picks_stations_id_overlap(self, real_data_paths):
        """Picks should reference station IDs that exist in the stations file."""
        picks_csv, station_csv = real_data_paths
        picks = pd.read_csv(picks_csv)
        stations = pd.read_csv(station_csv)
        pick_ids = set(picks["station_id"].unique())
        station_ids = set(stations["id"].unique())
        overlap = pick_ids & station_ids
        assert len(overlap) > 0, "No overlap between pick station IDs and station IDs"

    @pytest.mark.integration
    def test_phase_types_valid(self, real_data_paths):
        """All phase types should be P or S."""
        picks_csv, _ = real_data_paths
        picks = pd.read_csv(picks_csv)
        valid_types = {"P", "S"}
        actual_types = set(picks["phase_type"].unique())
        assert actual_types.issubset(valid_types), \
            f"Unexpected phase types: {actual_types - valid_types}"

    @pytest.mark.integration
    def test_phase_scores_in_range(self, real_data_paths):
        """All phase scores should be between 0 and 1."""
        picks_csv, _ = real_data_paths
        picks = pd.read_csv(picks_csv)
        assert picks["phase_score"].min() >= 0
        assert picks["phase_score"].max() <= 1.0
