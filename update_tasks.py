import re

with open("/home/akihito-kasai/.gemini/antigravity/brain/44a6c132-cd64-40bc-8e11-0505fb90f8d0/task.md", "r") as f:
    code = f.read()

code = code.replace("- [ ]", "- [x]")

with open("/home/akihito-kasai/.gemini/antigravity/brain/44a6c132-cd64-40bc-8e11-0505fb90f8d0/task.md", "w") as f:
    f.write(code)

print("Tasks updated")
