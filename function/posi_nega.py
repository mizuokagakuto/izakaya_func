from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd
import numpy as np

# 既存モデルの導入
model = AutoModelForSequenceClassification.from_pretrained("jarvisx17/japanese-sentiment-analysis")
tokenizer = AutoTokenizer.from_pretrained("jarvisx17/japanese-sentiment-analysis")
nlp = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# データの読み込み
df = pd.read_excel('fukuoka_izakaya.xlsx')
# 口コミ文字列の長さの出力を追加
df['word_length'] = df['review'].str.len()
#label = []
score = []

# 各レビューに対して感情分析を行う
for serifu in df['review']:
    # 非文字列やNaNのチェック
    if not isinstance(serifu, str) or pd.isna(serifu):
        #label.append(None)
        score.append(None)
        continue  # 次のループに進む

    try:
        # 感情分析の実行
        result = nlp(serifu)
        result = result[0]
        print(result)
        
        if result["label"] == "negative":
            result['score'] = -1 * result['score']
        
        #label.append(result['label'])
        score.append(result['score'])
        
    except RuntimeError as e:
        # 長すぎるレビューのために分割処理
        def split_string(input_string, chunk_size=512):
            return [input_string[i:i + chunk_size] for i in range(0, len(input_string), chunk_size)]
        
        split_serifus = split_string(serifu)
        split_scores = []
        #split_labels = []
        
        for split_serifu in split_serifus:
            split_result = nlp(split_serifu)
            split_result = split_result[0]
            print(split_result)
            
            if split_result["label"] == "negative":
                split_result['score'] = -1 * split_result['score']
            
            #split_labels.append(split_result['label'])
            split_scores.append(split_result['score'])
        
        # 分割結果の平均スコアと代表ラベル
        #label.append(split_labels[0] if len(set(split_labels)) == 1 else "mixed")
        score.append(np.average(split_scores))

# データフレームに結果を追加
#df['label'] = label
df['posi_nega_score'] = score

# store_id_reでグループ化して、posi_nega_scoreの平均を計算
# store_id_reでグループ化して、posi_nega_scoreの平均を計算
# Noneを含む行を除外した平均を計算
result = df.groupby('store_id_re')['posi_nega_score'].apply(lambda x: np.mean([i for i in x if i is not None])).reset_index()

# 結果をExcelファイルとして保存
result.to_excel('posi_nega_score.xlsx', index=False)
print("結果が 'posi_nega_score.xlsx' として保存されました")