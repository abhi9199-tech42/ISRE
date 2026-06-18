"""FastAPI REST API server for ISRE."""


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from ..pipeline import ISREPipeline

app = FastAPI(
    title="ISRE API",
    description="Intentional Semantic Reasoning Engine - REST API",
    version="0.1.0",
)

pipeline = ISREPipeline()


class ProcessRequest(BaseModel):
    input: str
    modality: str = "text"
    formats: Optional[list[str]] = None


class ProcessResponse(BaseModel):
    request_id: str
    outputs: dict
    knowledge_gaps: list
    decision_metadata: dict


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


@app.post("/process", response_model=ProcessResponse)
async def process(req: ProcessRequest):
    result = pipeline.process(req.input, req.modality, req.formats)
    return ProcessResponse(
        request_id=result["request_id"],
        outputs=result["outputs"],
        knowledge_gaps=result.get("knowledge_gaps", []),
        decision_metadata=result["decision_metadata"],
    )


@app.get("/trace/{request_id}")
async def get_trace(request_id: str):
    trace = pipeline.get_trace(request_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    return {"request_id": request_id, "trace": trace}


def main():
    """Run the API server with uvicorn."""
    import uvicorn
    uvicorn.run("isre.api.server:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
