# app/models/__init__.py (update existing file)
from app.models.users import PreApprovedUser, User
from app.models.proposals import CustomerProposal, SecureProposalLink

# Export all models
__all__ = ["PreApprovedUser", "User", "CustomerProposal", "SecureProposalLink"]