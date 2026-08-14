import json
from pathlib import Path

from app.schemas.training import TrainingLesson, TrainingQuizResult, TrainingQuizSubmission


STORAGE_DIR = Path(__file__).resolve().parents[2] / "storage"
TRAINING_FILE = STORAGE_DIR / "training_results.json"

LESSONS = [
    TrainingLesson(lesson_id="export_basics", title="Dis ticaret temel sureci", duration_minutes=25, required_score=70),
    TrainingLesson(lesson_id="lead_quality", title="Potansiyel musteri kalite kontrolu", duration_minutes=20, required_score=75),
    TrainingLesson(lesson_id="email_compliance", title="Spam riski ve guvenli mail", duration_minutes=18, required_score=80),
]

ANSWER_KEY = {
    "export_basics": {"q1": "incoterms", "q2": "invoice"},
    "lead_quality": {"q1": "website", "q2": "buyer"},
    "email_compliance": {"q1": "unsubscribe", "q2": "small_batch"},
}


def list_training_lessons() -> list[TrainingLesson]:
    return LESSONS


def submit_training_quiz(submission: TrainingQuizSubmission) -> TrainingQuizResult:
    key = ANSWER_KEY.get(submission.lesson_id, {})
    correct = 0
    for item in submission.answers:
        if key.get(item.question_id) == item.answer.strip().lower():
            correct += 1
    total = max(1, len(key))
    score = int(correct / total * 100)
    lesson = next((item for item in LESSONS if item.lesson_id == submission.lesson_id), LESSONS[0])
    result = TrainingQuizResult(
        employee_name=submission.employee_name,
        lesson_id=submission.lesson_id,
        score=score,
        passed=score >= lesson.required_score,
        status="passed" if score >= lesson.required_score else "needs_retry",
    )
    _write_results([result.model_dump(), *_read_results()])
    return result


def list_training_results(limit: int = 20) -> list[TrainingQuizResult]:
    return [TrainingQuizResult(**item) for item in _read_results()[:limit]]


def _read_results() -> list[dict]:
    if not TRAINING_FILE.exists():
        return []
    try:
        data = json.loads(TRAINING_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return data if isinstance(data, list) else []


def _write_results(items: list[dict]) -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    TRAINING_FILE.write_text(json.dumps(items[:100], indent=2), encoding="utf-8")
