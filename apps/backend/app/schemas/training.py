from pydantic import BaseModel, Field


class TrainingLesson(BaseModel):
    lesson_id: str
    title: str
    duration_minutes: int
    required_score: int


class TrainingAnswer(BaseModel):
    question_id: str
    answer: str


class TrainingQuizSubmission(BaseModel):
    employee_name: str
    lesson_id: str
    answers: list[TrainingAnswer] = Field(default_factory=list)


class TrainingQuizResult(BaseModel):
    employee_name: str
    lesson_id: str
    score: int
    passed: bool
    status: str
