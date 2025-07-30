#!/usr/bin/env python3
"""
External Data Management CLI

Command-line interface for managing external data integration.
Provides commands for triggering updates, managing schedules, and monitoring status.
"""

import click
import os
import sys
import time
from datetime import datetime
import json

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import create_app
from src.services.external_data_service import ExternalDataService
from src.services.data_update_scheduler import (
    get_scheduler, UpdateFrequency, UpdateStatus, initialize_scheduler
)


@click.group()
@click.pass_context
def cli(ctx):
    """External Data Management CLI for PaiNaiDee Backend"""
    ctx.ensure_object(dict)
    
    # Initialize Flask app context
    config_name = os.getenv("FLASK_ENV", "default")
    app = create_app(config_name)
    ctx.obj['app'] = app
    ctx.obj['app_context'] = app.app_context()
    ctx.obj['app_context'].push()


@cli.command()
@click.pass_context
def sources(ctx):
    """List all external data sources and their status"""
    click.echo("📊 External Data Sources Status:\n")
    
    service = ExternalDataService()
    sources_status = service.get_source_status()
    
    for source_name, status in sources_status.items():
        status_icon = "✅" if status['enabled'] else "❌"
        config_icon = "🔑" if status['configured'] else "⚠️"
        
        click.echo(f"{status_icon} {source_name}")
        click.echo(f"   Enabled: {status['enabled']}")
        click.echo(f"   Configured: {config_icon} {status['configured']}")
        click.echo(f"   Rate Limit: {status['rate_limit']} req/sec")
        if status['last_request']:
            last_req = datetime.fromtimestamp(status['last_request'])
            click.echo(f"   Last Request: {last_req.strftime('%Y-%m-%d %H:%M:%S')}")
        click.echo()


@cli.command()
@click.argument('source_name')
@click.option('--api-key', help='API key for the source')
@click.option('--enable/--disable', default=True, help='Enable or disable the source')
@click.pass_context
def configure(ctx, source_name, api_key, enable):
    """Configure an external data source"""
    service = ExternalDataService()
    
    try:
        service.configure_source(
            source_name=source_name,
            api_key=api_key,
            enabled=enable
        )
        
        status_text = "enabled" if enable else "disabled"
        click.echo(f"✅ Source '{source_name}' configured and {status_text}")
        
        if api_key:
            click.echo(f"🔑 API key set for '{source_name}'")
            
    except Exception as e:
        click.echo(f"❌ Error configuring source '{source_name}': {e}", err=True)


@cli.command()
@click.argument('source_name')
@click.option('--province', help='Filter by province')
@click.option('--query', help='Search query')
@click.option('--location', help='Location filter')
@click.pass_context
def update(ctx, source_name, province, query, location):
    """Trigger manual update from a specific source"""
    click.echo(f"🔄 Triggering manual update from '{source_name}'...")
    
    service = ExternalDataService()
    
    # Prepare parameters
    parameters = {}
    if province:
        parameters['province'] = province
    if query:
        parameters['query'] = query
    if location:
        parameters['location'] = location
    
    try:
        result = service.update_attractions_from_source(source_name, **parameters)
        
        if result.success:
            click.echo(f"✅ Update completed successfully!")
            click.echo(f"   Total processed: {result.total_processed}")
            click.echo(f"   New attractions created: {result.new_created}")
            click.echo(f"   Existing attractions updated: {result.existing_updated}")
            
            if result.errors:
                click.echo(f"⚠️  Errors encountered: {len(result.errors)}")
                for error in result.errors[:5]:  # Show first 5 errors
                    click.echo(f"     - {error}")
                if len(result.errors) > 5:
                    click.echo(f"     ... and {len(result.errors) - 5} more errors")
        else:
            click.echo(f"❌ Update failed!")
            for error in result.errors:
                click.echo(f"   Error: {error}")
                
    except Exception as e:
        click.echo(f"❌ Error during update: {e}", err=True)


