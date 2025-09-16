from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ConsoleErrorLog(Base):
    """Model for LOG.tblconsoleErrorLogs table"""
    __tablename__ = 'tblconsoleErrorLogs'
    __table_args__ = {'schema': 'LOG'}
    
    id = Column(Integer, primary_key=True)
    practiceid = Column(Integer)
    stacktraces = Column(Text)
    ErrorMassage = Column(Text)  # Note: keeping original column name with typo
    url = Column(String(500))
    ErrorTime = Column(DateTime)
    insertdat = Column(DateTime)
    updatedat = Column(DateTime)
    JiraStatus = Column(String(50))
    Status = Column(String(50))
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            'id': self.id,
            'practiceid': self.practiceid,
            'stacktraces': self.stacktraces,
            'ErrorMassage': self.ErrorMassage,
            'url': self.url,
            'ErrorTime': self.ErrorTime.isoformat() if self.ErrorTime else None,
            'insertdat': self.insertdat.isoformat() if self.insertdat else None,
            'updatedat': self.updatedat.isoformat() if self.updatedat else None,
            'JiraStatus': self.JiraStatus,
            'Status': self.Status
        }
