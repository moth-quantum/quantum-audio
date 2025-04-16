# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2025-04-16

### Changed
- Extended `qiskit` support to `2.0.0`
  - Adjusted results object as the `header` instance is now changed to a dictionary. ([#43](https://github.com/moth-quantum/quantum-audio/issues/43))  
  - Relaxed `qiskit-aer` version requirement to support the latest `qiskit` version. ([#41](https://github.com/moth-quantum/quantum-audio/issues/41))

### Notes
- This release is backward-compatible with previous versions of `qiskit` between `1.1.0` to `2.0.0`.
- This release is not compatible with `qiskit<=1.0.0`.

