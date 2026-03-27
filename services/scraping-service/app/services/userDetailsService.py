import bcrypt
import jwt

# functions used to encrypt & decrypt the users password before storing it in the database.
async def encryptPassword(password: str) -> bytes:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password
    
# function used to check if the provided password matches the hashed password.
async def verifyPassword(passwordHash, plainPassword) -> bool:
    password_byte_enc = plainPassword.encode('utf-8')
    return bcrypt.checkpw(password= password_byte_enc, hashed_password = passwordHash)


async def getEmailFromJwt(authHeader) -> str:
    token = authHeader[1]    
    decodedToken = jwt.decode(token, options={"verify_signature": False}) 
    user_email = decodedToken["email"]

    return user_email

async def getIdFromJwt(authHeader) -> int:
    token = authHeader[1]    
    decodedToken = jwt.decode(token, options={"verify_signature": False}) 
    user_id = decodedToken["ID"]

    return user_id
