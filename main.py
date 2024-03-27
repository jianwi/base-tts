from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import edge_tts
import os

app = FastAPI()

app.mount("/dist", StaticFiles(directory="static"), name="static")

class TTSRequest(BaseModel):  # 定义请求体的模型
    text: str
    voice: str = 'zh-CN-YunxiNeural'
    rate: str = '-4%'
    volume: str = '+0%'


@app.post("/tts/")  # 使用POST方法
async def generate_tts(request: TTSRequest):  # 使用请求模型
    text = request.text
    if not text:  # 检查text属性是否存在
        raise HTTPException(status_code=400, detail="Text is required for TTS.")

    try:
        # 生成音频并保存到临时文件
        temp_file = "temp_audio.mp3"
        tts = edge_tts.Communicate(text=text, voice=request.voice, rate=request.rate, volume=request.volume)
        await tts.save(temp_file)

        # 读取音频文件并准备响应
        def iterfile():
            with open(temp_file, mode="rb") as file_like:
                yield from file_like
            os.remove(temp_file)

        response = StreamingResponse(iterfile(), media_type="audio/mpeg")
        response.headers["Content-Disposition"] = "inline"
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3088)
