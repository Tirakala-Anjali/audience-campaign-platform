from app.schemas.auth import RegisterRequest, RegisterResponse, RoleResponse, UserResponse
from app.schemas.role import RoleBase, RoleCreate, RoleRead
from app.schemas.user import UserBase, UserCreate, UserRead
from app.schemas.audience_member import AudienceMemberBase, AudienceMemberCreate, AudienceMemberRead
from app.schemas.segment import SegmentBase, SegmentCreate, SegmentRead
from app.schemas.campaign import CampaignBase, CampaignCreate, CampaignRead
from app.schemas.template import TemplateBase, TemplateCreate, TemplateRead
from app.schemas.message import MessageBase, MessageCreate, MessageRead
from app.schemas.delivery_log import DeliveryLogBase, DeliveryLogCreate, DeliveryLogRead
from app.schemas.feedback import FeedbackBase, FeedbackCreate, FeedbackRead

__all__ = [
    # Auth
    "RegisterRequest", "RegisterResponse", "RoleResponse", "UserResponse",
    # Domain schemas
    "RoleBase", "RoleCreate", "RoleRead",
    "UserBase", "UserCreate", "UserRead",
    "AudienceMemberBase", "AudienceMemberCreate", "AudienceMemberRead",
    "SegmentBase", "SegmentCreate", "SegmentRead",
    "CampaignBase", "CampaignCreate", "CampaignRead",
    "TemplateBase", "TemplateCreate", "TemplateRead",
    "MessageBase", "MessageCreate", "MessageRead",
    "DeliveryLogBase", "DeliveryLogCreate", "DeliveryLogRead",
    "FeedbackBase", "FeedbackCreate", "FeedbackRead",
]
