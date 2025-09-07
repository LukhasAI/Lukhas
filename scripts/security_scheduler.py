#!/usr/bin/env python3
from typing import List
"""
🕒 LUKHAS Security Task Scheduler
================================
Schedule security fixes to run automatically at specified times.
Handles both dependency vulnerabilities and code security issues.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

import json
import os
import subprocess
from datetime import datetime, timedelta, timezone  # ΛTAG: utc
from pathlib import Path

import click


class SecurityTaskScheduler:
    """Scheduler for automated security tasks"""

    def __init__(self):
        self.schedule_file = Path("security-schedule.json")
        self.log_file = Path("security-scheduler.log")

    def log(self, message: str):
        """Log message with timestamp"""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")  # ΛTAG: utc
        log_msg = f"[{timestamp}] {message}\n"

        # Print to console
        click.echo(log_msg.strip())

        # Write to log file
        with open(self.log_file, "a") as f:
            f.write(log_msg)

    def load_schedule(self) -> dict:
        """Load existing schedule"""
        if self.schedule_file.exists():
            with open(self.schedule_file) as f:
                return json.load(f)
        return {"tasks": [], "last_run": None}

    def save_schedule(self, schedule: dict):
        """Save schedule to file"""
        with open(self.schedule_file, "w") as f:
            json.dump(schedule, f, indent=2)

    def schedule_task(self, task_type: str, run_time: str, description: str = ""):
        """Schedule a security task"""
        schedule = self.load_schedule()

        # Parse run time
        try:
            if ":" in run_time:
                # Time format like "14:30" (today) or "2025-08-22 14:30"
                if "-" in run_time:
                    scheduled_time = datetime.strptime(run_time, "%Y-%m-%d %H:%M").replace(
                        tzinfo=timezone.utc
                    )  # ΛTAG: utc
                else:
                    today = datetime.now(timezone.utc).date()  # ΛTAG: utc
                    time_part = datetime.strptime(run_time, "%H:%M").time()
                    scheduled_time = datetime.combine(today, time_part, tzinfo=timezone.utc)

                    # If time is in the past, schedule for tomorrow
                    if scheduled_time <= datetime.now(timezone.utc):  # ΛTAG: utc
                        scheduled_time += timedelta(days=1)
            else:
                # Relative time like "+2h", "+30m"
                if run_time.startswith("+"):
                    run_time = run_time[1:]

                if run_time.endswith("h"):
                    hours = int(run_time[:-1])
                    scheduled_time = datetime.now(timezone.utc) + timedelta(hours=hours)  # ΛTAG: utc
                elif run_time.endswith("m"):
                    minutes = int(run_time[:-1])
                    scheduled_time = datetime.now(timezone.utc) + timedelta(minutes=minutes)  # ΛTAG: utc
                else:
                    raise ValueError("Invalid time format")

        except ValueError:
            click.echo(f"❌ Invalid time format: {run_time}")
            click.echo("Examples: '14:30', '+2h', '+30m', '2025-08-22 20:00'")
            return False

        # Create task
        task = {
            "id": f"security_{int(datetime.now(timezone.utc).timestamp()}",  # ΛTAG: utc
            "type": task_type,
            "scheduled_time": scheduled_time.isoformat(),
            "description": description or f"Scheduled {task_type}",
            "status": "pending",
            "created": datetime.now(timezone.utc).isoformat(),  # ΛTAG: utc
        }

        schedule["tasks"].append(task)
        self.save_schedule(schedule)

        self.log(f"✅ Scheduled {task_type} for {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")
        click.echo(f"Task ID: {task['id']}")
        return True

    def list_tasks(self):
        """List all scheduled tasks"""
        schedule = self.load_schedule()
        tasks = schedule.get("tasks", [])

        if not tasks:
            click.echo("📅 No scheduled security tasks")
            return

        click.echo("📅 SCHEDULED SECURITY TASKS:")
        click.echo("=" * 50)

        for task in tasks:
            scheduled_time = datetime.fromisoformat(task["scheduled_time"]).astimezone(timezone.utc)  # ΛTAG: utc
            status_emoji = {
                "pending": "⏳",
                "running": "🔄",
                "completed": "✅",
                "failed": "❌",
            }.get(task["status"], "❓")

            click.echo(f"{status_emoji} {task['id']}")
            click.echo(f"   Type: {task['type']}")
            click.echo(f"   Time: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")
            click.echo(f"   Description: {task['description']}")
            click.echo(f"   Status: {task['status']}")
            click.echo()

    def run_pending_tasks(self):
        """Check and run any pending tasks"""
        schedule = self.load_schedule()
        tasks = schedule.get("tasks", [])
        now = datetime.now(timezone.utc)  # ΛTAG: utc

        executed_tasks = 0

        for task in tasks:
            if task["status"] != "pending":
                continue

            scheduled_time = datetime.fromisoformat(task["scheduled_time"]).astimezone(timezone.utc)  # ΛTAG: utc

            if scheduled_time <= now:
                self.log(f"🚀 Executing task: {task['id']} ({task['type']})")
                task["status"] = "running"
                task["started"] = now.isoformat()
                self.save_schedule(schedule)

                # Execute the task
                success = self.execute_task(task)

                # Update status
                task["status"] = "completed" if success else "failed"
                task["finished"] = datetime.now(timezone.utc).isoformat()  # ΛTAG: utc
                self.save_schedule(schedule)

                executed_tasks += 1

        if executed_tasks > 0:
            self.log(f"✅ Executed {executed_tasks} pending task(s)")

        return executed_tasks

    def execute_task(self, task: dict) -> bool:
        """Execute a specific security task"""
        task_type = task["type"]

        try:
            if task_type == "fix-vulnerabilities":
                result = subprocess.run(
                    ["make", "security-fix-vulnerabilities"],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

            elif task_type == "fix-issues":
                # Skip Ollama-dependent tasks for now
                self.log("⚠️ Skipping Ollama-dependent security issue fixes (Ollama not available)")
                return True

            elif task_type == "fix-all":
                # Run vulnerabilities fix only (skip issues due to Ollama)
                result = subprocess.run(
                    ["make", "security-fix-vulnerabilities"],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

            elif task_type == "comprehensive-scan":
                result = subprocess.run(
                    ["make", "security-comprehensive-scan"],
                    capture_output=True,
                    text=True,
                    timeout=600,
                )

            else:
                self.log(f"❌ Unknown task type: {task_type}")
                return False

            if result.returncode == 0:
                self.log(f"✅ Task {task['id']} completed successfully")
                return True
            else:
                self.log(f"❌ Task {task['id']} failed with exit code {result.returncode}")
                self.log(f"Error output: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.log(f"⏰ Task {task['id']} timed out")
            return False
        except Exception as e:
            self.log(f"❌ Task {task['id']} failed with exception: {e}")
            return False

    def cancel_task(self, task_id: str):
        """Cancel a scheduled task"""
        schedule = self.load_schedule()
        tasks = schedule.get("tasks", [])

        for task in tasks:
            if task["id"] == task_id:
                if task["status"] == "pending":
                    task["status"] = "cancelled"
                    task["cancelled"] = datetime.now(timezone.utc).isoformat()  # ΛTAG: utc
                    self.save_schedule(schedule)
                    self.log(f"❌ Cancelled task: {task_id}")
                    click.echo(f"✅ Task {task_id} cancelled")
                    return True
                else:
                    click.echo(f"⚠️ Cannot cancel task {task_id} (status: {task['status']})")
                    return False

        click.echo(f"❌ Task {task_id} not found")
        return False

    def setup_cron_job(self):
        """Set up a cron job to check for pending tasks every 15 minutes"""
        cron_command = f"*/15 * * * * cd {os.getcwd()} && python3 scripts/security_scheduler.py run-pending >> security-scheduler.log 2>&1"

        click.echo("🕒 Setting up automated task runner...")
        click.echo("Add this line to your crontab (run 'crontab -e'):")
        click.echo()
        click.echo(f"  {cron_command}")
        click.echo()
        click.echo("Or run this command to add it automatically:")
        click.echo(f"  (crontab -l 2>/dev/null; echo '{cron_command}') | crontab -")


@click.group()
def cli():
    """LUKHAS Security Task Scheduler"""
    pass


@cli.command()
@click.argument(
    "task_type",
    type=click.Choice(["fix-vulnerabilities", "fix-issues", "fix-all", "comprehensive-scan"]),
)
@click.argument("time")
@click.option("--description", "-d", help="Task description")
def schedule(task_type, time, description):
    """Schedule a security task

    Examples:
        schedule fix-all +3h
        schedule fix-vulnerabilities 20:00
        schedule comprehensive-scan "2025-08-22 14:30"
    """
    scheduler = SecurityTaskScheduler()
    scheduler.schedule_task(task_type, time, description)


@cli.command()
def list():
    """List all scheduled tasks"""
    scheduler = SecurityTaskScheduler()
    scheduler.list_tasks()


@cli.command()
def run_pending():
    """Run any pending tasks (used by cron)"""
    scheduler = SecurityTaskScheduler()
    scheduler.run_pending_tasks()


@cli.command()
@click.argument("task_id")
def cancel(task_id):
    """Cancel a scheduled task"""
    scheduler = SecurityTaskScheduler()
    scheduler.cancel_task(task_id)


@cli.command()
def setup_cron():
    """Set up automated task runner via cron"""
    scheduler = SecurityTaskScheduler()
    scheduler.setup_cron_job()


@cli.command()
def status():
    """Show scheduler status and recommendations"""
    scheduler = SecurityTaskScheduler()

    # Check if we have pending vulnerabilities
    if Path("reports/security/bandit.json").exists():
        click.echo("📊 SECURITY STATUS:")

        # Count issues from bandit report
        try:
            with open("reports/security/bandit.json") as f:
                data = json.load(f)
                total_issues = len(data.get("results", []))
                high_issues = len([i for i in data["results"] if i.get("issue_severity") == "HIGH"])
                medium_issues = len([i for i in data["results"] if i.get("issue_severity") == "MEDIUM"])

            click.echo(f"🔥 HIGH severity: {high_issues} issues")
            click.echo(f"⚠️  MEDIUM severity: {medium_issues} issues")
            click.echo(f"📊 Total issues: {total_issues}")

            if high_issues + medium_issues > 0:
                click.echo("\n💡 RECOMMENDATIONS:")
                click.echo("   Schedule security fixes when Ollama is available:")
                click.echo("   python3 scripts/security_scheduler.py schedule fix-all +3h")

        except Exception as e:
            click.echo(f"❌ Could not read security report: {e}")

    # Show current schedule
    click.echo("\n📅 CURRENT SCHEDULE:")
    scheduler.list_tasks()


if __name__ == "__main__":
    cli()