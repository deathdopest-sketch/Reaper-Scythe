"""
Identity Management Module

Tools for managing and maintaining digital identities over time.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from .identity import DigitalIdentity, IdentityStatus


@dataclass
class IdentityProfile:
    """Extended profile for identity management."""
    identity: DigitalIdentity
    usage_log: List[Dict] = field(default_factory=list)
    maintenance_history: List[Dict] = field(default_factory=list)
    last_maintenance: Optional[datetime] = None
    next_maintenance_due: Optional[datetime] = None
    activity_score: float = 0.0
    health_status: str = "healthy"  # healthy, at_risk, burned
    
    def add_usage(self, activity: str, platform: str, timestamp: Optional[datetime] = None):
        """Log identity usage."""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.usage_log.append({
            "activity": activity,
            "platform": platform,
            "timestamp": timestamp
        })
        self.identity.last_used = timestamp
        self.identity.usage_count += 1


class ActivityTracker:
    """Tracks identity activity patterns."""
    
    def __init__(self):
        """Initialize activity tracker."""
        self.activities: List[Dict] = []
    
    def log_activity(self, identity_id: str, activity: str, platform: str):
        """Log an activity."""
        self.activities.append({
            "identity_id": identity_id,
            "activity": activity,
            "platform": platform,
            "timestamp": datetime.now()
        })
    
    def get_activity_summary(self, identity_id: str) -> Dict:
        """Get activity summary for identity."""
        activities = [a for a in self.activities if a["identity_id"] == identity_id]
        return {
            "total_activities": len(activities),
            "platforms_used": list(set(a["platform"] for a in activities)),
            "recent_activities": activities[-10:] if len(activities) > 10 else activities
        }


class IdentityManager:
    """
    Comprehensive identity management system.
    
    Provides:
    - Identity tracking and maintenance
    - Usage monitoring
    - Activity pattern analysis
    - Health monitoring
    - Rotation strategies
    """
    
    def __init__(self):
        """Initialize identity manager."""
        self.profiles: Dict[str, IdentityProfile] = {}
        self.tracker = ActivityTracker()
    
    def register_identity(self, identity: DigitalIdentity) -> IdentityProfile:
        """
        Register an identity for management.
        
        Args:
            identity: Identity to register
            
        Returns:
            IdentityProfile for the identity
        """
        profile = IdentityProfile(identity=identity)
        self.profiles[identity.identity_id] = profile
        return profile
    
    def track_usage(self, identity_id: str, activity: str, platform: str):
        """Track identity usage."""
        if identity_id in self.profiles:
            profile = self.profiles[identity_id]
            profile.add_usage(activity, platform)
            self.tracker.log_activity(identity_id, activity, platform)
        else:
            raise ValueError(f"Identity {identity_id} not registered")
    
    def maintain_identity(self, identity_id: str) -> Dict:
        """
        Perform maintenance on an identity.
        
        Args:
            identity_id: ID of identity to maintain
            
        Returns:
            Maintenance report
        """
        if identity_id not in self.profiles:
            return {"error": "Identity not found"}
        
        profile = self.profiles[identity_id]
        identity = profile.identity
        
        maintenance_tasks = []
        
        # Update last used
        if identity.last_used:
            days_since_use = (datetime.now() - identity.last_used).days
            if days_since_use > 30:
                maintenance_tasks.append("Identity inactive for 30+ days")
        
        # Check account health
        if len(identity.social_media_accounts) == 0:
            maintenance_tasks.append("No social accounts - consider adding")
        
        # Update maintenance date
        profile.last_maintenance = datetime.now()
        profile.next_maintenance_due = datetime.now() + timedelta(days=7)
        
        maintenance_record = {
            "identity_id": identity_id,
            "date": datetime.now(),
            "tasks_performed": maintenance_tasks,
            "health_status": profile.health_status
        }
        
        profile.maintenance_history.append(maintenance_record)
        return maintenance_record
    
    def rotate_identity(self, old_identity_id: str) -> DigitalIdentity:
        """
        Rotate (replace) an identity with a new one.
        
        Args:
            old_identity_id: ID of identity to replace
            
        Returns:
            New DigitalIdentity
        """
        if old_identity_id not in self.profiles:
            raise ValueError(f"Identity {old_identity_id} not found")
        
        from .identity import IdentityGenerator
        
        # Generate new identity
        generator = IdentityGenerator()
        new_identity = generator.generate_persona()
        
        # Archive old identity
        old_profile = self.profiles[old_identity_id]
        old_profile.identity.status = IdentityStatus.ARCHIVED
        old_profile.health_status = "rotated"
        
        # Register new identity
        self.register_identity(new_identity)
        
        return new_identity
    
    def audit_identity(self, identity_id: str) -> Dict:
        """
        Perform comprehensive audit of identity.
        
        Args:
            identity_id: ID of identity to audit
            
        Returns:
            Audit report
        """
        if identity_id not in self.profiles:
            return {"error": "Identity not found"}
        
        profile = self.profiles[identity_id]
        identity = profile.identity
        
        activity_summary = self.tracker.get_activity_summary(identity_id)
        
        return {
            "identity_id": identity_id,
            "status": identity.status.value,
            "usage_count": identity.usage_count,
            "last_used": identity.last_used.isoformat() if identity.last_used else None,
            "accounts_count": len(identity.social_media_accounts),
            "activity_summary": activity_summary,
            "health_status": profile.health_status,
            "maintenance_count": len(profile.maintenance_history),
            "risk_factors": self._assess_risks(profile)
        }
    
    def _assess_risks(self, profile: IdentityProfile) -> List[str]:
        """Assess risks for an identity."""
        risks = []
        identity = profile.identity
        
        if identity.usage_count == 0:
            risks.append("Identity never used - may appear suspicious")
        
        if identity.last_used:
            days_inactive = (datetime.now() - identity.last_used).days
            if days_inactive > 90:
                risks.append("Identity inactive for 90+ days")
        
        if len(identity.social_media_accounts) == 0:
            risks.append("No social media presence")
        
        return risks
    
    def backup_identity_data(self, identity_id: str) -> Dict:
        """
        Backup identity data securely.
        
        Args:
            identity_id: ID of identity to backup
            
        Returns:
            Backup information (no actual sensitive data)
        """
        if identity_id not in self.profiles:
            return {"error": "Identity not found"}
        
        profile = self.profiles[identity_id]
        identity = profile.identity
        
        return {
            "identity_id": identity_id,
            "backup_date": datetime.now().isoformat(),
            "metadata": {
                "type": identity.identity_type.value,
                "status": identity.status.value,
                "accounts_count": len(identity.social_media_accounts),
                "usage_count": identity.usage_count
            },
            "note": "Sensitive data should be stored separately and encrypted"
        }


# Convenience functions
def track_identity_usage(identity_id: str, activity: str, platform: str) -> None:
    """Track usage of an identity."""
    manager = IdentityManager()
    manager.track_usage(identity_id, activity, platform)


def maintain_identity(identity_id: str) -> Dict:
    """Maintain an identity."""
    manager = IdentityManager()
    return manager.maintain_identity(identity_id)


def rotate_identity(old_identity_id: str) -> DigitalIdentity:
    """Rotate an identity."""
    manager = IdentityManager()
    return manager.rotate_identity(old_identity_id)


def audit_identity(identity_id: str) -> Dict:
    """Audit an identity."""
    manager = IdentityManager()
    return manager.audit_identity(identity_id)


def backup_identity_data(identity_id: str) -> Dict:
    """Backup identity data."""
    manager = IdentityManager()
    return manager.backup_identity_data(identity_id)

