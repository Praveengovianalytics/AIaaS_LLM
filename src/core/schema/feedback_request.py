from pydantic import BaseModel


class FeedbackRequest(BaseModel):
    """
    Feedback Request Model
    """

    chat_history: list
    user_timestamp: str
    feedback_timestamp: str
    bot_timestamp: str
    feedback_timestamp: str
    feedback: str
