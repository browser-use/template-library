"""
Scheduler that executes browser-use agents every N minutes.

This script automatically discovers and runs all Python scripts in the agents
directory as concurrent subprocesses on a configurable interval, logging each
execution with timestamps and displaying final results.

Configuration:
- SCHEDULER_INTERVAL_MINUTES: Time between executions (default: 5)
- SCHEDULER_SCRIPTS_DIR: Directory containing the scripts (default: agents)
- All other configuration is inherited from .env (API keys, profiles, etc.)

Auto-discovery:
- All .py files in the scripts directory are automatically discovered and run
- Files starting with _ or . are ignored (use to disable scripts)
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
INTERVAL_MINUTES = int(os.getenv("SCHEDULER_INTERVAL_MINUTES", 5))
INTERVAL_SECONDS = INTERVAL_MINUTES * 60

# Scripts directory
SCRIPTS_DIR = os.getenv("SCHEDULER_SCRIPTS_DIR", "agents")


def log_message(message: str, level: str = "INFO"):
    """Log a message with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}", flush=True)


async def run_script_subprocess(script_path: Path) -> tuple[str, bool, str]:
    """
    Run a Python script as a subprocess and read its result from a JSON file.

    Returns:
        tuple: (script_name, success, result_content)
    """
    import json

    script_name = script_path.name
    log_message(f"Starting {script_name}...", "INFO")

    # Define where the script will write its result
    result_file = Path("/tmp") / f"{script_name}_result.json"

    # Clean up any existing result file
    if result_file.exists():
        result_file.unlink()

    try:
        # Run the script as a subprocess (output goes to /dev/null, we read the file)
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            str(script_path),
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
            cwd=script_path.parent,
        )

        # Wait for completion
        returncode = await process.wait()

        # Read the result from the JSON file
        if result_file.exists():
            with open(result_file, "r") as f:
                result_data = json.load(f)

            success = result_data.get("success", False)
            result_content = result_data.get("result", "No result")

            if success:
                log_message(f"{script_name} completed successfully", "SUCCESS")
            else:
                log_message(f"{script_name} completed with no result", "WARNING")

            return (script_name, success, result_content)
        else:
            # File doesn't exist - script failed or didn't write output
            log_message(
                f"{script_name} failed - no result file found (exit code: {returncode})",
                "ERROR",
            )
            return (
                script_name,
                False,
                f"Script exited with code {returncode}, no result file generated",
            )

    except Exception as e:
        log_message(f"{script_name} execution failed: {str(e)}", "ERROR")
        import traceback

        error_trace = traceback.format_exc()
        log_message(error_trace, "ERROR")
        return (script_name, False, str(e))


async def run_all_scripts(scripts: list[Path]) -> dict:
    """
    Run all scripts concurrently as subprocesses and display their outputs.

    Returns:
        dict: Summary of execution results
    """
    log_message(f"Running {len(scripts)} script(s) concurrently...")

    start_time = datetime.now()

    # Run all scripts concurrently
    tasks = [run_script_subprocess(script) for script in scripts]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Display outputs from each script
    print("\n" + "=" * 80)
    log_message("Agent Results:", "INFO")
    print("=" * 80 + "\n")

    for result in results:
        if isinstance(result, tuple):
            script_name, success, output = result

            print(f"{'=' * 80}")
            print(f"  Script: {script_name}")
            print(f"  Status: {'✓ SUCCESS' if success else '✗ FAILED'}")
            print(f"{'=' * 80}")

            if output:
                print(output)
            else:
                print("(no output)")

            print()

    print("=" * 80)

    # Summarize results
    successful = sum(1 for r in results if isinstance(r, tuple) and r[1])
    failed = len(results) - successful

    summary = {
        "total": len(scripts),
        "successful": successful,
        "failed": failed,
        "duration": duration,
        "results": results,
    }

    log_message(
        f"Batch complete: {successful}/{len(scripts)} successful, "
        f"{failed} failed, duration: {duration:.2f}s",
        "SUCCESS" if failed == 0 else "WARNING",
    )

    return summary


def discover_scripts() -> list[Path]:
    """
    Automatically discover all Python scripts in the scripts directory.

    Ignores files starting with _ or . (for disabled/hidden scripts).

    Returns:
        list[Path]: List of discovered script paths
    """
    base_dir = Path(__file__).parent
    scripts_dir = base_dir / SCRIPTS_DIR

    # Check if scripts directory exists
    if not scripts_dir.exists():
        log_message(f"Error: Scripts directory not found: {scripts_dir}", "ERROR")
        log_message(f"Please create the directory: mkdir {SCRIPTS_DIR}", "ERROR")
        return []

    # Discover all .py files
    discovered = []
    for script_path in scripts_dir.glob("*.py"):
        # Ignore files starting with _ or .
        if script_path.name.startswith(("_", ".")):
            log_message(f"Skipping disabled script: {script_path.name}", "INFO")
            continue

        discovered.append(script_path)

    # Sort for consistent ordering
    discovered.sort(key=lambda p: p.name)

    return discovered


async def scheduler_loop():
    """Main scheduler loop that runs all discovered scripts every INTERVAL_MINUTES."""
    log_message(
        f"Scheduler started - will run scripts every {INTERVAL_MINUTES} minutes"
    )
    log_message("Press Ctrl+C to stop")

    # Discover scripts in the directory
    scripts = discover_scripts()

    if not scripts:
        log_message("Error: No scripts found to run!", "ERROR")
        return

    script_names = [s.name for s in scripts]
    log_message(f"Discovered {len(scripts)} script(s): {', '.join(script_names)}")

    execution_count = 0
    total_successful = 0
    total_failed = 0

    try:
        while True:
            execution_count += 1
            log_message("=" * 60)
            log_message(f"Execution batch #{execution_count} starting...")

            # Run all scripts
            summary = await run_all_scripts(scripts)

            total_successful += summary["successful"]
            total_failed += summary["failed"]

            # Wait for the next interval
            log_message(f"Next execution in {INTERVAL_MINUTES} minutes...")
            log_message("=" * 60)
            await asyncio.sleep(INTERVAL_SECONDS)

    except KeyboardInterrupt:
        log_message("=" * 60)
        log_message("Scheduler stopped by user", "INFO")
        log_message(f"Total batches: {execution_count}")
        log_message(f"Total successful runs: {total_successful}")
        log_message(f"Total failed runs: {total_failed}")
        log_message("=" * 60)
    except Exception as e:
        log_message(f"Scheduler error: {str(e)}", "ERROR")
        raise


def main():
    """Entry point for the scheduler."""
    log_message("=" * 60)
    log_message("Browser-Use Multi-Agent Scheduler")
    log_message(f"Interval: {INTERVAL_MINUTES} minutes")
    log_message(f"Scripts directory: {SCRIPTS_DIR}")
    log_message("=" * 60)

    # Run the scheduler
    asyncio.run(scheduler_loop())


if __name__ == "__main__":
    main()
