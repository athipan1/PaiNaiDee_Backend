"""
Data Update Scheduler and Management System

Handles scheduling and managing automated data updates from external sources.
Supports manual triggers, scheduled updates, and monitoring.
"""

import threading
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import json
from pathlib import Path

from src.services.external_data_service import ExternalDataService, UpdateResult


class UpdateFrequency(Enum):
    """Update frequency options"""
    MANUAL = "manual"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class UpdateStatus(Enum):
    """Update task status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledUpdate:
    """Configuration for a scheduled update task"""
    id: str
    source_name: str
    frequency: UpdateFrequency
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    parameters: Dict = None
    created_at: datetime = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class UpdateTask:
    """Individual update task"""
    id: str
    scheduled_update_id: Optional[str]
    source_name: str
    status: UpdateStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[UpdateResult] = None
    error_message: Optional[str] = None
    parameters: Dict = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


class DataUpdateScheduler:
    """Scheduler for managing external data updates"""

    def __init__(self, external_data_service: ExternalDataService):
        self.external_data_service = external_data_service
        self.logger = logging.getLogger(__name__)
        
        # Storage for schedules and tasks
        self.scheduled_updates: Dict[str, ScheduledUpdate] = {}
        self.update_tasks: Dict[str, UpdateTask] = {}
        
        # Scheduler state
        self.is_running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Configuration
        self.max_concurrent_tasks = 3
        self.running_tasks: Dict[str, threading.Thread] = {}
        
        # Load persisted schedules
        self._load_schedules()

    def add_scheduled_update(self, source_name: str, frequency: UpdateFrequency,
                           enabled: bool = True, parameters: Dict = None) -> str:
        """Add a new scheduled update"""
        schedule_id = f"{source_name}_{frequency.value}_{int(time.time())}"
        
        scheduled_update = ScheduledUpdate(
            id=schedule_id,
            source_name=source_name,
            frequency=frequency,
            enabled=enabled,
            parameters=parameters or {}
        )
        
        # Calculate next run time
        scheduled_update.next_run = self._calculate_next_run(frequency)
        
        self.scheduled_updates[schedule_id] = scheduled_update
        self._save_schedules()
        
        self.logger.info(f"Added scheduled update: {schedule_id}")
        return schedule_id

    def remove_scheduled_update(self, schedule_id: str) -> bool:
        """Remove a scheduled update"""
        if schedule_id in self.scheduled_updates:
            del self.scheduled_updates[schedule_id]
            self._save_schedules()
            self.logger.info(f"Removed scheduled update: {schedule_id}")
            return True
        return False

    def update_scheduled_update(self, schedule_id: str, **kwargs) -> bool:
        """Update a scheduled update configuration"""
        if schedule_id not in self.scheduled_updates:
            return False
        
        scheduled_update = self.scheduled_updates[schedule_id]
        
        if 'enabled' in kwargs:
            scheduled_update.enabled = kwargs['enabled']
        if 'frequency' in kwargs:
            scheduled_update.frequency = kwargs['frequency']
            scheduled_update.next_run = self._calculate_next_run(kwargs['frequency'])
        if 'parameters' in kwargs:
            scheduled_update.parameters.update(kwargs['parameters'])
        
        self._save_schedules()
        self.logger.info(f"Updated scheduled update: {schedule_id}")
        return True

    def trigger_manual_update(self, source_name: str, parameters: Dict = None) -> str:
        """Trigger a manual update immediately"""
        task_id = f"manual_{source_name}_{int(time.time())}"
        
        task = UpdateTask(
            id=task_id,
            scheduled_update_id=None,
            source_name=source_name,
            status=UpdateStatus.PENDING,
            parameters=parameters or {}
        )
        
        self.update_tasks[task_id] = task
        
        # Execute the task in a separate thread
        self._execute_task_async(task_id)
        
        return task_id

    def start_scheduler(self):
        """Start the scheduler daemon"""
        if self.is_running:
            self.logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        self.stop_event.clear()
        
        self.scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            name="DataUpdateScheduler",
            daemon=True
        )
        self.scheduler_thread.start()
        
        self.logger.info("Data update scheduler started")

    def stop_scheduler(self):
        """Stop the scheduler daemon"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.stop_event.set()
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=10)
        
        # Cancel running tasks
        for task_id in list(self.running_tasks.keys()):
            self._cancel_task(task_id)
        
        self.logger.info("Data update scheduler stopped")

    def _scheduler_loop(self):
        """Main scheduler loop"""
        while not self.stop_event.is_set():
            try:
                self._check_and_execute_scheduled_updates()
                self._cleanup_completed_tasks()
                
                # Sleep for 1 minute before next check
                if not self.stop_event.wait(60):
                    continue
                    
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)

    def _check_and_execute_scheduled_updates(self):
        """Check for due scheduled updates and execute them"""
        now = datetime.utcnow()
        
        for schedule_id, scheduled_update in self.scheduled_updates.items():
            if (scheduled_update.enabled and 
                scheduled_update.next_run and 
                scheduled_update.next_run <= now and
                len(self.running_tasks) < self.max_concurrent_tasks):
                
                # Create and execute task
                task_id = f"scheduled_{schedule_id}_{int(time.time())}"
                
                task = UpdateTask(
                    id=task_id,
                    scheduled_update_id=schedule_id,
                    source_name=scheduled_update.source_name,
                    status=UpdateStatus.PENDING,
                    parameters=scheduled_update.parameters.copy()
                )
                
                self.update_tasks[task_id] = task
                
                # Update schedule for next run
                scheduled_update.last_run = now
                scheduled_update.next_run = self._calculate_next_run(
                    scheduled_update.frequency, from_time=now
                )
                
                # Execute task
                self._execute_task_async(task_id)
                
                self.logger.info(f"Executing scheduled update: {schedule_id}")

    def _execute_task_async(self, task_id: str):
        """Execute update task in a separate thread"""
        if task_id not in self.update_tasks:
            return
        
        task_thread = threading.Thread(
            target=self._execute_task,
            args=(task_id,),
            name=f"UpdateTask-{task_id}",
            daemon=True
        )
        
        self.running_tasks[task_id] = task_thread
        task_thread.start()

    def _execute_task(self, task_id: str):
        """Execute an update task"""
        if task_id not in self.update_tasks:
            return
        
        task = self.update_tasks[task_id]
        
        try:
            # Update task status
            task.status = UpdateStatus.RUNNING
            task.started_at = datetime.utcnow()
            
            self.logger.info(f"Starting update task: {task_id} for source: {task.source_name}")
            
            # Execute the update
            result = self.external_data_service.update_attractions_from_source(
                task.source_name, **task.parameters
            )
            
            # Update task with result
            task.result = result
            task.status = UpdateStatus.COMPLETED if result.success else UpdateStatus.FAILED
            task.completed_at = datetime.utcnow()
            
            if not result.success:
                task.error_message = "; ".join(result.errors)
            
            self.logger.info(f"Completed update task: {task_id}")
            
        except Exception as e:
            # Handle task failure
            task.status = UpdateStatus.FAILED
            task.completed_at = datetime.utcnow()
            task.error_message = str(e)
            
            self.logger.error(f"Failed update task: {task_id}: {e}")
            
        finally:
            # Remove from running tasks
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]

    def _cancel_task(self, task_id: str):
        """Cancel a running task"""
        if task_id in self.update_tasks:
            task = self.update_tasks[task_id]
            if task.status in [UpdateStatus.PENDING, UpdateStatus.RUNNING]:
                task.status = UpdateStatus.CANCELLED
                task.completed_at = datetime.utcnow()
        
        if task_id in self.running_tasks:
            # Note: We can't actually stop a running thread in Python,
            # but we mark it as cancelled
            del self.running_tasks[task_id]

    def _cleanup_completed_tasks(self):
        """Clean up old completed tasks"""
        # Keep only last 100 tasks
        if len(self.update_tasks) > 100:
            completed_tasks = [
                (task_id, task) for task_id, task in self.update_tasks.items()
                if task.status in [UpdateStatus.COMPLETED, UpdateStatus.FAILED, UpdateStatus.CANCELLED]
            ]
            
            # Sort by completion time and keep only recent ones
            completed_tasks.sort(key=lambda x: x[1].completed_at or datetime.min)
            
            # Remove oldest tasks
            for task_id, _ in completed_tasks[:-80]:  # Keep last 80 completed tasks
                del self.update_tasks[task_id]

    def _calculate_next_run(self, frequency: UpdateFrequency, 
                          from_time: datetime = None) -> datetime:
        """Calculate next run time based on frequency"""
        if from_time is None:
            from_time = datetime.utcnow()
        
        if frequency == UpdateFrequency.HOURLY:
            return from_time + timedelta(hours=1)
        elif frequency == UpdateFrequency.DAILY:
            return from_time + timedelta(days=1)
        elif frequency == UpdateFrequency.WEEKLY:
            return from_time + timedelta(weeks=1)
        elif frequency == UpdateFrequency.MONTHLY:
            # Approximate monthly (30 days)
            return from_time + timedelta(days=30)
        else:
            # Manual updates don't have next run time
            return None

    def get_scheduled_updates(self) -> List[Dict]:
        """Get all scheduled updates"""
        return [asdict(update) for update in self.scheduled_updates.values()]

    def get_update_tasks(self, limit: int = 50, 
                        status_filter: Optional[UpdateStatus] = None) -> List[Dict]:
        """Get update tasks with optional filtering"""
        tasks = list(self.update_tasks.values())
        
        if status_filter:
            tasks = [task for task in tasks if task.status == status_filter]
        
        # Sort by start time (most recent first)
        tasks.sort(key=lambda x: x.started_at or datetime.min, reverse=True)
        
        # Convert to dict and limit results
        return [self._task_to_dict(task) for task in tasks[:limit]]

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get status of a specific task"""
        if task_id in self.update_tasks:
            return self._task_to_dict(self.update_tasks[task_id])
        return None

    def _task_to_dict(self, task: UpdateTask) -> Dict:
        """Convert UpdateTask to dictionary"""
        result = {
            'id': task.id,
            'scheduled_update_id': task.scheduled_update_id,
            'source_name': task.source_name,
            'status': task.status.value,
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'error_message': task.error_message,
            'parameters': task.parameters
        }
        
        # Convert result object
        if task.result:
            result['result'] = {
                'success': task.result.success,
                'total_processed': task.result.total_processed,
                'new_created': task.result.new_created,
                'existing_updated': task.result.existing_updated,
                'errors': task.result.errors,
                'source': task.result.source,
                'timestamp': task.result.timestamp.isoformat() if task.result.timestamp else None
            }
        else:
            result['result'] = None
        
        return result

    def get_scheduler_status(self) -> Dict:
        """Get overall scheduler status"""
        return {
            'is_running': self.is_running,
            'active_schedules': len([s for s in self.scheduled_updates.values() if s.enabled]),
            'total_schedules': len(self.scheduled_updates),
            'running_tasks': len(self.running_tasks),
            'pending_tasks': len([t for t in self.update_tasks.values() 
                                if t.status == UpdateStatus.PENDING]),
            'max_concurrent_tasks': self.max_concurrent_tasks
        }

    def _save_schedules(self):
        """Save scheduled updates to file"""
        try:
            schedules_data = {}
            for schedule_id, schedule in self.scheduled_updates.items():
                schedule_dict = asdict(schedule)
                # Convert datetime objects to ISO strings
                if schedule_dict['last_run']:
                    schedule_dict['last_run'] = schedule.last_run.isoformat()
                if schedule_dict['next_run']:
                    schedule_dict['next_run'] = schedule.next_run.isoformat()
                if schedule_dict['created_at']:
                    schedule_dict['created_at'] = schedule.created_at.isoformat()
                # Convert enum to value
                schedule_dict['frequency'] = schedule.frequency.value
                
                schedules_data[schedule_id] = schedule_dict
            
            # Save to file
            schedules_file = Path('instance/scheduled_updates.json')
            schedules_file.parent.mkdir(exist_ok=True)
            
            with open(schedules_file, 'w') as f:
                json.dump(schedules_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving schedules: {e}")

    def _load_schedules(self):
        """Load scheduled updates from file"""
        try:
            schedules_file = Path('instance/scheduled_updates.json')
            
            if not schedules_file.exists():
                return
            
            with open(schedules_file, 'r') as f:
                schedules_data = json.load(f)
            
            for schedule_id, schedule_dict in schedules_data.items():
                # Convert ISO strings back to datetime objects
                if schedule_dict.get('last_run'):
                    schedule_dict['last_run'] = datetime.fromisoformat(
                        schedule_dict['last_run']
                    )
                if schedule_dict.get('next_run'):
                    schedule_dict['next_run'] = datetime.fromisoformat(
                        schedule_dict['next_run']
                    )
                if schedule_dict.get('created_at'):
                    schedule_dict['created_at'] = datetime.fromisoformat(
                        schedule_dict['created_at']
                    )
                
                # Convert string back to enum
                schedule_dict['frequency'] = UpdateFrequency(schedule_dict['frequency'])
                
                self.scheduled_updates[schedule_id] = ScheduledUpdate(**schedule_dict)
                
            self.logger.info(f"Loaded {len(self.scheduled_updates)} scheduled updates")
            
        except Exception as e:
            self.logger.error(f"Error loading schedules: {e}")


# Global scheduler instance
_scheduler_instance: Optional[DataUpdateScheduler] = None


def get_scheduler() -> DataUpdateScheduler:
    """Get the global scheduler instance"""
    global _scheduler_instance
    
    if _scheduler_instance is None:
        from src.services.external_data_service import ExternalDataService
        external_service = ExternalDataService()
        _scheduler_instance = DataUpdateScheduler(external_service)
    
    return _scheduler_instance


def initialize_scheduler():
    """Initialize and start the scheduler"""
    scheduler = get_scheduler()
    scheduler.start_scheduler()
    return scheduler