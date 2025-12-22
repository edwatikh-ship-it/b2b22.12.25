from pydantic import BaseModel


class UpdateEmailPolicyRequestDTO(BaseModel):
    emailpolicy: str
