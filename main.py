from fastapi import FastAPI, Query
from pydantic import BaseModel, HttpUrl
from pydantic import Field
from typing import Literal
from typing import Optional
from fastapi import Depends, Header, HTTPException, status
from PIL import Image
from io import BytesIO
import asyncio
import httpx
import random

import pytesseract

#cache 
import time
CACHE = {}
CACHE_TTL = 300
CACHE_TIME = {}
###

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

#auth

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_KEY: str = "dev-secret"  # fallback for local
    class Config:
        env_file = ".env"

settings = Settings()


async def require_api_key(x_api_key: str | None = Header(default=None)):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")
    return True

# end of auth


# (temporary documnentation) This API allows you to grab any inspiritional quote directly from r/inspiration on reddit. Although most are images (AI will be implemented later to counteract this)

app = FastAPI()


class PostPreview(BaseModel):
    id: str
    title: str
    score: int = Field(ge=0)
    permalink: HttpUrl
    author: Optional[str] = None
    date: float
    image: Optional[str] = None
    image_quote: Optional[str] = None

class SubredditResponse(BaseModel):
    subreddit: str
    limit: int
    posts: list[PostPreview]
    sort: Literal["hot", "new", "top"]
    count: int

async def image_to_bytes(img_url: str):

    async with httpx.AsyncClient() as client:
        response = await client.get(img_url)     
        response.raise_for_status()
    img = Image.open(BytesIO(response.content))  
    return img


async def clean_qoute(quote: str):
    string = ""

    prompt = f"""Rewrite this quote, remove any new break lines, and make it clean and fill in blanks
    Max ~{300} characters. Return ONLY the final text (no preface/quotes).

    Quote:
    {quote}
    """

    payload = {
        "model": "phi3:3.8b",  
        "prompt": prompt,
        "temperature": 0.2,
        "stream": False
    }


    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post("http://localhost:11434/api/generate", json=payload)
        r.raise_for_status()
        string = (r.json().get("response") or "").strip()      
    return string



async def fetch_posts(subreddit: str, limit: int, sort:Literal["hot", "new", "top"]):
    url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit={50}"
    headers = {"User-Agent": "fastapi-learning-app/0.1"}
    sets = ["png", "jpg", "jpeg", "webp"]
    image = ""
    NEW_POSTS = []



    # add error handling later
        

    # Include more types, for example if it's a gif then....its skipped
    
    while len(NEW_POSTS) < 90:
       
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
        JSONDATA = data.get("data", {}).get("children", [])

        after = data.get("data", {}).get("after")

        for d in JSONDATA:

            image = d.get("data", {}).get("url", "")
       
            if image == ".jpg" or image == ".png":
                image = image[-3:]
            else:
                image = image[-4:]

            if image in sets:
                NEW_POSTS.append(PostPreview.model_validate({
                    "title": d.get("data", {}).get("title", ""),
                    "score": d.get("data", {}).get("score", 0),
                    "id": d.get("data", {}).get("id", ""),
                    "permalink": "https://www.reddit.com" + d.get("data", {}).get("permalink", "/"),
                    "author": d.get("data", {}).get("author", ""),
                    "date": d.get("data", {}).get("created_utc", 0.0),
                    "image": d.get("data", {}).get("url", ""),
                    "image_quote": "error"
                }).model_dump())
                   
        

        if not after:
            break

        url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit={50}&after={after}"
        await asyncio.sleep(3) 

    


   
       
        
   
 


    return NEW_POSTS
    



@app.get("/reddit/{subreddit}", 
    response_model=SubredditResponse,
    summary="List posts from a subreddit, mainly r/inspiration",
    description="N/A",         
)
async def get_inspiration_from_reddit(subreddit: str, limit: int = Query(5, ge=1, le=25), sort: Literal["hot", "new", "top"] = "hot", _auth: bool = Depends(require_api_key)):
    subreddit = subreddit.lower()

    

    if subreddit in CACHE and time.time() - CACHE_TIME[subreddit] < CACHE_TTL:
           posts = CACHE[subreddit]
    else:
        posts = await fetch_posts(subreddit, limit, sort)
        CACHE[subreddit] = posts
        CACHE_TIME[subreddit] = time.time()
    

    random.shuffle(posts)
    posts = posts[:limit]


    #for entry in NEW_POSTS:
        # quote =  pytesseract.image_to_string(await image_to_bytes(entry["image"]))
        # quote = await clean_qoute(quote)
        #entry["image_quote"] = quote
            
    return {
        "subreddit": subreddit,
        "limit": limit,
        "posts": posts,
        "sort": sort,
        "count": len(posts),
    }

