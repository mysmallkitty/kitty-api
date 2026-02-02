SRC = "0123456789abcdefghijklmnopqrstuv"
DST = "lLpXrkbMmKVIGFECDBz6y4juD0mktnQP"

if len(SRC) != len(DST):
	raise ValueError("SRC와 DST 길이가 다릅니다.")

TRANS = str.maketrans({s: d for s, d in zip(SRC, DST)})

def convert(text: str) -> str:
	return text.translate(TRANS)

print(convert("rr00rrrrrrrrrr0rr0000r000800r000rq00808880000800rqqq00800000qq80rq000q02qquuqqq8r00qqu25q252uqqqr0qqr22022022rq02v20ru2222222r0quu2qrruu22uurrq0o2grrrr22urrrrrqoogr22gouuog22rroogguung80pnuu2roogggnnn80nnnnu2rnnoonnn80nnnroorroornnn80nnnrogrrrrrnnn80nnnrog"))