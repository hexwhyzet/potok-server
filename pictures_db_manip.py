import sqlite3
import base64


# # binary
# c.execute("INSERT INTO images VALUES ({})".format(sqlite3.Binary(file.read())))


def create_db():
    temp_conn = sqlite3.connect('app_db.db')
    temp_c = temp_conn.cursor()
    temp_c.execute('''CREATE TABLE images (image text)''')
    temp_conn.commit()
    temp_conn.close()


def upload_image(image):
    conn = sqlite3.connect('app_db.db')
    c = conn.cursor()
    c.execute("INSERT INTO images (name, image) VALUES ({}{})".format(base64.b64encode(image.read())),)
    conn.commit()
    conn.close()


if __name__ == '__main__':
    # file = open("resources/memes/meme_1.jpg", "br")
    # upload_image(file)
    create_db()