from ollama import chat

res = chat(
    model='gpt-oss:20b',
    messages=[
        {'role': 'system', 'content': 'あなたは有能なPythonアシスタントです'},
        {'role': 'user', 'content': 'Pythonでフィボナッチ数列を生成する関数を書いてください。'}
    ],
    # ここで推論パラメータを制御
    options={
        'num_ctx': 8192,       # コンテキスト長
        'temperature': 0.7,    # 生成の多様性
        'num_predict': 51200     # 生成トークン上限
    }
)
print(res.message.conten)
