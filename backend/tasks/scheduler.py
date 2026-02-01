from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.future import select
from datetime import datetime, timedelta
from database import AsyncSessionLocal
from models.db_models import User, PantryItem
from services.notification_service import NotificationService
import asyncio

scheduler = AsyncIOScheduler()

async def check_expiring_ingredients():
    print("🕒 Running daily expiry check...")
    async with AsyncSessionLocal() as db:
        # Get all users
        result = await db.execute(select(User))
        users = result.scalars().all()
        
        for user in users:
            # Find items expiring in <= 2 days
            stmt = select(PantryItem).where(
                PantryItem.user_id == user.id,
                PantryItem.days_until_expiry <= 2
            )
            item_result = await db.execute(stmt)
            expiring_items = item_result.scalars().all()
            
            if expiring_items:
                items_data = [
                    {
                        "name": item.ingredient_name,
                        "days": item.days_until_expiry,
                        "urgency": item.urgency,
                        "storage": item.storage
                    } for item in expiring_items
                ]
                NotificationService.send_expiry_email(user.email, user.full_name, items_data)

def start_scheduler():
    # Schedule for 9:00 AM every day
    scheduler.add_job(check_expiring_ingredients, 'cron', hour=9, minute=0)
    # Also run once on startup for debug/demonstration (can be commented out)
    # scheduler.add_job(check_expiring_ingredients, 'date', run_date=datetime.now() + timedelta(seconds=10))
    scheduler.start()
    print("🚀 Background scheduler started.")
