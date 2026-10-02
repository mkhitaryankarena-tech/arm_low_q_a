from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from app.benchmark_questions import BENCHMARK_QUESTIONS

from app.qa import ask_question
from app.benchmark import run_benchmark

app = FastAPI(
    title="Armenian Legal Q&A API",
    description=(
        "RAG-based Q&A system for the Law of the "
        "Republic of Armenia on Electronic Communications"
    ),
    version="1.0.0"
)


# Static files (CSS)
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# HTML templates
templates = Jinja2Templates(
    directory="templates"
)


class QuestionRequest(BaseModel):
    question: str
class BenchmarkRequest(BaseModel):
    question: str

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.post("/ask")
def ask(request: QuestionRequest):
    try:
        result = ask_question(request.question)

        return {
            "question": result["question"],
            "answer": result["answer"],
            "sources": result["sources"]
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
@app.post("/benchmark")
def benchmark(request: BenchmarkRequest):
    try:
        return run_benchmark(
            question=request.question                  
        
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
@app.get("/benchmark/questions")
def get_benchmark_questions():
    return {
        "questions": BENCHMARK_QUESTIONS
    }