from datetime import datetime, timedelta
from sqlalchemy import select, func, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models.User import User
from src.database.enums.basic import TimeRange
from typing import Dict, Any

class UserStatistics:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_basic_counts(self) -> Dict[str, int]:
        try:
            total_users = await self.session.scalar(select(func.count(User.id)))
            active_users = await self.session.scalar(
                select(func.count(User.id)).where(User.is_active == True)
            )
            return {
                "total": total_users or 0,
                "active": active_users or 0,
                "inactive": (total_users or 0) - (active_users or 0)
            }
        except Exception as e:
            print(f"Error in get_basic_counts: {e}")
            raise

    async def get_geographical_distribution(self) -> Dict[str, Dict[int, int]]:
        try:
            country_query = (
                select(User.country_id, func.count(User.id))
                .group_by(User.country_id)
                .order_by(desc(func.count(User.id)))
            )
            country_result = await self.session.execute(country_query)

            pizzeria_query = (
                select(User.pizzeria_id, func.count(User.id))
                .group_by(User.pizzeria_id)
                .order_by(desc(func.count(User.id)))
            )
            pizzeria_result = await self.session.execute(pizzeria_query)

            return {
                "countries": dict(country_result.all()),
                "pizzerias": dict(pizzeria_result.all())
            }
        except Exception as e:
            print(f"Error in get_geographical_distribution: {e}")
            raise

    async def get_activity_metrics(self) -> Dict[str, Dict[str, Any]]:
        try:
            now = datetime.now()
            metrics = {}
            
            for time_range in TimeRange:
                days = time_range.value
                active_users = await self.session.scalar(
                    select(func.count(User.id))
                    .where(User.updated_at >= now - timedelta(days=days))
                )
                new_users = await self.session.scalar(
                    select(func.count(User.id))
                    .where(User.created_at >= now - timedelta(days=days))
                )
                metrics[time_range.name.lower()] = {
                    "active_users": active_users or 0,
                    "new_users": new_users or 0
                }

            return metrics
        except Exception as e:
            print(f"Error in get_activity_metrics: {e}")
            raise

    async def get_notification_metrics(self) -> Dict[str, Any]:
        try:
            avg_failed = await self.session.scalar(
                select(func.avg(User.failed_notifications))
            )
            max_failed = await self.session.scalar(
                select(func.max(User.failed_notifications))
            )
            users_with_failures = await self.session.scalar(
                select(func.count(User.id))
                .where(User.failed_notifications > 0)
            )

            time_query = (
                select(
                    func.date_part('hour', User.notification_time).label('hour'),
                    func.count(User.id)
                )
                .group_by('hour')
                .order_by('hour')
            )
            time_result = await self.session.execute(time_query)

            return {
                "average_failed": round(avg_failed or 0, 2),
                "max_failed": max_failed or 0,
                "users_with_failures": users_with_failures or 0,
                "time_distribution": dict(time_result.all())
            }
        except Exception as e:
            print(f"Error in get_notification_metrics: {e}")
            raise

    async def get_retention_metrics(self) -> Dict[str, Dict[str, Any]]:
        try:
            now = datetime.now()
            retention_stats = {}

            for time_range in TimeRange:
                days = time_range.value
                period = timedelta(days=days)
                
                retained_users = await self.session.scalar(
                    select(func.count(User.id))
                    .where(and_(
                        User.created_at <= now - period,
                        User.updated_at >= now - timedelta(days=1),
                        User.is_active == True
                    ))
                )
                
                total_period_users = await self.session.scalar(
                    select(func.count(User.id))
                    .where(User.created_at <= now - period)
                )

                retention_stats[time_range.name.lower()] = {
                    "retained": retained_users or 0,
                    "total": total_period_users or 0,
                    "rate": round(
                        (retained_users or 0) / (total_period_users or 1) * 100, 2
                    )
                }

            return retention_stats
        except Exception as e:
            print(f"Error in get_retention_metrics: {e}")
            raise

    async def get_complete_statistics(self) -> Dict[str, Any]:
        try:
            return {
                "counts": await self.get_basic_counts(),
                "distribution": await self.get_geographical_distribution(),
                "activity": await self.get_activity_metrics(),
                "notifications": await self.get_notification_metrics(),
                "retention": await self.get_retention_metrics()
            }
        except Exception as e:
            print(f"Error in get_complete_statistics: {e}")
            raise