from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

from django.utils.crypto import pbkdf2
import hashlib
from  base64 import b64decode

identity_PasswordHash = "AOOVvPns8Nov6CsJDTAWz+QDOEO2csh60m5aYyX2Vn7LsNDhiiZ5UaSDWr5izwWeHA=="
pwd_plain = 'Hellow123'


def dotnet_identity_check_password(password, hash):
    binsalt = b64decode(hash)[1:17]
    binpwd = b64decode(hash)[17:]
    genpwd = pbkdf2(password, binsalt, 1000, digest=hashlib.sha1, dklen=32)
    if genpwd == binpwd:
       return True
    return False

if dotnet_identity_check_password(pwd_plain,identity_PasswordHash):
     print("OK")
else:
     print("Fail")


# class CustomPBKDF2Backend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         UserModel = get_user_model()
#         try:
#             user = UserModel.objects.get(username=username)
#         except UserModel.DoesNotExist:
#             return None
#         if your_custom_hashing_module.verify(password, user.password):  # Используйте вашу функцию проверки хэша
#             return user
#     def get_user(self, user_id):
#         UserModel = get_user_model()
#         try:
#             return UserModel.objects.get(pk=user_id)
#         except UserModel.DoesNotExist:
#             return None


