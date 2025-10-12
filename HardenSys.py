#!/usr/bin/env python3
"""
HardenSys CLI Tool
Command-line interface for running Windows security compliance checks.
"""

import sys
import json
import time
import argparse
import subprocess
import ctypes
from typing import Dict, List, Any
from datetime import datetime
import os

# Import all compliance functions
from windows_tasks import *


class ComplianceCLI:
    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None
        
    def load_tasks(self, json_file: str = "windows_tasks.json") -> List[Dict]:
        """Load compliance tasks from JSON file."""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {json_file} not found!")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {json_file}: {e}")
            sys.exit(1)
    
    def run_single_check(self, task: Dict) -> Dict:
        """Run a single compliance check."""
        script_key = task.get('script_key')
        if not script_key:
            return {
                'status': 'error',
                'message': 'No script_key found',
                'previous': 'Unknown',
                'current': 'Unknown'
            }
        
        # Get the function from windows_tasks module
        try:
            func = globals().get(script_key)
            if not func:
                return {
                    'status': 'error',
                    'message': f'Function {script_key} not found',
                    'previous': 'Unknown',
                    'current': 'Unknown'
                }
            
            # Run the function
            result = func()
            
            # Ensure result is a dictionary
            if isinstance(result, dict):
                return result
            else:
                return {
                    'status': 'success' if '✓' in str(result) else 'error',
                    'message': str(result),
                    'previous': 'Unknown',
                    'current': 'Unknown'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Exception: {str(e)}',
                'previous': 'Unknown',
                'current': 'Unknown'
            }
    
    def run_checks(self, tasks: List[Dict], filter_heading: str = None, filter_subheading: str = None, filter_title: str = None) -> List[Dict]:
        """Run compliance checks with optional filtering."""
        self.start_time = time.time()
        results = []
        
        print(f"Running {len(tasks)} compliance checks...")
        print("=" * 60)
        
        for i, task in enumerate(tasks, 1):
            # Apply filters
            if filter_heading and task.get('heading', '').lower() != filter_heading.lower():
                continue
            if filter_subheading and task.get('subheading', '').lower() != filter_subheading.lower():
                continue
            if filter_title and task.get('title', '').lower() != filter_title.lower():
                continue
            
            print(f"[{i}/{len(tasks)}] {task.get('title', 'Unknown')}")
            
            # Run the check
            result = self.run_single_check(task)
            
            # Add task info to result
            result.update({
                'heading': task.get('heading', ''),
                'subheading': task.get('subheading', ''),
                'title': task.get('title', ''),
                'details': task.get('details', ''),
                'script_key': task.get('script_key', ''),
                'timestamp': datetime.now().isoformat()
            })
            
            results.append(result)
            
            # Print result
            status_icon = "✓" if result['status'] == 'success' else "✗"
            print(f"  {status_icon} {result['message']}")
            print()
        
        self.end_time = time.time()
        self.results = results
        return results
    
    def generate_report(self, output_file: str = None, format: str = 'text') -> str:
        """Generate compliance report."""
        if not self.results:
            return "No results to report."
        
        # Calculate statistics
        total_checks = len(self.results)
        successful_checks = len([r for r in self.results if r['status'] == 'success'])
        failed_checks = total_checks - successful_checks
        duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        if format == 'json':
            report = {
                'summary': {
                    'total_checks': total_checks,
                    'successful_checks': successful_checks,
                    'failed_checks': failed_checks,
                    'success_rate': f"{(successful_checks/total_checks)*100:.1f}%" if total_checks > 0 else "0%",
                    'duration_seconds': round(duration, 2),
                    'timestamp': datetime.now().isoformat()
                },
                'results': self.results
            }
            report_text = json.dumps(report, indent=2)
        else:
            # Text format
            report_lines = [
                "Windows Security Compliance Report",
                "=" * 40,
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Duration: {duration:.2f} seconds",
                f"Total Checks: {total_checks}",
                f"Successful: {successful_checks}",
                f"Failed: {failed_checks}",
                f"Success Rate: {(successful_checks/total_checks)*100:.1f}%" if total_checks > 0 else "0%",
                "",
                "Detailed Results:",
                "=" * 40
            ]
            
            # Group by heading
            current_heading = None
            for result in self.results:
                if result['heading'] != current_heading:
                    current_heading = result['heading']
                    report_lines.append(f"\n{current_heading}")
                    report_lines.append("-" * len(current_heading))
                
                status_icon = "✓" if result['status'] == 'success' else "✗"
                report_lines.append(f"{status_icon} {result['title']}")
                report_lines.append(f"  Status: {result['status']}")
                report_lines.append(f"  Message: {result['message']}")
                if result.get('previous') and result.get('current'):
                    report_lines.append(f"  Previous: {result['previous']}")
                    report_lines.append(f"  Current: {result['current']}")
                report_lines.append("")
            
            report_text = "\n".join(report_lines)
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"Report saved to: {output_file}")
        
        return report_text
    
    def list_categories(self, tasks: List[Dict]):
        """List available categories and subcategories."""
        headings = {}
        for task in tasks:
            heading = task.get('heading', 'Unknown')
            subheading = task.get('subheading', 'Unknown')
            
            if heading not in headings:
                headings[heading] = set()
            headings[heading].add(subheading)
        
        print("Available Categories:")
        print("=" * 30)
        for heading, subheadings in sorted(headings.items()):
            print(f"\n{heading}:")
            for subheading in sorted(subheadings):
                count = len([t for t in tasks if t.get('heading') == heading and t.get('subheading') == subheading])
                print(f"  - {subheading} ({count} checks)")
    
    def show_info(self, tasks: List[Dict], search_term: str):
        """Show detailed information about a specific parameter, subheading, or heading."""
        search_term_lower = search_term.lower()
        matching_tasks = []
        
        # Find matching tasks
        for task in tasks:
            title = task.get('title', '').lower()
            subheading = task.get('subheading', '').lower()
            heading = task.get('heading', '').lower()
            
            if (search_term_lower in title or 
                search_term_lower in subheading or 
                search_term_lower in heading):
                matching_tasks.append(task)
        
        if not matching_tasks:
            print(f"No tasks found matching '{search_term}'")
            return
        
        print(f"Information for: '{search_term}'")
        print("=" * 50)
        
        # Group by heading and subheading
        grouped = {}
        for task in matching_tasks:
            heading = task.get('heading', 'Unknown')
            subheading = task.get('subheading', 'Unknown')
            
            if heading not in grouped:
                grouped[heading] = {}
            if subheading not in grouped[heading]:
                grouped[heading][subheading] = []
            
            grouped[heading][subheading].append(task)
        
        # Display grouped information
        for heading in sorted(grouped.keys()):
            print(f"\n[HEADING] {heading}")
            print("-" * (len(heading) + 10))
            
            for subheading in sorted(grouped[heading].keys()):
                tasks_in_subheading = grouped[heading][subheading]
                print(f"\n  [SUBCATEGORY] {subheading} ({len(tasks_in_subheading)} tasks)")
                
                for task in tasks_in_subheading:
                    title = task.get('title', 'Unknown')
                    details = task.get('details', 'No details available')
                    script_key = task.get('script_key', 'Unknown')
                    
                    print(f"\n    [TASK] {title}")
                    print(f"       Details: {details}")
                    print(f"       Script Key: {script_key}")
        
        print(f"\nTotal matches: {len(matching_tasks)}")
        
        # Show usage examples
        print("\nUsage Examples:")
        print("-" * 20)
        if len(matching_tasks) == 1:
            task = matching_tasks[0]
            print(f"python HardenSys.py --parameter \"{task.get('title', '')}\"")
        else:
            print(f"python HardenSys.py --heading \"{list(grouped.keys())[0]}\"")
            print(f"python HardenSys.py --subheading \"{list(grouped[list(grouped.keys())[0]].keys())[0]}\"")


