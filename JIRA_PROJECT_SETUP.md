# JIRA Project Setup Guide: PhasenetGaMMa Local Test Scripts

## Recommended JIRA Project Configuration

### Project Details

| Field | Value |
|-------|-------|
| **Project Name** | PhaseNet & GaMMa Local Testing |
| **Project Key** | `PGLT` (or `PNGT`) |
| **Project Type** | Scrum (supports Sprints and Backlog) |
| **Project Lead** | Ryan Tam |

### Board Configuration

- **Board Type**: Scrum Board
- **Estimation**: Story Points (Fibonacci: 1, 2, 3, 5, 8, 13)
- **Sprint Duration**: 2 weeks recommended

---

## Proposed Epic Structure

### Epic 1: Security & Critical Fixes
> Priority: Highest. Address security vulnerabilities and correctness bugs before any feature work.

### Epic 2: GaMMa Associator Improvements
> Tuning, bug fixes, and quality improvements for the event association algorithm.

### Epic 3: PhaseNet Quality & Reliability
> Amplitude calculation fixes, result validation, and reliability improvements across both PhaseNet versions.

### Epic 4: Code Quality & Infrastructure
> Configuration management, error handling, logging, and code cleanup.

### Epic 5: Testing & Validation
> Unit tests, integration tests, and regression test framework.

### Epic 6: Documentation
> Data flow documentation, API docs, and operational runbooks.

---

## Proposed Milestones (Versions/Releases)

| Milestone | Target | Description |
|-----------|--------|-------------|
| **v0.1 - Security Baseline** | Sprint 1 | All critical security and correctness issues resolved |
| **v0.2 - GaMMa Tuned** | Sprint 2-3 | GaMMa associator producing reliable event catalogs |
| **v0.3 - Amplitude Fix** | Sprint 3-4 | PhaseNet amplitude calculations validated and corrected |
| **v0.4 - Production Ready** | Sprint 5-6 | Full test coverage, configuration management, documentation |

---

## Complete Issue Backlog

### Epic 1: Security & Critical Fixes

#### PGLT-1: Remove hardcoded MongoDB credentials from source code
- **Type**: Bug
- **Priority**: Critical
- **Story Points**: 2
- **Sprint**: Sprint 1
- **Description**: `LatestPhasenetLocalTest/phasenet/predict.py` (lines 29-32) contains hardcoded MongoDB credentials (`root`/`quakeflow123`). Move to environment variables or a secrets management system.
- **Acceptance Criteria**:
  - Credentials read from environment variables
  - `.env.example` file documents required variables
  - `.env` added to `.gitignore`

#### PGLT-2: Fix command injection vulnerability in sampleChunkToMSEED
- **Type**: Bug
- **Priority**: Critical
- **Story Points**: 2
- **Sprint**: Sprint 1
- **Description**: `LatestPhasenetLocalTest/sampleChunkToMSEED.py` (line 99) uses `os.system()` with string concatenation, which is vulnerable to shell injection. Replace with `subprocess.run()` using list arguments.
- **Acceptance Criteria**:
  - `os.system()` replaced with `subprocess.run()`
  - Command arguments passed as a list, not concatenated string
  - Return code checked and errors logged

#### PGLT-3: Fix GaMMa hourly processing bug - wrong variable passed to association()
- **Type**: Bug
- **Priority**: Critical
- **Story Points**: 1
- **Sprint**: Sprint 1
- **Description**: In `GaMMaTest/GaMMaTest.py` (line 29), when processing >5000 picks hourly, the code filters picks into `picks_` but passes the unfiltered `picks` to `association()`. This means all picks are processed instead of just the hourly subset, defeating the purpose of the hourly split.
- **Acceptance Criteria**:
  - `association(picks, ...)` changed to `association(picks_, ...)`
  - Verified with test data that hourly filtering works correctly

---

### Epic 2: GaMMa Associator Improvements

#### PGLT-4: Fix event processing loop early break
- **Type**: Bug
- **Priority**: High
- **Story Points**: 3
- **Sprint**: Sprint 1
- **Description**: `GaMMaTest/GaMMaTest.py` (lines 277-281) contains a `break` statement that causes the event processing loop to exit after the first event. Only the first event's magnitude and probability are extracted.
- **Acceptance Criteria**:
  - `break` removed; all events processed
  - Results stored in appropriate data structure
  - Output verified against expected event count

