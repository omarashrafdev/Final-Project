from hashlib import md5

id = "0"

hash_object = md5(id.encode()).hexdigest()

print(hash_object)