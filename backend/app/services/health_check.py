"""
Health Check Service for Enterprise DaaS Governance Portal
Comprehensive system health monitoring
"""

import os
import psutil
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.orm import Session
import structlog

from app.database import engine, SessionLocal
from app.logging_config import get_logger

logger = get_logger(__name__)


class HealthCheckService:
    """
    Comprehensive health check service

    Monitors:
    - API status
    - Database connectivity
    - Database query performance
    - System resources (CPU, memory, disk)
    - Application uptime
    - External dependencies (Redis, if configured)
    """

    def __init__(self):
        self.start_time = datetime.now()
        self.logger = logger

    def get_uptime(self) -> Dict[str, Any]:
        """
        Get application uptime

        Returns:
            Dictionary with uptime information
        """
        uptime_delta = datetime.now() - self.start_time
        return {
            "started_at": self.start_time.isoformat(),
            "uptime_seconds": int(uptime_delta.total_seconds()),
            "uptime_human": str(uptime_delta).split('.')[0]  # Remove microseconds
        }

    def check_database(self) -> Dict[str, Any]:
        """
        Check database connectivity and performance

        Returns:
            Dictionary with database health status
        """
        try:
            db: Session = SessionLocal()
            start_time = time.time()

            # Execute simple query to test connectivity
            result = db.execute(text("SELECT 1")).scalar()

            # Measure query time
            query_time_ms = (time.time() - start_time) * 1000

            # Get database info
            db_info = db.execute(text("SELECT version()")).scalar()

            # Test connection pool
            pool = engine.pool
            pool_status = {
                "pool_size": pool.size(),
                "checked_in_connections": pool.checkedin(),
                "checked_out_connections": pool.checkedout(),
                "overflow_connections": pool.overflow(),
            }

            db.close()

            return {
                "status": "healthy",
                "accessible": True,
                "query_time_ms": round(query_time_ms, 2),
                "database_version": db_info.split()[0:2] if db_info else "unknown",
                "connection_pool": pool_status
            }

        except Exception as e:
            self.logger.error("database_health_check_failed", error=str(e))
            return {
                "status": "unhealthy",
                "accessible": False,
                "error": str(e)
            }

    def check_system_resources(self) -> Dict[str, Any]:
        """
        Check system resource usage

        Returns:
            Dictionary with system resource metrics
        """
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()

            # Memory usage
            memory = psutil.virtual_memory()
            memory_mb = memory.total / (1024 * 1024)
            memory_used_mb = memory.used / (1024 * 1024)

            # Disk usage
            disk = psutil.disk_usage('/')
            disk_gb = disk.total / (1024 * 1024 * 1024)
            disk_used_gb = disk.used / (1024 * 1024 * 1024)
            disk_free_gb = disk.free / (1024 * 1024 * 1024)

            # Determine health status
            status = "healthy"
            warnings = []

            if cpu_percent > 80:
                status = "degraded"
                warnings.append("High CPU usage")

            if memory.percent > 85:
                status = "degraded"
                warnings.append("High memory usage")

            if disk.percent > 90:
                status = "degraded"
                warnings.append("Low disk space")

            return {
                "status": status,
                "warnings": warnings,
                "cpu": {
                    "usage_percent": round(cpu_percent, 2),
                    "count": cpu_count
                },
                "memory": {
                    "total_mb": round(memory_mb, 2),
                    "used_mb": round(memory_used_mb, 2),
                    "available_mb": round(memory.available / (1024 * 1024), 2),
                    "usage_percent": round(memory.percent, 2)
                },
                "disk": {
                    "total_gb": round(disk_gb, 2),
                    "used_gb": round(disk_used_gb, 2),
                    "free_gb": round(disk_free_gb, 2),
                    "usage_percent": round(disk.percent, 2)
                }
            }

        except Exception as e:
            self.logger.error("system_health_check_failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    def check_redis(self) -> Optional[Dict[str, Any]]:
        """
        Check Redis connectivity (if configured)

        Returns:
            Dictionary with Redis health status or None if not configured
        """
        redis_url = os.getenv("REDIS_URL")
        enable_redis = os.getenv("ENABLE_REDIS_CACHE", "false").lower() == "true"

        if not enable_redis or not redis_url:
            return None

        try:
            import redis
            r = redis.from_url(redis_url, socket_connect_timeout=2)

            start_time = time.time()
            r.ping()
            ping_time_ms = (time.time() - start_time) * 1000

            # Get Redis info
            info = r.info()

            return {
                "status": "healthy",
                "accessible": True,
                "ping_time_ms": round(ping_time_ms, 2),
                "version": info.get("redis_version"),
                "used_memory_mb": round(info.get("used_memory", 0) / (1024 * 1024), 2),
                "connected_clients": info.get("connected_clients", 0)
            }

        except ImportError:
            self.logger.warning("redis_client_not_installed")
            return {
                "status": "unavailable",
                "error": "redis module not installed"
            }
        except Exception as e:
            self.logger.error("redis_health_check_failed", error=str(e))
            return {
                "status": "unhealthy",
                "accessible": False,
                "error": str(e)
            }

    def check_external_dependencies(self) -> Dict[str, Any]:
        """
        Check external service dependencies

        Returns:
            Dictionary with external dependency statuses
        """
        dependencies = {}

        # Check Redis (if configured)
        redis_status = self.check_redis()
        if redis_status:
            dependencies["redis"] = redis_status

        # Check Sentry (if configured)
        enable_sentry = os.getenv("ENABLE_SENTRY", "false").lower() == "true"
        sentry_dsn = os.getenv("SENTRY_DSN")

        if enable_sentry and sentry_dsn:
            dependencies["sentry"] = {
                "status": "configured",
                "enabled": True
            }
        else:
            dependencies["sentry"] = {
                "status": "not_configured",
                "enabled": False
            }

        return dependencies

    def get_comprehensive_health(self) -> Dict[str, Any]:
        """
        Get comprehensive health check report

        Returns:
            Dictionary with all health check results
        """
        # Basic API health
        api_health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "Enterprise DaaS Governance Portal",
            "version": os.getenv("APP_VERSION", "2.0.0")
        }

        # Uptime
        uptime = self.get_uptime()

        # Database health
        database = self.check_database()

        # System resources
        system = self.check_system_resources()

        # External dependencies
        dependencies = self.check_external_dependencies()

        # Determine overall health status
        overall_status = "healthy"

        if database.get("status") == "unhealthy":
            overall_status = "unhealthy"
        elif system.get("status") == "degraded":
            overall_status = "degraded"

        # Check if any dependency is unhealthy
        for dep_name, dep_status in dependencies.items():
            if isinstance(dep_status, dict) and dep_status.get("status") == "unhealthy":
                overall_status = "degraded"  # Dependencies don't make overall unhealthy

        return {
            "status": overall_status,
            "timestamp": api_health["timestamp"],
            "service": api_health["service"],
            "version": api_health["version"],
            "uptime": uptime,
            "checks": {
                "database": database,
                "system_resources": system,
                "dependencies": dependencies
            }
        }

    def get_readiness(self) -> Dict[str, Any]:
        """
        Check if application is ready to serve traffic (Kubernetes readiness probe)

        Returns:
            Dictionary with readiness status
        """
        # Check critical components only
        database = self.check_database()

        is_ready = database.get("accessible", False)

        return {
            "ready": is_ready,
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "database": database.get("accessible", False)
            }
        }

    def get_liveness(self) -> Dict[str, Any]:
        """
        Check if application is alive (Kubernetes liveness probe)

        Returns:
            Dictionary with liveness status
        """
        # Simple check - if we can respond, we're alive
        return {
            "alive": True,
            "timestamp": datetime.now().isoformat()
        }


# Singleton instance
health_check_service = HealthCheckService()
