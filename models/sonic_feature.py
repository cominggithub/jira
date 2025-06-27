from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import db


class FeatureMap(db.Model):
    """EC SONiC Feature Map - stores feature support across different branches"""
    __tablename__ = 's_feature_map'
    
    feature_key = Column(String(255), primary_key=True)
    category = Column(String(100))
    feature_n1 = Column(Text)  # Feature description
    
    # Branch support status columns
    ec_sonic_2111 = Column(String(50))
    ec_sonic_2211 = Column(String(50))
    ec_202211_fabric = Column(String(50))
    ec_sonic_2311_x = Column(String(50))
    ec_sonic_2311_n = Column(String(50))
    vs_202311 = Column(String(50))
    vs_202311_fabric = Column(String(50))
    
    # Source and component info
    ec_proprietary = Column(String(20))  # 'COMMUNITY' or 'EC'
    component = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to labels
    labels = relationship("FeatureLabel", back_populates="feature", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<FeatureMap {self.feature_key}>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'feature_key': self.feature_key,
            'category': self.category,
            'feature_description': self.feature_n1,
            'branches': {
                'ec_sonic_2111': self.ec_sonic_2111,
                'ec_sonic_2211': self.ec_sonic_2211,
                'ec_202211_fabric': self.ec_202211_fabric,
                'ec_sonic_2311_x': self.ec_sonic_2311_x,
                'ec_sonic_2311_n': self.ec_sonic_2311_n,
                'vs_202311': self.vs_202311,
                'vs_202311_fabric': self.vs_202311_fabric,
            },
            'ec_proprietary': self.ec_proprietary,
            'component': self.component,
            'labels': [label.label for label in self.labels],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class FeatureLabel(db.Model):
    """Feature Labels - many-to-many relationship with features"""
    __tablename__ = 's_feature_label'
    
    feature_key = Column(String(255), ForeignKey('s_feature_map.feature_key'), primary_key=True)
    label = Column(String(100), primary_key=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship back to feature
    feature = relationship("FeatureMap", back_populates="labels")
    
    # Note: Primary key constraint is automatically unique
    
    def __repr__(self):
        return f"<FeatureLabel {self.feature_key}:{self.label}>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'feature_key': self.feature_key,
            'label': self.label,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }