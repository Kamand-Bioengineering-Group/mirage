#!/usr/bin/env python3
"""
Backup script for XPECTO competition data
Creates a timestamped backup of all competition data
"""

import os
import shutil
import datetime
import argparse
import json
from pathlib import Path

def backup_data(source_dir, backup_dir=None, backup_name=None):
    """
    Create a backup of competition data
    
    Args:
        source_dir (str): Directory containing competition data
        backup_dir (str): Directory to store backups
        backup_name (str): Optional custom name for backup
    
    Returns:
        str: Path to the created backup
    """
    # Convert to Path objects
    source_path = Path(source_dir)
    
    # Validate source directory
    if not source_path.exists() or not source_path.is_dir():
        raise ValueError(f"Source directory does not exist: {source_dir}")
    
    # Create timestamp for backup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Set backup directory (use default if not specified)
    if backup_dir is None:
        backup_dir = source_path.parent / "backups"
    else:
        backup_dir = Path(backup_dir)
    
    # Create backup directory if it doesn't exist
    backup_dir.mkdir(exist_ok=True, parents=True)
    
    # Create backup name
    if backup_name is None:
        backup_name = f"xpecto_data_backup_{timestamp}"
    else:
        backup_name = f"{backup_name}_{timestamp}"
    
    # Full path for the backup
    backup_path = backup_dir / backup_name
    
    # Create backup
    shutil.copytree(source_path, backup_path)
    
    # Create metadata file
    metadata = {
        "backup_date": timestamp,
        "source_directory": str(source_path),
        "backup_name": backup_name,
        "files_count": len(list(backup_path.glob("**/*"))),
        "backup_version": "1.0"
    }
    
    with open(backup_path / "backup_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Backup created at: {backup_path}")
    return str(backup_path)

def list_backups(backup_dir):
    """List all available backups in the backup directory"""
    backup_path = Path(backup_dir)
    if not backup_path.exists():
        print(f"Backup directory does not exist: {backup_dir}")
        return
    
    backups = [d for d in backup_path.iterdir() if d.is_dir()]
    if not backups:
        print("No backups found.")
        return
    
    print(f"Found {len(backups)} backups:")
    for backup in sorted(backups):
        metadata_file = backup / "backup_metadata.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                metadata = json.load(f)
                print(f"  {backup.name} - Created: {metadata.get('backup_date', 'Unknown')}")
        else:
            print(f"  {backup.name} - No metadata")

def restore_backup(backup_path, restore_dir=None):
    """
    Restore a backup to the specified directory
    
    Args:
        backup_path (str): Path to the backup
        restore_dir (str): Directory to restore to (defaults to original location)
    """
    backup_path = Path(backup_path)
    
    # Validate backup
    if not backup_path.exists() or not backup_path.is_dir():
        raise ValueError(f"Backup directory does not exist: {backup_path}")
    
    metadata_file = backup_path / "backup_metadata.json"
    if not metadata_file.exists():
        raise ValueError(f"Not a valid backup: Missing metadata file")
    
    # Load metadata
    with open(metadata_file) as f:
        metadata = json.load(f)
    
    # Determine restore location
    if restore_dir is None:
        restore_dir = metadata.get("source_directory")
        if restore_dir is None:
            raise ValueError("Original source directory unknown. Please specify restore_dir.")
    
    restore_path = Path(restore_dir)
    
    # Confirm restoration
    if restore_path.exists():
        confirm = input(f"Restore will overwrite {restore_path}. Continue? (y/n): ")
        if confirm.lower() != 'y':
            print("Restoration cancelled.")
            return
        
        # Backup current data before restoring
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_backup = restore_path.parent / f"pre_restore_backup_{timestamp}"
        shutil.copytree(restore_path, temp_backup)
        print(f"Created safety backup at: {temp_backup}")
        
        # Remove current data
        shutil.rmtree(restore_path)
    
    # Copy backup files (excluding metadata)
    restore_path.mkdir(parents=True, exist_ok=True)
    
    for item in backup_path.glob("**/*"):
        if item.name == "backup_metadata.json":
            continue
        