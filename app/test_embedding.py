from embedding import create_embedding


text = "DocuMind projesinde ilk embedding testimizi yapıyoruz."

vector = create_embedding(text)

print("Embedding başarıyla oluşturuldu!")
print("Vektör boyutu:", len(vector))
print("İlk 5 değer:", vector[:5])