@cli.command()
@click.option('--province', help='Filter by province')
@click.pass_context
def update_all(ctx, province):
    """Trigger updates from all enabled sources"""
    click.echo("🔄 Triggering updates from all enabled sources...")
    
    service = ExternalDataService()
    
    parameters = {}
    if province:
        parameters['province'] = province
    
    try:
        results = service.update_all_sources(**parameters)
        
        total_processed = 0
        total_created = 0
        total_updated = 0
        total_errors = 0
        
        for result in results:
            click.echo(f"\n📊 Results from '{result.source}':")
            click.echo(f"   Processed: {result.total_processed}")
            click.echo(f"   Created: {result.new_created}")
            click.echo(f"   Updated: {result.existing_updated}")
            click.echo(f"   Errors: {len(result.errors)}")
            
            total_processed += result.total_processed
            total_created += result.new_created
            total_updated += result.existing_updated
            total_errors += len(result.errors)
        
        click.echo(f"\n🎯 Summary:")
        click.echo(f"   Sources updated: {len(results)}")
        click.echo(f"   Total processed: {total_processed}")
        click.echo(f"   Total created: {total_created}")
        click.echo(f"   Total updated: {total_updated}")
        click.echo(f"   Total errors: {total_errors}")
        
    except Exception as e:
        click.echo(f"❌ Error during update: {e}", err=True)


