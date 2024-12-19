from abc import ABC, abstractmethod
from datetime import datetime


class Authenticator(ABC):
    @abstractmethod
    def get_access_token(self) -> str:
        """Get the access token for API authentication"""
        pass

    @abstractmethod
    def expiry(self) -> datetime:
        """Get token expiry time"""
        pass

    @abstractmethod
    def refresh(self) -> str:
        """Refresh the access token"""
        pass