def main():
    parser = argparse.ArgumentParser(
        description="Windows Security Compliance CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python HardenSys.py                               # Run all checks
  python HardenSys.py --heading "Account Policies"  # Run specific category
  python HardenSys.py --subheading "Password Policy"  # Run specific subcategory
  python HardenSys.py --parameter "Enforce password history"  # Run specific task by title
  python HardenSys.py --info "password"            # Show info about password-related tasks
  python HardenSys.py --output report.txt          # Save report to file
  python HardenSys.py --format json                # Generate JSON report
  python HardenSys.py --list                       # List available categories
        """
    )
    
    parser.add_argument('--json', default='windows_tasks.json', 
                       help='Path to tasks JSON file (default: windows_tasks.json)')
    parser.add_argument('--heading', 
                       help='Filter by heading (e.g., "Account Policies")')
    parser.add_argument('--subheading', 
                       help='Filter by subheading (e.g., "Password Policy")')
    parser.add_argument('--parameter', 
                       help='Filter by title name (e.g., "Enforce password history")')
    parser.add_argument('--info', 
                       help='Show detailed information about parameter/subheading/heading')
    parser.add_argument('--output', '-o', 
                       help='Output file for report')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Report format (default: text)')
    parser.add_argument('--list', action='store_true',
                       help='List available categories and exit')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Check if running as administrator
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if not is_admin:
            print("Warning: Not running as Administrator. Some checks may fail.")
            print("Consider running: python compliance_cli.py --help")
    except:
        pass  # Not on Windows or admin check failed
    
    cli = ComplianceCLI()
    
    # Load tasks
    tasks = cli.load_tasks(args.json)
    
    # List categories if requested
    if args.list:
        cli.list_categories(tasks)
        return
    
    # Show info if requested
    if args.info:
        cli.show_info(tasks, args.info)
        return
    
    # Run checks
    try:
        results = cli.run_checks(tasks, args.heading, args.subheading, args.parameter)
        
        # Generate and display report
        report = cli.generate_report(args.output, args.format)
        
        if not args.output:
            print("\n" + "=" * 60)
            print(report)
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

