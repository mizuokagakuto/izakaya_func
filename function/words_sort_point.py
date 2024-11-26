import pandas as pd

# CSVファイルの読み込み
df = pd.read_excel('fukuoka_izakaya.xlsx')

# 指定キーワードのカテゴリごとのリスト
pickupwords = []#チャットGPTで類義語検索

with open("pickupword.txt", 'r' ,encoding='utf-8') as file:
    for line in file:
        inner_array = list(map(str, line.strip().split(',')))
        pickupwords.append(inner_array)

df_grouped = df.groupby('store_id_re')['review'].apply(lambda reviews: ' '.join(reviews.astype(str))).reset_index()


def count_words_in_text(text, pickupwords):
    counts = []
    for category in pickupwords:
        category_count = sum(text.count(word) for word in category)
        counts.append(category_count)
    return counts


df_grouped['word_counts'] = df_grouped['review'].apply(lambda text: count_words_in_text(text, pickupwords))


category_labels = ['満足指数', '違った指数', 'おしゃれ指数', '落着き指数', 'サービス指数']
df_counts = pd.DataFrame(df_grouped['word_counts'].tolist(), columns=category_labels)

# 結果を結合
df_result = pd.concat([df_grouped['store_id_re'], df_counts], axis=1)



print(df_result)
df_result.to_excel("fukuoka_izakaya_point.xlsx", index = False )