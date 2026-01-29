# Legacy Backup Directory

This directory contains historical code and documentation from the early development stages of the TransUnion PDF parser project.

## Archive Status

**Archived on**: 2026-01-29
**Archive file**: `legacy_backup_archive_20260129.tar.gz` (in project root)
**Archive size**: ~116 KB

## Contents

This directory includes:

- Early Python scripts for PDF processing
- Original Goals and planning documents
- Sample JSON reports from initial development
- Credit report samples and output text files

## Purpose

These files are kept for historical reference and to track the project's evolution. The current production codebase is in the `src/` directory.

## Migration

The best practices and lessons learned from this legacy code have been integrated into the current implementation:

- Modern FastAPI structure in `src/`
- Robust parsing engine with multi-currency support
- Comprehensive PII scrubbing
- Production-ready Docker deployment
- Complete test suite

## Restoration

If needed, the full legacy backup can be restored from:

```bash
tar -xzf legacy_backup_archive_20260129.tar.gz
```

---

**Do not modify these files.** They are preserved for historical reference only.
