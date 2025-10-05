# Life's API V.02

# This API leverages posts from any reddit community, preferably a inspirational community that posts quotes, images with quotes etc. 


# Updates

- (0.1) Implemented Tesseract OCR so now images and their quotes are now transferred into a semi-readable string.

- (0.2) Life API now Integrates Ollama phi3:3.8b to rewrite and clean up the quote that has been extracted from the image.








- Future will include AI integration where I clean up the quotes and package them nicely with the image.

- Expect constant updates as I am constantly going to improve this API as much as possible



# Contributions

- All are welcome, if you want to implement any of the above features I plan on adding please do!



# notes on FAST API (I am learning this with you so take my notes as is and confirm with your own research)

- So FASTAPI leverages Type Hints to add things such as metadata(data about data, basically for a picture it would be it's Date taken etc.) or anything else.

- Type Hints used in python are declared as follows:

    # def someFunction(somevariable : str):
            # somevariable. (now some variable has properties that it wouldn't have otherwise, aka for strings in this case)

- Some things to remember is that Type Hints can be declared in many ways depending on the version of python you are running, so make sure to use the best format!

    # Some Notes taken from FAST API DOC
        from typing import Optional

        def say_hi(name: Optional[str] = None):
            if name is not None:
                print(f"Hey {name}!")
            else:
                print("Hello World")
        Using Optional[str] instead of just str will let the editor help you detect errors where you could be assuming that a value is always a str, when it could actually be None too.

        Optional[Something] is actually a shortcut for Union[Something, None], they are equivalent.

        This also means that in Python 3.10, you can use Something | None:

- FastAPI also uses pythons new Pydantic Library to declare properties for data types that are instances of an class EX: 
        from datetime import datetime

        from pydantic import BaseModel


        class User(BaseModel):
            id: int
            name: str = "John Doe"
            signup_ts: datetime | None = None
            friends: list[int] = []


        external_data = {
            "id": "123",
            "signup_ts": "2017-06-01 12:22",
            "friends": [1, "2", b"3"],
        }
        user = User(**external_data)
        print(user)
        # > User id=123 name='John Doe' signup_ts=datetime.datetime(2017, 6, 1, 12, 22) friends=[1, 2, 3]
        print(user.id)
        # > 123


-- end of notes ( more to be added soon as we progress into this new API (suggestions are welcome so do contribute if you believe you'd want to change something))