#### PGLT-5: Remove or complete dead code in event analysis loop
- **Type**: Task
- **Priority**: Medium
- **Story Points**: 2
- **Sprint**: Sprint 2
- **Description**: `GaMMaTest/GaMMaTest.py` (lines 246-248) loops through events and filters high-probability picks but never uses the result. Either complete the analysis or remove the dead code.
- **Acceptance Criteria**:
  - Dead code either completed with meaningful analysis or removed
  - If completed: results logged or exported

#### PGLT-6: Tune GaMMa parameters to reduce over-detection
- **Type**: Story
- **Priority**: High
- **Story Points**: 8
- **Sprint**: Sprint 2
- **Milestone**: v0.2 - GaMMa Tuned
- **Description**: GaMMa currently detects more events than actually exist (overly aggressive). Systematic parameter tuning is needed. Key parameters to investigate:
  - `min_picks_per_eq` (currently `min(5, len(stations) // 2)`)
  - `dbscan_eps` parameters
  - `max_sigma11`, `max_sigma22`, `max_sigma12` thresholds
- **Acceptance Criteria**:
  - Test against known event catalog (e.g., USGS catalog for Ridgecrest sequence)
  - False positive rate documented
  - Optimal parameters documented with rationale
  - Before/after comparison report

#### PGLT-7: Create GaMMa parameter configuration file
- **Type**: Task
- **Priority**: Medium
- **Story Points**: 3
- **Sprint**: Sprint 2
- **Description**: Extract all hardcoded GaMMa configuration parameters (lines 96-126 of GaMMaTest.py) into a YAML/JSON configuration file. Currently parameters like `degree2km=111.19492474777779`, velocity model, and DBSCAN settings are embedded in code.
- **Acceptance Criteria**:
  - Configuration file created (`config/gamma_config.yaml`)
  - Script reads config from file
  - Command-line override for config file path
  - Default config documented

---

### Epic 3: PhaseNet Quality & Reliability

#### PGLT-8: Investigate and fix amplitude calculation in Latest PhaseNet
- **Type**: Bug
- **Priority**: High
- **Story Points**: 8
- **Sprint**: Sprint 3
- **Milestone**: v0.3 - Amplitude Fix
- **Description**: README documents that "The resulting amplitudes are wrong" in Latest PhaseNet. Root cause analysis needed to determine why amplitude calculations diverge from expected values. May involve tracing through seismological processing (integration, filtering, instrument response).
- **Acceptance Criteria**:
  - Root cause identified and documented
  - Fix implemented with validation against known correct amplitudes
  - Regression test created

#### PGLT-9: Document Earlier PhaseNet reliability issues
- **Type**: Task
- **Priority**: Medium
- **Story Points**: 3
- **Sprint**: Sprint 3
- **Description**: Earlier PhaseNet is noted as having "Unreliable results, but good speed." Document specific failure modes, when/why it fails, and under what conditions it may still be useful (e.g., real-time multi-station processing where speed matters more than accuracy).
- **Acceptance Criteria**:
  - Failure modes documented with examples
  - Comparison with Latest PhaseNet results
  - Recommendation on whether to keep, archive, or deprecate

#### PGLT-10: Parameterize test dataset selection
- **Type**: Task
- **Priority**: Medium
- **Story Points**: 3
- **Sprint**: Sprint 2
- **Description**: Multiple files use commented-out lines to switch between test datasets (e.g., `app_RT_ampCalc.py` lines 215-219, `sampleChunkToMSEED.py`). Replace with command-line arguments or a configuration file.
- **Acceptance Criteria**:
  - `argparse` or config-based dataset selection
  - All existing dataset options available as named choices
  - Default dataset specified

#### PGLT-11: Make model paths configurable
- **Type**: Task
- **Priority**: Medium
- **Story Points**: 2
- **Sprint**: Sprint 2
- **Description**: Model path `model/190703-214543` is hardcoded in multiple files: `predict.py`, `app.py`, `app_RT_ampCalc.py`, `slide_window.py`. Make configurable via command-line argument.
- **Acceptance Criteria**:
  - `--model-path` argument added to all entry points
  - Default value preserved for backward compatibility
  - Path validated at startup with clear error message if model not found

---

### Epic 4: Code Quality & Infrastructure

#### PGLT-12: Fix all bare exception handlers
- **Type**: Task
- **Priority**: Medium
- **Story Points**: 3
- **Sprint**: Sprint 2
- **Description**: Multiple files use bare `except:` clauses that catch all exceptions (including `SystemExit`, `KeyboardInterrupt`) and don't log exception details. Locations:
  - `data_reader.py` (lines 194-196, 458)
  - `predict.py` (lines 41-43)
  - `app_RT_ampCalc.py` (lines 134-138)
