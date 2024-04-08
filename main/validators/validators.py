import re

from app.model import User

class Validators:
    @staticmethod
    def check_user_required_fields(data_dct):
        mandatory_field = ["username", "password", "email"]
        for data in mandatory_field:
            if data not in data_dct or not data_dct[data]:
                return {"status": 400, "message": f"{data} is required"}
        
        email_validation = r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$'
        if not re.match(email_validation, data_dct.get('email', '')):
            return {"status": 400, "message": "Enter a valid email"}
        
        return {"status": 200, "message": "Validation successful"}

    @staticmethod
    def check_login_required_fields(data_dct):
        mandatory_field = ["username", "password"]
        for data in mandatory_field:
            if data not in data_dct or not data_dct[data]:
                return {"status": 400, "message": f"{data} is required"}
        return {"status": 200, "message": "Validation successful"}

    @staticmethod
    def check_profile_update_required_fields(data_dct):
        mandatory_field_lst = ["username", "email"]
        for field in mandatory_field_lst:
            if field not in data_dct or not data_dct[field]:
                return {"status": 400, "message": f"{field} is required"}
        return {"status": 200, "message": "Validation successful"}
    
    @staticmethod
    def validate_comment_data(data):
        if 'content' not in data or not data['content']:
            return {"status": 400, "message": "Content is required"}
        return {"status": 200, "message": "Validation successful"}

    @staticmethod
    def validate_comment_delete(comment, current_user_id):
        if not comment:
            return {"status": 404, "message": "Comment not found"}
        if comment.user_id != current_user_id:
            return {"status": 403, "message": "You are not authorized"}
        return {"status": 200, "message": "Validation successful"}
    

    @staticmethod
    def validate_user_id(user_id):
        if not isinstance(user_id, int) or user_id <= 0:
            return {"status": 400, "message": "Invalid user ID"}
        if not User.query.get(user_id):
            return {"status": 404, "message": "User not found"}
        return {"status": 200, "message": "Validation successful"}
    
    @staticmethod
    def validate_user_id(user_id):
        if not isinstance(user_id, int) or user_id <= 0:
            return {"status": 400, "message": "Invalid user ID"}
        if not User.query.get(user_id):
            return {"status": 404, "message": "User not found"}
        return {"status": 200, "message": "Validation successful"}

    @staticmethod
    def validate_message_content(content):
        if not content:
            return {"status": 400, "message": "Message content is required"}
        return {"status": 200, "message": "Validation successful"}
    
    @staticmethod
    def validate_post_content(content):
        if not content:
            return {"status": 400, "message": "Post content is required"}
        return {"status": 200, "message": "Validation successful"}

