from django.contrib import messages
import re

def commonpasswordCheck(password):
        
        if len(password) < 8:
            return "Enter password at least 8 characters"

        if not re.search(r'[A-Z]', password):
            return  "Check if the password contains at least one uppercase letter"
    
        if not re.search(r'[a-z]', password):
            return "Check if the password contains at least one lowercase letter"
    
        if not re.search(r'\d', password):
            return "Check if the password contains at least one digit"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):       
            return "Check if the password contains at least one special character"
        
        return True