- **Acceptance Criteria**:
  - All bare `except:` replaced with `except Exception as e:`
  - Exception details logged: `logging.error(f"... failed: {e}")`

#### PGLT-13: Add error handling to main entry points
- **Type**: Task
- **Priority**: High
- **Story Points**: 3
- **Sprint**: Sprint 2
- **Description**: Main execution blocks in `GaMMaTest.py`, `app_RT_ampCalc.py`, and `sampleChunkToMSEED.py` have no try-except wrappers. Any error crashes the entire script with no graceful handling.
- **Acceptance Criteria**:
  - Main blocks wrapped with try-except
  - Meaningful error messages on failure
  - Non-zero exit codes on error

#### PGLT-14: Replace print() with Python logging module
- **Type**: Task
- **Priority**: Medium
- **Story Points**: 3
- **Sprint**: Sprint 3
- **Description**: All components use `print()` for output. Replace with structured logging using Python's `logging` module to enable log levels, timestamps, and configurable output.
- **Acceptance Criteria**:
  - All `print()` replaced with appropriate `logging.*()` calls
  - Log format includes timestamp, level, module
  - Log level configurable via environment variable or argument

#### PGLT-15: Add input CSV validation
- **Type**: Task
- **Priority**: Medium
- **Story Points**: 3
- **Sprint**: Sprint 3
- **Description**: No validation of CSV structure, required columns, data types, or value ranges before processing. Bad data silently propagates and errors appear downstream.
- **Acceptance Criteria**:
  - Schema validation for picks CSV (required columns, types)
  - Schema validation for stations CSV
  - Clear error messages on validation failure
  - Validation runs at startup before processing

#### PGLT-16: Clean up commented-out code
- **Type**: Task
- **Priority**: Low
- **Story Points**: 2
- **Sprint**: Sprint 4
- **Description**: Large blocks of commented-out code in `data_reader.py`, `visulization.py`, and other files. Remove dead code or add explanatory comments for intentionally-disabled sections.
- **Acceptance Criteria**:
  - Dead code removed
  - Any intentionally-disabled code has a comment explaining why
  - Git history preserves the removed code

#### PGLT-17: Fix filename typo: visulization.py -> visualization.py
- **Type**: Task
- **Priority**: Low
- **Story Points**: 1
- **Sprint**: Sprint 4
- **Description**: `LatestPhasenetLocalTest/phasenet/visulization.py` is misspelled. Rename to `visualization.py` and update all imports.
- **Acceptance Criteria**:
  - File renamed
  - All imports updated
  - No broken references

---

### Epic 5: Testing & Validation

#### PGLT-18: Create test framework and directory structure
- **Type**: Story
- **Priority**: High
- **Story Points**: 3
- **Sprint**: Sprint 3
- **Milestone**: v0.4 - Production Ready
- **Description**: No test files exist in the repository. Create a `tests/` directory with pytest configuration and test fixtures for sample seismic data.
- **Acceptance Criteria**:
  - `tests/` directory created
  - `pytest.ini` or `pyproject.toml` configured
  - Test fixtures for sample data
  - CI-ready test runner

#### PGLT-19: Add unit tests for PhaseNet pick extraction
- **Type**: Story
- **Priority**: High
- **Story Points**: 5
- **Sprint**: Sprint 4
- **Description**: Create unit tests that validate PhaseNet pick extraction against known correct picks from the Ridgecrest test data.
- **Acceptance Criteria**:
  - Tests for Latest PhaseNet pick extraction
  - Tests for Earlier PhaseNet pick extraction
  - Known-good picks stored as test fixtures
  - Tests validate pick times, phases (P/S), and probabilities

#### PGLT-20: Add unit tests for GaMMa association
- **Type**: Story
- **Priority**: High
- **Story Points**: 5
- **Sprint**: Sprint 4
- **Description**: Create unit tests that validate GaMMa event association against a known event catalog.
- **Acceptance Criteria**:
  - Tests for event association accuracy
  - Tests for false positive rate
  - Known event catalog as test fixture
  - Tests for edge cases (few picks, many picks, single station)

#### PGLT-21: Add integration test for full pipeline
- **Type**: Story
- **Priority**: Medium
- **Story Points**: 5
- **Sprint**: Sprint 5
- **Description**: End-to-end test: raw data -> PhaseNet picks -> GaMMa association -> event catalog. Validates the full pipeline against known results.
- **Acceptance Criteria**:
  - Full pipeline runs in test mode
  - Output compared against expected event catalog
  - Test data included in repository

---

### Epic 6: Documentation