@cli.command()
@click.pass_context
def schedules(ctx):
    """List all scheduled updates"""
    scheduler = get_scheduler()
    schedules = scheduler.get_scheduled_updates()
    
    if not schedules:
        click.echo("📅 No scheduled updates configured")
        return
    
    click.echo("📅 Scheduled Updates:\n")
    
    for schedule in schedules:
        status_icon = "✅" if schedule['enabled'] else "❌"
        
        click.echo(f"{status_icon} {schedule['id']}")
        click.echo(f"   Source: {schedule['source_name']}")
        click.echo(f"   Frequency: {schedule['frequency']}")
        click.echo(f"   Enabled: {schedule['enabled']}")
        
        if schedule['last_run']:
            last_run = datetime.fromisoformat(schedule['last_run'])
            click.echo(f"   Last Run: {last_run.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if schedule['next_run']:
            next_run = datetime.fromisoformat(schedule['next_run'])
            click.echo(f"   Next Run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if schedule.get('parameters'):
            click.echo(f"   Parameters: {json.dumps(schedule['parameters'], indent=6)}")
        
        click.echo()


@cli.command()
@click.argument('source_name')
@click.option('--frequency', type=click.Choice(['hourly', 'daily', 'weekly', 'monthly']), 
              required=True, help='Update frequency')
@click.option('--enable/--disable', default=True, help='Enable the schedule')
@click.option('--province', help='Province parameter')
@click.pass_context
def schedule_add(ctx, source_name, frequency, enable, province):
    """Add a new scheduled update"""
    scheduler = get_scheduler()
    
    parameters = {}
    if province:
        parameters['province'] = province
    
    try:
        frequency_enum = UpdateFrequency(frequency)
        schedule_id = scheduler.add_scheduled_update(
            source_name=source_name,
            frequency=frequency_enum,
            enabled=enable,
            parameters=parameters
        )
        
        click.echo(f"✅ Scheduled update created: {schedule_id}")
        click.echo(f"   Source: {source_name}")
        click.echo(f"   Frequency: {frequency}")
        click.echo(f"   Enabled: {enable}")
        
    except Exception as e:
        click.echo(f"❌ Error creating schedule: {e}", err=True)


@cli.command()
@click.argument('schedule_id')
@click.pass_context
def schedule_remove(ctx, schedule_id):
    """Remove a scheduled update"""
    scheduler = get_scheduler()
    
    try:
        success = scheduler.remove_scheduled_update(schedule_id)
        
        if success:
            click.echo(f"✅ Scheduled update removed: {schedule_id}")
        else:
            click.echo(f"❌ Schedule not found: {schedule_id}")
            
    except Exception as e:
        click.echo(f"❌ Error removing schedule: {e}", err=True)


@cli.command()
@click.option('--limit', default=20, help='Number of tasks to show')
@click.option('--status', type=click.Choice(['pending', 'running', 'completed', 'failed', 'cancelled']),
              help='Filter by status')
@click.pass_context
def tasks(ctx, limit, status):
    """List update tasks"""
    scheduler = get_scheduler()
    
    status_filter = None
    if status:
        status_filter = UpdateStatus(status)
    
    tasks = scheduler.get_update_tasks(limit=limit, status_filter=status_filter)
    
    if not tasks:
        click.echo("📋 No tasks found")
        return
    
    click.echo(f"📋 Update Tasks (showing {len(tasks)}):\n")
    
    for task in tasks:
        status_icon = {
            'pending': '⏳',
            'running': '🔄',
            'completed': '✅',
            'failed': '❌',
            'cancelled': '🚫'
        }.get(task['status'], '❓')
        
        click.echo(f"{status_icon} {task['id']}")
        click.echo(f"   Source: {task['source_name']}")
        click.echo(f"   Status: {task['status']}")
        
        if task['started_at']:
            started = datetime.fromisoformat(task['started_at'])
            click.echo(f"   Started: {started.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if task['completed_at']:
            completed = datetime.fromisoformat(task['completed_at'])
            click.echo(f"   Completed: {completed.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if task.get('result'):
            result = task['result']
            click.echo(f"   Results: {result['total_processed']} processed, "
                      f"{result['new_created']} created, {result['existing_updated']} updated")
        
        if task.get('error_message'):
            click.echo(f"   Error: {task['error_message']}")
        
        click.echo()


@cli.command()
@click.pass_context
def status(ctx):
    """Show system status"""
    click.echo("🏥 System Status:\n")
    
    # Scheduler status
    scheduler = get_scheduler()
    scheduler_status = scheduler.get_scheduler_status()
    
    click.echo("📊 Scheduler:")
    click.echo(f"   Running: {'✅' if scheduler_status['is_running'] else '❌'}")
    click.echo(f"   Active Schedules: {scheduler_status['active_schedules']}")
    click.echo(f"   Total Schedules: {scheduler_status['total_schedules']}")
    click.echo(f"   Running Tasks: {scheduler_status['running_tasks']}")
    click.echo(f"   Pending Tasks: {scheduler_status['pending_tasks']}")
    click.echo()
    
    # Data sources status
    service = ExternalDataService()
    sources_status = service.get_source_status()
    
    click.echo("🔌 Data Sources:")
    enabled_sources = sum(1 for s in sources_status.values() if s['enabled'])
    configured_sources = sum(1 for s in sources_status.values() if s['configured'])
    
    click.echo(f"   Total Sources: {len(sources_status)}")
    click.echo(f"   Enabled: {enabled_sources}")
    click.echo(f"   Configured: {configured_sources}")
    click.echo()
    
    # Database stats (if available)
    try:
        from src.models import Attraction, db
        total_attractions = Attraction.query.count()
        
        attractions_with_images = Attraction.query.filter(
            Attraction.main_image_url.isnot(None),
            Attraction.main_image_url != ''
        ).count()
        
        click.echo("🏛️ Database:")
        click.echo(f"   Total Attractions: {total_attractions}")
        click.echo(f"   With Images: {attractions_with_images}")
        
    except Exception as e:
        click.echo("🏛️ Database: ❌ Not available")


@cli.command()
@click.pass_context
def coverage(ctx):
    """Show province coverage statistics"""
    click.echo("🗺️ Province Coverage Analysis:\n")
    
    try:
        from src.models import Attraction, db
        from sqlalchemy import func
        
        # Thai provinces
        thai_provinces = [
            'กรุงเทพมหานคร', 'กระบี่', 'กาญจนบุรี', 'กาฬสินธุ์', 'กำแพงเพชร',
            'ขอนแก่น', 'จันทบุรี', 'ฉะเชิงเทรา', 'ชลบุรี', 'ชัยนาท', 'ชัยภูมิ',
            'ชุมพร', 'เชียงราย', 'เชียงใหม่', 'ตรัง', 'ตราด', 'ตาก', 'นครนายก',
            'นครปฐม', 'นครพนม', 'นครราชสีมา', 'นครศรีธรรมราช', 'นครสวรรค์',
            'นนทบุรี', 'นราธิวาส', 'น่าน', 'บึงกาฬ', 'บุรีรัมย์', 'ปทุมธานี',
            'ประจวบคีรีขันธ์', 'ปราจีนบุรี', 'ปัตตานี', 'พระนครศรีอยุธยา',
            'พังงา', 'พัทลุง', 'พิจิตร', 'พิษณุโลก', 'เพชรบุรี', 'เพชรบูรณ์',
            'แพร่', 'ภูเก็ต', 'มหาสารคาม', 'มุกดาหาร', 'แม่ฮ่องสอน', 'ยโสธร',
            'ยะลา', 'ร้อยเอ็ด', 'ระนอง', 'ระยอง', 'ราชบุรี', 'ลพบุรี', 'ลำปาง',
            'ลำพูน', 'เลย', 'ศรีสะเกษ', 'สกลนคร', 'สงขลา', 'สตูล', 'สมุทรปราการ',
            'สมุทรสงคราม', 'สมุทรสาคร', 'สระแก้ว', 'สระบุรี', 'สิงห์บุรี',
            'สุโขทัย', 'สุพรรณบุรี', 'สุราษฎร์ธานี', 'สุรินทร์', 'หนองคาย',
            'หนองบัวลำภู', 'อ่างทอง', 'อำนาจเจริญ', 'อุดรธานี', 'อุตรดิตถ์',
            'อุทัยธานี', 'อุบลราชธานี'
        ]
        
        # Get province counts
        results = db.session.query(
            Attraction.province,
            func.count(Attraction.id).label('count')
        ).group_by(Attraction.province).all()
        
        province_counts = {result.province: result.count for result in results if result.province}
        
        covered_provinces = 0
        total_attractions = 0
        
        for province in thai_provinces:
            count = province_counts.get(province, 0)
            if count > 0:
                covered_provinces += 1
                total_attractions += count
                status = "✅"
            else:
                status = "❌"
            
            click.echo(f"{status} {province}: {count} attractions")
        
        coverage_percentage = (covered_provinces / len(thai_provinces)) * 100
        
        click.echo(f"\n📊 Summary:")
        click.echo(f"   Total Provinces: {len(thai_provinces)}")
        click.echo(f"   Covered Provinces: {covered_provinces}")
        click.echo(f"   Coverage: {coverage_percentage:.1f}%")
        click.echo(f"   Total Attractions: {total_attractions}")
        
    except Exception as e:
        click.echo(f"❌ Error getting coverage data: {e}")


@cli.command()
@click.pass_context
def start_scheduler(ctx):
    """Start the data update scheduler"""
    click.echo("🚀 Starting data update scheduler...")
    
    try:
        scheduler = initialize_scheduler()
        click.echo("✅ Scheduler started successfully!")
        click.echo("   The scheduler is now running in the background")
        click.echo("   Use 'python external_data_cli.py status' to check status")
        
    except Exception as e:
        click.echo(f"❌ Error starting scheduler: {e}", err=True)


@cli.command()
@click.pass_context
def stop_scheduler(ctx):
    """Stop the data update scheduler"""
    click.echo("🛑 Stopping data update scheduler...")
    
    try:
        scheduler = get_scheduler()
        scheduler.stop_scheduler()
        click.echo("✅ Scheduler stopped successfully!")
        
    except Exception as e:
        click.echo(f"❌ Error stopping scheduler: {e}", err=True)


if __name__ == '__main__':
    cli()