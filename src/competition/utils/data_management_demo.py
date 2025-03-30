#!/usr/bin/env python3
"""
Data Management Demo Script

This script demonstrates how to use the data management utilities for the competition system,
including backup, import/export, scenario management, and storage integrity validation.
"""
import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent.parent
sys.path.append(str(project_root))

from src.competition.utils.data_management import DataManager, create_advanced_scenarios
from src.competition.data.storage import LocalStorageProvider
from src.competition.data.enhanced_storage import EnhancedLocalStorageProvider


def setup_argparse():
    """Set up command line argument parsing."""
    parser = argparse.ArgumentParser(description="Competition Data Management Demo")
    
    # Action selector
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument("--backup", action="store_true", help="Create a data backup")
    action_group.add_argument("--restore", help="Restore from a backup file")
    action_group.add_argument("--export", action="store_true", help="Export data to CSV/JSON")
    action_group.add_argument("--import-scenario", help="Import a scenario from JSON file")
    action_group.add_argument("--create-scenarios", action="store_true", help="Create sample advanced scenarios")
    action_group.add_argument("--validate", action="store_true", help="Validate storage integrity")
    action_group.add_argument("--demo-all", action="store_true", help="Run all demo functions in sequence")
    
    # General options
    parser.add_argument("--data-dir", default="data", help="Data directory (default: data)")
    parser.add_argument("--enhanced", action="store_true", help="Use enhanced storage provider")
    parser.add_argument("--output-dir", default="export", help="Directory for exports (default: export)")
    parser.add_argument("--format", choices=["json", "csv"], default="json", help="Export format (default: json)")
    
    return parser.parse_args()


def backup_demo(data_manager, args):
    """Demonstrate data backup functionality."""
    print("\n=== Backup Demonstration ===")
    
    # Create a backup
    backup_path = data_manager.backup_data(backup_dir="backups")
    
    print(f"Backup created at: {backup_path}")
    print(f"You can restore this backup using: --restore {backup_path}")


def restore_demo(data_manager, args):
    """Demonstrate backup restoration."""
    if not args.restore:
        print("Error: No backup file specified")
        return
        
    print(f"\n=== Restore Demonstration ===")
    print(f"Restoring from backup: {args.restore}")
    
    # Restore from specified backup
    success = data_manager.restore_backup(args.restore)
    
    if success:
        print("Backup restored successfully")
    else:
        print("Backup restoration failed")


def export_demo(data_manager, args):
    """Demonstrate data export functionality."""
    print(f"\n=== Export Demonstration ===")
    print(f"Exporting data in {args.format} format to {args.output_dir}")
    
    # Export data
    success = data_manager.export_data(args.output_dir, args.format)
    
    if success:
        print(f"Data exported successfully to {args.output_dir}")
        print(f"Exported directories:")
        for subdir in ["players", "attempts", "scenarios", "leaderboard"]:
            path = Path(args.output_dir) / subdir
            if path.exists():
                print(f"  - {path}")
    else:
        print("Data export failed")


def import_scenario_demo(data_manager, args):
    """Demonstrate scenario import functionality."""
    if not args.import_scenario:
        print("Error: No scenario file specified")
        return
        
    print(f"\n=== Scenario Import Demonstration ===")
    print(f"Importing scenario from: {args.import_scenario}")
    
    # Import scenario
    scenario_id = data_manager.import_scenario(args.import_scenario)
    
    if scenario_id:
        print(f"Scenario imported successfully with ID: {scenario_id}")
    else:
        print("Scenario import failed")


