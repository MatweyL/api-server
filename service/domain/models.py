from sqlalchemy import Column, VARCHAR, Text, ForeignKey
from sqlalchemy.orm import relationship

from service.common.orm import Base


class TaskGenerationModel(Base):
    __tablename__ = 'task_generation'
    task_uid = Column(VARCHAR(64), primary_key=True, index=True)
    task_status = Column(VARCHAR(64), nullable=False)
    task_type = Column(VARCHAR(64), nullable=False)
    task_images = relationship('TaskImageModel', viewonly=True)


class TaskImageModel(Base):
    __tablename__ = 'task_image'
    image_uid = Column(VARCHAR(64), primary_key=True)
    image_url = Column(VARCHAR(128), nullable=False)
    task_uid = Column(VARCHAR(64), ForeignKey('task_generation.task_uid'), index=True)
    task = relationship('TaskGenerationModel', viewonly=True)


class TaskVideoPreviewGenerationModel(Base):
    __tablename__ = 'task_video_preview_generation'
    video_url = Column(VARCHAR(128), nullable=False)
    video_text = Column(Text)
    video_author_comments = Column(Text)
    tags = Column(Text)
    task_uid = Column(VARCHAR(64), ForeignKey('task_generation.task_uid'), primary_key=True, index=True)


class TaskAvatarGenerationModel(Base):
    __tablename__ = 'task_avatar_generation'
    avatar_description = Column(Text, nullable=False)
    task_uid = Column(VARCHAR(64), ForeignKey('task_generation.task_uid'), primary_key=True, index=True)


class TaskChannelBannerGenerationModel(Base):
    __tablename__ = 'task_channel_banner_generation'
    channel_banner_description = Column(Text, nullable=False)
    task_uid = Column(VARCHAR(64), ForeignKey('task_generation.task_uid'), primary_key=True, index=True)
