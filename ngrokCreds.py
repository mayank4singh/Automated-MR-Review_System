from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/webhook/gitlab")
async def gitlab_webhook(request: Request):
    payload = await request.json()

    print("🔥 Received GitLab Event")
    print(payload)

    return {"status": "received"}