def create_scenarios_demo(data_manager, args):
    """Demonstrate creating advanced scenarios."""
    print(f"\n=== Create Scenarios Demonstration ===")
    
    # List existing scenarios
    existing = data_manager.storage.list_scenarios()
    print(f"Existing scenarios: {len(existing)}")
    for scenario in existing:
        print(f"  - {scenario.id}: {scenario.name}")
    
    # Create advanced scenarios
    print("\nCreating advanced scenarios...")
    created_ids = create_advanced_scenarios(data_manager)
    
    print(f"\nCreated {len(created_ids)} new scenarios:")
    for scenario_id in created_ids:
        scenario = data_manager.storage.get_scenario(scenario_id)
        if scenario:
            print(f"  - {scenario.id}: {scenario.name} (R0: {scenario.r0}, Difficulty: {scenario.difficulty})")


def validate_demo(data_manager, args):
    """Demonstrate storage validation functionality."""
    print(f"\n=== Storage Validation Demonstration ===")
    
    # Validate storage integrity
    results = data_manager.validate_storage_integrity()
    
    # Print validation results
    print("\nValidation Results:")
    
    # Players
    print(f"\nPlayers: {results['players']['count']} total")
    print(f"  - Valid: {results['players']['valid']}")
    print(f"  - Invalid: {results['players']['invalid']}")
    if results['players']['issues']:
        print("  - Issues:")
        for issue in results['players']['issues']:
            print(f"    * {issue}")
    
    # Attempts
    print(f"\nAttempts: {results['attempts']['count']} total")
    print(f"  - Valid: {results['attempts']['valid']}")
    print(f"  - Invalid: {results['attempts']['invalid']}")
    if results['attempts']['issues']:
        print("  - Issues:")
        for issue in results['attempts']['issues']:
            print(f"    * {issue}")
    
    # Scenarios
    print(f"\nScenarios: {results['scenarios']['count']} total")
    print(f"  - Valid: {results['scenarios']['valid']}")
    print(f"  - Invalid: {results['scenarios']['invalid']}")
    if results['scenarios']['issues']:
        print("  - Issues:")
        for issue in results['scenarios']['issues']:
            print(f"    * {issue}")
    
    # Leaderboard
    print(f"\nLeaderboard: {'Valid' if results['leaderboard']['valid'] else 'Invalid'}")
    if results['leaderboard']['issues']:
        print("  - Issues:")
        for issue in results['leaderboard']['issues']:
            print(f"    * {issue}")


def run_all_demos(data_manager, args):
    """Run all demos in sequence."""
    print("\n=== Running Complete Data Management Demo ===\n")
    
    # Create scenarios
    create_scenarios_demo(data_manager, args)
    
    # Validate storage
    validate_demo(data_manager, args)
    
    # Create backup
    backup_path = data_manager.backup_data(backup_dir="backups")
    print(f"\nBackup created at: {backup_path}")
    
    # Export data
    export_demo(data_manager, args)
    
    print("\nDemo completed! You now have:")
    print(f"1. Advanced scenarios in your competition system")
    print(f"2. A backup at {backup_path}")
    print(f"3. Exported data in {args.output_dir}")
    print(f"4. Storage validation results")


def main():
    """Main entry point for the demo."""
    # Parse command line arguments
    args = setup_argparse()
    
    # Create storage provider
    if args.enhanced:
        storage = EnhancedLocalStorageProvider(data_dir=args.data_dir)
        print(f"Using EnhancedLocalStorageProvider with data directory: {args.data_dir}")
    else:
        storage = LocalStorageProvider(data_dir=args.data_dir)
        print(f"Using LocalStorageProvider with data directory: {args.data_dir}")
    
    # Create data manager
    data_manager = DataManager(storage)
    
    # Run selected demo
    if args.backup:
        backup_demo(data_manager, args)
    elif args.restore:
        restore_demo(data_manager, args)
    elif args.export:
        export_demo(data_manager, args)
    elif args.import_scenario:
        import_scenario_demo(data_manager, args)
    elif args.create_scenarios:
        create_scenarios_demo(data_manager, args)
    elif args.validate:
        validate_demo(data_manager, args)
    elif args.demo_all:
        run_all_demos(data_manager, args)


if __name__ == "__main__":
    main() 