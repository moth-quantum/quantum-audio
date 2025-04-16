# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2025-04-16

### Changed
- Extended `qiskit` support to `2.0.0`
  - Adjusted results object as the `header` instance is now changed to a dictionary. (Issue #43)  
  - Relaxed `qiskit-aer` version to support `qiskit==2.0.0`. (Issue #41)
- Adjusted internal API usage to align with changes in `some-core-lib@3.0.0`

### Notes
- This release is backward-compatible with previous versions of `qiskit` between `1.1.0` to `2.0.0`.

