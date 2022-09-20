import io
import json
import pickle
import torch
import numpy as np

from flask_cors import CORS
from flask import Flask, jsonify, request

PATH = '/home/ubuntu/project/9oormthon_name_in_jeju/model/9oormthon'
## 만약 CPU 로 작업하는 경우에는 밑에 두개 주석을 해제하세요!
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print("log : device is {}".format(device))
models = torch.load(PATH+'model.pt',map_location=device)  # 전체 모델을 통째로 불러옴, 클래스 선언 필수
print("log : load model")
#models.load_state_dict(torch.load(PATH + 'model_state_dict.pt', map_location=device))  # state_dict를 불러 온 후, 모델에 저장
print("log : load state dict model")
# models.to(device)

#제주어 사전 가져오기 (표준 -> 제주)
path = '/home/ubuntu/project/9oormthon_name_in_jeju/model/jeju_dict_t2.pkl'
with open(path,'rb') as f:
  jeju_dict_t = pickle.load(f)

print("log : load jejuword dict")
words = list(jeju_dict_t.keys())

#사전에 있는 한국어 데이터셋을 가져온다.
document_embeddings = np.load(PATH+"_embeddings.npy")

app = Flask(__name__)
CORS(app)


m = ['자국떼다', '신관', '남소왕이', '욜다', '풀돋잇마', '고막곶', '바당이영', '건들마', '벨롱겡이', '곳다', '끙물다변', '속도']

d = ['옵서', '날봅서', '천성', '올르다', '뒈게', '영낙읏이', '아며도', '심껏', '반시', '침내', '놀놀', '느런히', '엇다', '어중구랑', '아깝다', '조금사리', '히뜨거니', 
     '랑지다', '디다', '벨다', '멩글다', '흘르다', '헤우다', '벨라지다', '라메다', '귀애하다', '심들다', '속다', '섭력다', '디긋다', '부끄리다']

def cos_sim(a, b):
    """
    Computes the cosine similarity cos_sim(a[i], b[j]) for all i and j.
    :return: Matrix with res[i][j]  = cos_sim(a[i], b[j])
    """
    if not isinstance(a, torch.Tensor):
        a = torch.tensor(a)

    if not isinstance(b, torch.Tensor):
        b = torch.tensor(b)

    if len(a.shape) == 1:
        a = a.unsqueeze(0)

    if len(b.shape) == 1:
        b = b.unsqueeze(0)

    a_norm = torch.nn.functional.normalize(a, p=2, dim=1)
    b_norm = torch.nn.functional.normalize(b, p=2, dim=1)
    return torch.mm(a_norm, b_norm.transpose(0, 1))
def jej_trans_t(text):
  result = []
  for t in text.split():
    if t in jeju_dict_t:
      t = jeju_dict_t[t]
      result.append(t)
    else:
      result.append(t)
  return result
def NameInJeju_t(text):
  query = text
  query_embedding = models.encode(query,device=device)

  #입력 단어 - 후보군 단어간 유사도 계산
  top_k = min(5, len(words))

  # 입력 단어 - 문장 단어간 코사인 유사도 계산 후,
  cos_scores = cos_sim(query_embedding, document_embeddings)[0]

  # 코사인 유사도 순으로 'top_k' 개 단어 추출
  top_results = torch.topk(cos_scores, k=top_k)

  # print(f"입력 단어: {query}")
  # print(f"\n<입력 단어와 유사한 {top_k} 개의 단어>\n")
  answer = []
  for i, (score, idx) in enumerate(zip(top_results[0], top_results[1])):
    x = words[idx]
    answer.append(x)
      
  result = jej_trans_t(answer[0])
  show = answer[0]
  result = jej_trans_t(show)

  if result == text:
    show = answer[1]
    result = jej_trans_t(show)

  return result

def Jeju_name_md(nm,nd):
  return [m[int(nm)-1],d[int(nd)-1]]

@app.route('/birthtransfer',methods = ['POST', 'GET'])
def post_birth():
    if request.method == 'POST':
       print(request.data.decode('utf-8')[1:-1].split(","))
       nm,nd = request.data.decode('utf-8')[1:-1].split(",")
    with open('../count_people','r') as f:
        data = int(f.readline())
    with open('../count_people','w') as f:
        f.write(str(data+1))
    print("logging : count => {}".format(data))

    return Jeju_name_md(nm,nd)


@app.route('/transfer',methods = ['POST', 'GET'])
def post_transfer():
    print(request.data)
    if request.method == 'POST':
        res = list()
        for _ in request.data.decode('utf-8')[2:-2].split("\",\""):
            res += NameInJeju_t(_)

    with open('../count_people','r') as f:
        data = int(f.readline())
    with open('../count_people','w') as f:
        f.write(str(data+1))
    print("logging : count => {}".format(data))
    return res


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4500) 
