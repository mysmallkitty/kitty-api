SRC = "0123456789abcdefghijklmnopqrstuv"
DST = "lLpXrkbMmKVIGFECDBz6y4juD0mktnQP"

if len(SRC) != len(DST):
	raise ValueError("SRC와 DST 길이가 다릅니다.")

TRANS = str.maketrans({s: d for s, d in zip(SRC, DST)})

def convert(text: str) -> str:
	return text.translate(TRANS)
while True:
	user_input = input("변환할 문자열을 입력하세요 (종료하려면 'exit' 입력): ")
	if user_input.lower() == 'exit':
		break
	converted = convert(user_input)
	print(f"{converted}")