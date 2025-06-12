#!/usr/bin/env python3
"""
Docker entrypoint for RAG Pipeline that supports both continuous and single-run modes.
"""
import os
import sys
import argparse
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    parser = argparse.ArgumentParser(description='RAG Pipeline Docker Entrypoint')
    parser.add_argument('--pipeline', type=str, choices=['local', 'google_drive'], 
                        default='local', help='Which pipeline to run')
    parser.add_argument('--mode', type=str, choices=['continuous', 'single'], 
                        default='continuous', help='Run mode: continuous or single check')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--directory', type=str, help='Directory to watch (for local pipeline)')
    parser.add_argument('--interval', type=int, default=60, 
                        help='Interval in seconds between checks (continuous mode only)')
    
    args = parser.parse_args()
    
    # Import the appropriate pipeline
    if args.pipeline == 'local':
        # Change to Local_Files directory for proper imports
        local_files_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Local_Files')
        os.chdir(local_files_dir)
        sys.path.insert(0, local_files_dir)
        
        from file_watcher import LocalFileWatcher
        import main as local_main_module
        
        if args.mode == 'single':
            # Single run mode - just do one check and exit
            config_path = args.config or 'config.json'
            watcher = LocalFileWatcher(
                watch_directory=args.directory,
                config_path=config_path
            )
            # Perform a single check (for now, call the continuous method once)
            # TODO: Implement actual single check method
            print("Single check mode not yet implemented. Running continuous mode instead.")
            watcher.watch_for_changes(interval_seconds=args.interval)
        else:
            # Continuous mode - use the existing main function
            sys.argv = ['main.py']
            if args.config:
                sys.argv.extend(['--config', args.config])
            if args.directory:
                sys.argv.extend(['--directory', args.directory])
            sys.argv.extend(['--interval', str(args.interval)])
            local_main_module.main()
            
    elif args.pipeline == 'google_drive':
        # Change to Google_Drive directory for proper imports
        google_drive_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Google_Drive')
        os.chdir(google_drive_dir)
        sys.path.insert(0, google_drive_dir)
        
        from drive_watcher import GoogleDriveWatcher
        import main as drive_main_module
        
        if args.mode == 'single':
            # Single run mode - just do one check and exit
            config_path = args.config or 'config.json'
            watcher = GoogleDriveWatcher(config_path=config_path)
            # Perform a single check (for now, call the continuous method once)
            # TODO: Implement actual single check method
            print("Single check mode not yet implemented. Running continuous mode instead.")
            watcher.watch_for_changes(interval_seconds=args.interval)
        else:
            # Continuous mode - use the existing main function
            sys.argv = ['main.py']
            if args.config:
                sys.argv.extend(['--config', args.config])
            sys.argv.extend(['--interval', str(args.interval)])
            drive_main_module.main()

if __name__ == "__main__":
    main()