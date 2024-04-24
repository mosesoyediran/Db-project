- a web-based API serving json and using postgres as the persistence layer
- will support user registration and authentication using HTTP Basic Auth
- queries will be dynamically generated at runtime uisng a Database type that we'll define (an OOP approach)
- users will be able to post messages, update and delete them, vote on other users public messages and more
- project will be deployed to the web at zero cost

uvicorn main:app --reload
