import requests

r = requests.get("https://edu2review.com/chuong-trinh-dao-tao-trinh-do-dai-hoc-tai-viet-nam-23736")

print(r.text)
# for txt in r:
#     print(txt.text)
