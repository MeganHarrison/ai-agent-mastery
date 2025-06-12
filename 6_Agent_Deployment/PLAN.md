# RAG Pipeline Refactoring Plan for Single-Run Mode Support

## Overview
The current RAG pipeline is designed to run continuously in an infinite loop, checking for changes at regular intervals. To support deployment scenarios where the pipeline needs to run as a scheduled job (e.g., cron, Kubernetes CronJob, cloud schedulers), we need to add a single-run mode that performs one check cycle and exits.

## Current Architecture
Both `Local_Files/file_watcher.py` and `Google_Drive/drive_watcher.py` implement:
- `watch_for_changes()`: Runs an infinite loop checking for changes
- `get_changes()`: Fetches changed files since last check
- `process_file()`: Processes individual files
- `check_for_deleted_files()`: Checks for removed files

## Proposed Changes

### 1. Add `check_for_changes()` Method
Create a new method in both watchers that performs a single check cycle:

```python
def check_for_changes(self) -> Dict[str, Any]:
    """
    Perform a single check for changes and process them.
    Returns statistics about the check.
    """
```

This method will:
- Perform initial scan if not initialized
- Get changes since last check
- Process changed files
- Check for deleted files
- Update last check time
- Return statistics (files processed, deleted, errors)

### 2. Refactor `watch_for_changes()`
Extract the core logic from the infinite loop into `check_for_changes()` and have `watch_for_changes()` call it repeatedly:

```python
def watch_for_changes(self, interval_seconds: int = 60):
    while True:
        stats = self.check_for_changes()
        print(f"Check complete: {stats}")
        time.sleep(interval_seconds)
```

### 3. Update `docker_entrypoint.py`
The current entrypoint already supports single mode but needs to:
- Ensure proper initialization
- Call the new `check_for_changes()` method
- Return appropriate exit codes
- Log statistics

### 4. Configuration Updates
Add configuration options for single-run mode:
- `save_state`: Whether to persist state between runs (default: true)
- `initial_scan`: Whether to scan all files on first run (default: true)
- `process_all`: Force processing of all files regardless of state

### 5. State Management
Ensure state is properly persisted between single runs:
- Last check time saved to config
- Known files state preserved
- Handle edge cases (config corruption, first run)

## Implementation Steps

### Phase 1: Core Refactoring
1. Extract check logic from `watch_for_changes()` into `check_for_changes()` in both watchers
2. Update `watch_for_changes()` to use the new method
3. Add proper error handling and statistics collection

### Phase 2: Docker Integration
1. Update `docker_entrypoint.py` to properly call single-run mode
2. Add environment variable support for mode selection
3. Ensure proper exit codes for container orchestration

### Phase 3: Testing
1. Test continuous mode still works as before
2. Test single-run mode processes files correctly
3. Test state persistence between runs
4. Test error scenarios

## Benefits
- **Flexibility**: Deploy as continuous service or scheduled job
- **Resource Efficiency**: Only consume resources when needed
- **Better Integration**: Works with Kubernetes CronJobs, Cloud Scheduler, etc.
- **Cost Optimization**: Pay-per-run on serverless platforms

## Minimal Code Changes Required
The refactoring is designed to be minimal:
1. Move existing logic into new method
2. Update loop to call new method
3. Already have docker entrypoint structure in place
4. State management already exists (config saving)

## Risks and Mitigations
- **Risk**: State corruption between runs
  - **Mitigation**: Add state validation and recovery logic
- **Risk**: Missing changes between runs
  - **Mitigation**: Overlap check windows slightly
- **Risk**: Performance impact of frequent initialization
  - **Mitigation**: Cache initialization where possible