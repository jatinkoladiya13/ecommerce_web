from cryptography.fernet import Fernet


key = Fernet.generate_key()
cipher_suite = Fernet(key)



def encrypt(data):
    return cipher_suite.encrypt(data.encode()).decode('utf-8')

def decrypt(data):
    return cipher_suite.decrypt(data.encode()).decode('utf-8')