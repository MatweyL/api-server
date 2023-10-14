from pydantic import BaseModel


class UploadingResponse(BaseModel):
    success: bool
    image_url: str
