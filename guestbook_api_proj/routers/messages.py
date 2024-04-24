from fastapi import APIRouter, Form, Depends, HTTPException, status
from dependencies import get_db, validate_user
from db import Database

router = APIRouter(tags=["messages"])


@router.get("/messages/most_upvoted")
def get_most_upvoted_messages(db: Database = Depends(get_db)):
    messages = db.get("top_messages", ["id", "message", "upvotes"])

    return messages


@router.post("/messages/{message_id}/upvote")
def upvote_a_specific_message(message_id: int, db: Database = Depends(get_db),
                              user_id: str = Depends(validate_user)):
    # 1. does the message even exist? try to get it from the db.
    message = db.get_one("guestbook", ["id", "user_id", "private"], where={"id": message_id})

    # 2. prevent users from upvoting private messages they do not own, or messages that don't exist
    if (not message) or (message['private'] and message['user_id'] != user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="A message by this id either does not exist or is private")

    # 3. prevent users from upvoting their own messages
    if message["user_id"] == user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Please upvote messages other than your own")

    # 4. prevent users from upvoting a messages more than once
    upvote = db.get_one("upvotes", ["id"], where={"user_id": user_id, "message_id": message_id})

    if upvote:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You have already upvoted this message")

    db.write("upvotes", ["user_id", "message_id"], [user_id, message_id])

    return {"status": "Successfully upvoted message with id " + str(message_id) + ". Thank you!"}


@router.post("/messages")
def write_a_message_on_the_guestbook(message: str = Form(...), private: bool = Form(False),
                                     db: Database = Depends(get_db),
                                     user_id: int = Depends(validate_user)):
    message_id = db.write("guestbook", ["user_id", "message", "private"], [user_id, message, private])

    return {
        "message_id": message_id
    }


# POST  -> create a new resource
# PUT   -> update an existing resource (full replace)
# PATCH -> update an existing resource (partially)

@router.patch("/messages/{message_id}")
def update_a_specific_message(message_id: int, message: str = Form(...), private: bool = Form(False),
                              db: Database = Depends(get_db),
                              user_id: str = Depends(validate_user)):
    message_db = db.get_one("guestbook", ["id", "user_id"], where={"id": message_id})

    if not message_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message was not found")

    if message_db.get("user_id") == user_id:
        db.update("guestbook", ["message", "private"], [message, private], where={"id": message_id})
        return {"status": "Message updated"}

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to update this message")


@router.get("/messages/search")
def search_for_messages_by_keyword(search_term: str, num: int = 10,
                                   db: Database = Depends(get_db),
                                   user_id: int = Depends(validate_user)):
    # all public messages + all private messages that contain search_term
    messages = db.get("guestbook",
                      ["id", "message", "private"],
                      where={"private": False},
                      or_where={"private": True, "user_id": user_id},
                      contains={"message": search_term},
                      limit=num)

    return messages


@router.get("/messages/{message_id}")
def get_a_specific_message(message_id: int, db: Database = Depends(get_db),
                           user_id: int = Depends(validate_user)):
    message = db.get_one(
        table="guestbook",
        columns=["id", "user_id", "message", "private", "created_at"],
        where={"id": message_id}
    )

    if (not message) or (message['private'] and message['user_id'] != user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="A public message by that id could not be found")

    # do not return user_id and private
    exclude = ["user_id", "private"]

    return {k: v for k, v in message.items() if k not in exclude}


@router.get("/messages")
def get_all_messages(num: int = 10, db: Database = Depends(get_db), user_id: str = Depends(validate_user)):
    messages = db.get(table="guestbook",
                      columns=["id", "message", "created_at"],
                      where={"private": False},
                      or_where={"private": True, "user_id": user_id},
                      limit=num)

    return messages


@router.delete("/messages/{message_id}")
def delete_a_specific_message(message_id: int,
                              db: Database = Depends(get_db),
                              user_id: str = Depends(validate_user)):
    message = db.get_one("guestbook", ["id", "user_id"], where={"id": message_id})

    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Message was not found")

    if message.get("user_id") == user_id:
        db.delete("guestbook", where={"id": message_id})
        return {"status": "Message deleted"}

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail="You are not allowed to delete this message")
