from openai import OpenAI
from fastapi import FastAPI, Form, Request, WebSocket
from typing import Annotated

from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Load OpenAI client
client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
)

# Jinja2 Templates
templates = Jinja2Templates(directory="templates")

# Mount Static Directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# => Chat logs and Keep history (https://127.0.0.1:8000/docs)
chatlogs = [
    {
        "role": "system",
        "content": "You are a helpful chatbot assistant,\
            you help people for various things and you know everything about general knowledge." # \ mean next new line
    }
]
datas = []

@app.get("/")
def read_root():
    return RedirectResponse(url="/chatpage")

# => Text Generate
# => Template (http://127.0.0.1:8000/)

@app.get("/", response_class=HTMLResponse)
async def chatpage(request: Request):
    return templates.TemplateResponse(
        # request= request,name="layout.html"
        # "layout.html",("request":request)

        # request= request,name="layout.html",context={"datas":datas}
        "layout.html", {"request": request, "datas": datas} # get old datas
    )


# # => Text Generate (Before WebSocket) (Handle Text Input - Form POST)
# @app.post("/", response_class=HTMLResponse)
# async def chat(request: Request, userinput: Annotated[str, Form()]):
#     chatlogs.append({"role": "user", "content": userinput})
#     datas.append(userinput)

#     completion = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         store=False,
#         messages=chatlogs,
#         temperature=0.6
#     )

#     botresponse = completion.choices[0].message.content
#     chatlogs.append({"role": "assistant", "content": botresponse})
#     datas.append(botresponse)

#     return templates.TemplateResponse(
#         # request= request,name="layout.html",context={"datas":datas}
#         "layout.html", {"request": request, "datas": datas}
#     )

# => Text Generate ( After WebSocket , without Streaming)
# exe 1
# @app.websocket("/ws")
# async def chat(websocket: WebSocket):
#     await websocket.accept()
#     while True:
#         userinput = await websocket.receive_text()
#         await.websocket.send_text(userinput)


# exe 2
# @app.websocket("/ws")
# async def chat(websocket: WebSocket):
#     await websocket.accept()
#     while True:
#         userinput = await websocket.receive_text()

#         chatlogs.append({"role": "user", "content": userinput})

#         try:
#             completion = client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 store=False,
#                 messages=chatlogs,
#                 temperature=0.6
#             )

#             botresponse = completion.choices[0].message.content
#             # await websocket.send_text(str(completion)) # explain how to get choices[0].message.content
#             await websocket.send_text(botresponse)

#             chatlogs.append({"role": "assistant", "content": botresponse})



#         except Exception as err:
#             await websocket.send_text(f"Error found: {str(err)}")
#             break



# => Text Generate ( After WebSocket , with Streaming)
@app.websocket("/ws")
async def chat(websocket: WebSocket):
    await websocket.accept()
    while True:
        userinput = await websocket.receive_text()

        chatlogs.append({"role": "user", "content": userinput})

        fullresponse = ""


        try:
            completion = client.chat.completions.create(
                model="gpt-4.1",
                store=False,
                messages=chatlogs,
                temperature=0.6,
                stream=True
            )

            for chunk in completion:
                botresponse = chunk.choices[0].delta.content
                if botresponse is not None:
                    fullresponse += botresponse
                    await websocket.send_text(str(botresponse))
            chatlogs.append({"role": "assistant", "content": fullresponse})



        except Exception as err:
            await websocket.send_text(f"Error found: {str(err)}")
            break


# => Image Generate 
# => Template (http://127.0.0.1:8000/image)

@app.get("/image", response_class=HTMLResponse)
async def image(request: Request):
    return templates.TemplateResponse(
        # request= request,name="image.html"
        "image.html", {"request": request, "data": None, "error": None}
    )

# => Text Generate (Before WebSocket)
# @app.post("/image", response_class=HTMLResponse)
# async def generateimage(request: Request, userinput: Annotated[str, Form()]):
#     try:
#         completion = client.images.generate(
#             model="dall-e-2",
#             prompt=userinput,
#             size="256x256",
#             n=1
#         )
#         botresponse = completion.data[0].url

#         if not completion.data or not botresponse:
#             raise ValueError("No image generated")

#         return templates.TemplateResponse(
#             "image.html", {"request": request, "data": botresponse, "error": None}
#         )

#     except Exception as e:
#         return templates.TemplateResponse(
#             "image.html", {"request": request, "data": None, "error": f"Error generating image: {str(e)}"}
#         )


# => Text Generate (After WebSocket)
@app.websocket("/image")
async def generateimage(websocket: WebSocket):
    await websocket.accept()
    while True:
        userinput = await websocket.receive_text()

        
        try:
            completion = client.images.generate(
                model="dall-e-2",
                prompt=userinput,
                size="256x256",
                n=1
            )

            botresponse = completion.data[0].url

            if not completion.data or not botresponse:
                raise ValueError("No image generated")

            await websocket.send_text(str(botresponse))

        except Exception as err:
            await websocket.send_text(f"Error found: {str(err)}")
            break


#tamplate example
# https://fastapi.tiangolo.com/advanced/templates/#using-jinja2templates


# uvicorn main:app --reload