#### PGLT-22: Create data flow documentation
- **Type**: Task
- **Priority**: Medium
- **Story Points**: 3
- **Sprint**: Sprint 4
- **Description**: Document how data flows between components: raw seismic data -> MSEED conversion -> PhaseNet detection -> pick CSV -> GaMMa association -> event catalog. Include input/output formats for each stage.
- **Acceptance Criteria**:
  - Data flow diagram
  - Input/output format specification for each component
  - Example data at each stage

#### PGLT-23: Document GaMMa parameter sensitivity
- **Type**: Task
- **Priority**: Medium
- **Story Points**: 3
- **Sprint**: Sprint 3
- **Description**: As part of GaMMa tuning (PGLT-6), document the sensitivity of each parameter and its effect on detection results.
- **Acceptance Criteria**:
  - Each parameter documented with range, default, and effect
  - Recommended values for different use cases (local earthquakes, regional, teleseismic)

---

## Sprint Plan

### Sprint 1: Critical Fixes (Foundation)
| Key | Summary | Points | Priority |
|-----|---------|--------|----------|
| PGLT-1 | Remove hardcoded credentials | 2 | Critical |
| PGLT-2 | Fix command injection | 2 | Critical |
| PGLT-3 | Fix GaMMa hourly processing bug | 1 | Critical |
| PGLT-4 | Fix event processing loop break | 3 | High |
| **Total** | | **8** | |

### Sprint 2: Configuration & GaMMa Tuning
| Key | Summary | Points | Priority |
|-----|---------|--------|----------|
| PGLT-5 | Remove/complete dead code | 2 | Medium |
| PGLT-6 | Tune GaMMa parameters | 8 | High |
| PGLT-7 | GaMMa config file | 3 | Medium |
| PGLT-10 | Parameterize dataset selection | 3 | Medium |
| PGLT-11 | Make model paths configurable | 2 | Medium |
| PGLT-12 | Fix bare exception handlers | 3 | Medium |
| PGLT-13 | Add main entry point error handling | 3 | High |
| **Total** | | **24** | |

### Sprint 3: PhaseNet & Code Quality
| Key | Summary | Points | Priority |
|-----|---------|--------|----------|
| PGLT-8 | Fix amplitude calculation | 8 | High |
| PGLT-9 | Document Earlier PhaseNet issues | 3 | Medium |
| PGLT-14 | Replace print() with logging | 3 | Medium |
| PGLT-15 | Add CSV validation | 3 | Medium |
| PGLT-18 | Create test framework | 3 | High |
| PGLT-23 | Document GaMMa parameters | 3 | Medium |
| **Total** | | **23** | |

### Sprint 4: Testing & Cleanup
| Key | Summary | Points | Priority |
|-----|---------|--------|----------|
| PGLT-16 | Clean up commented code | 2 | Low |
| PGLT-17 | Fix filename typo | 1 | Low |
| PGLT-19 | PhaseNet unit tests | 5 | High |
| PGLT-20 | GaMMa unit tests | 5 | High |
| PGLT-22 | Data flow documentation | 3 | Medium |
| **Total** | | **16** | |

### Sprint 5: Integration & Polish
| Key | Summary | Points | Priority |
|-----|---------|--------|----------|
| PGLT-21 | Integration test for full pipeline | 5 | Medium |
| **Total** | | **5** | |

---

## How to Create This in JIRA

### Step 1: Create the Project
1. Go to https://caltech-team-hpxnmtln.atlassian.net/jira/projects
2. Click **Create project**
3. Select **Scrum** template
4. Name: `PhaseNet & GaMMa Local Testing`
5. Key: `PGLT`
6. Click **Create**

### Step 2: Create Epics
In the project backlog, create the 6 epics listed above.

### Step 3: Create Issues
For each issue in the backlog above, create a JIRA issue with:
- **Type**: As specified (Bug, Story, or Task)
- **Epic**: Link to the appropriate epic
- **Priority**: As specified
- **Story Points**: As specified
- **Description**: Use the description and acceptance criteria from above

### Step 4: Create Sprints
1. In the Backlog view, create 5 sprints
2. Drag issues into the appropriate sprints per the Sprint Plan above

### Step 5: Create Versions (Milestones)
1. Go to Project Settings > Versions
2. Create the 4 versions listed in the Milestones table
3. Assign issues to their respective versions

### Optional: Bulk Import via CSV
JIRA supports CSV import. You can create a CSV file with columns:
`Summary, Issue Type, Priority, Story Points, Epic Link, Sprint, Fix Version, Description`
and import all issues at once via **Project Settings > Import issues from CSV**.
