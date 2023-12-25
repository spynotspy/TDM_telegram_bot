import yadisk
from TOKENS import Y_TOKEN, Y2_TOKEN


def upload_on_disk():
    disk = yadisk.YaDisk(token=Y2_TOKEN)
    disk.upload("mystery_santa.db", "/mystery_santa.db")
