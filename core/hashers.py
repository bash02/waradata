import bcrypt
from django.contrib.auth.hashers import BasePasswordHasher
from django.contrib.auth.hashers import make_password, check_password




class MyCustomPasswordHasher():
    algorithm = "bcrypt"

    def salt(self):
        """
        Generate a cryptographically secure nonce salt using bcrypt.
        """
        return bcrypt.gensalt()

    def encode(self, password, salt):
        """
        Create an encoded hash using bcrypt.
        """
        hashed_password = bcrypt.hashpw(password.encode(), salt)
        return hashed_password.decode()

    def verify(self, password, encoded):
        """
        Verify the password against the encoded hash.
        """
        # Decode the encoded hash if it's not already a byte string
        if not isinstance(encoded, bytes):
            encoded = encoded.encode()

        # Use bcrypt to check if the provided password matches the encoded hash
        return bcrypt.checkpw(password.encode(), encoded)

    def safe_summary(self, encoded):
        """
        Return a summary of the hash.
        """
        return {
            "algorithm": self.algorithm,
            "hash": encoded,
        }


# class MyCustomPasswordHasher(BasePasswordHasher):
#     """
#     Custom password hasher implementation using bcrypt.
#     """
#     algorithm = 'bcrypt'  # Specify the algorithm name

#     def encode(self, password, salt):
#         # Generate a bcrypt hashed password
#         hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
#         # Concatenate the salt and hashed password
#         encoded_password = salt + hashed_password
#         return encoded_password.decode(), None  # Return the encoded password and None for salt
    
#     # Implement the verify method to compare the given password with the hashed password
#     def verify(self, password, encoded):
#         # Extract the salt from the encoded password
#         salt = encoded[:29]  # Extract the first 29 characters as the salt
#         # Check if the provided password matches the encoded hashed password
#         return bcrypt.checkpw(password.encode('utf-8'), encoded.encode('utf-8'))

#     # Optionally, implement the safe_summary method to provide information about the hasher
#     def safe_summary(self, encoded):
#         # Provide information about the hasher
#         return {
#             'algorithm': self.algorithm,
#             'iterations': None,  # bcrypt does not use iterations
#             'salt': encoded[:29],  # Salt length of bcrypt
#         }
