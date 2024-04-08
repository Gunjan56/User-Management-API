from werkzeug.security import (generate_password_hash)

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extensions

def secure_password(password):
    return generate_password_hash(password)    
