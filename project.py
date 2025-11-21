from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Employee(BaseModel):
    id: int
    name: str
    email: str


@app.get("/test")
async def get_something():
    return {"response": "got soemting from db"}

@app.post("/test")
async def post_something(employee: Employee):
    print(employee)
    return {"status": "created succesfully", "employee": employee}

@app.put("/test{id}")
async def update_something(new_employee: Employee):
    print(new_employee)
    return {"status": "updated", "employee": new_employee}