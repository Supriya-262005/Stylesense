import os
from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from utils.analysis import analyze_face
from utils.ai import get_recommendations

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze")
async def analyze(
    image: UploadFile = File(...),
    gender: str = Form(...),
    api_key: str = Form(None)
):
    try:
        # If user provides API key in form, set it for this session implicitly
        # (Note: In a real app we'd pass it to the function directly, but here we rely on env or form)
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key
            # Re-init client in utils.ai if needed (simple hack for this demo script)
            import utils.ai
            from groq import Groq
            utils.ai.client = Groq(api_key=api_key)

        contents = await image.read()
        
        # 1. Analyze Face
        profile = analyze_face(contents)
        profile["gender"] = gender
        
        # 2. Get AI Recommendations
        recommendations = get_recommendations(profile)
        
        return JSONResponse({
            "profile": profile,
            "recommendations": recommendations
        })
        
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)