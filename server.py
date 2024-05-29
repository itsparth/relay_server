import enum
# import usbrelay_py
import time
import threading
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import relay
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# count = usbrelay_py.board_count()
# print("Count: ", count)

# boards = usbrelay_py.board_details()
# print("Boards: ", boards)


# def turnOn(board: int, index: int):
#     board = boards[board]
#     result = usbrelay_py.board_control(board[board], index, 1)
#     print(f"Turn on: {index} result {result}")
#     relay.turn_on(index)
   
# def turnOff(board: int, index: int):
#     board = boards[board:int]
#     result = usbrelay_py.board_control(board[board:int], index, 0)
#     print(f"Turn off: {index} result {result}")
#     relay.turn_off(index)

def turnOn(board: int, index: int):
    relay.turn_on(index)
   
def turnOff(board: int, index: int):
    relay.turn_off(index)
 
def turnOnFor(board: int, index: int, duration: float):
    turnOn(board, index)
    time.sleep(duration)
    turnOff(board, index)


def turnOnForAsync(board: int, index: int, duration: float):
    t = threading.Thread(target=turnOnFor, args=(board, index, duration))
    t.start()


class ActionType(enum.Enum):
    on = "on"
    off = "off"
    pulse = "pulse"


class RelayControl(BaseModel):
    board: int
    index: int
    action: ActionType
    duration: float


@app.get("/boardsCount")
def getBoards():
    return {"count": int(count)}


@app.post("/control")
def controlRelay(relayControl: RelayControl):
    if relayControl.action == ActionType.on:
        turnOn(relayControl.board, relayControl.index)
    elif relayControl.action == ActionType.off:
        turnOff(relayControl.board, relayControl.index)
    elif relayControl.action == ActionType.pulse:
        turnOnForAsync(relayControl.board, relayControl.index, relayControl.duration)
    return {"status": "success"}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
