import json

with open(r'storage/Bredberi_Marsianskie_hroniki.json', encoding='utf-8') as file:
    content: dict = json.load(file)
    content_str: str = json.dumps(content)

query: str = '''
INSERT INTO books
(name, content)
VALUES (%s, %s)
'''
values: tuple = ('📖 Ray Bradbury `The Martian Chronicles`', content_str)
