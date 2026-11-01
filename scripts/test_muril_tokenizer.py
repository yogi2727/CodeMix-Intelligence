
from transformers import AutoTokenizer

MODEL_ID = "google/muril-base-cased"

print("Loading MuRIL tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_ID,
    use_fast=False
)

samples = {
    "English": "Today I am going to college.",

    "Hindi native":
        "\u0906\u091c \u092e\u0948\u0902 \u0915\u0949\u0932\u0947\u091c \u091c\u093e \u0930\u0939\u093e \u0939\u0942\u0901\u0964",

    "Telugu native":
        "\u0c28\u0c47\u0c28\u0c41 \u0c08\u0c30\u0c4b\u0c1c\u0c41 \u0c15\u0c3e\u0c32\u0c47\u0c1c\u0c40\u0c15\u0c3f \u0c35\u0c46\u0c33\u0c4d\u0c24\u0c41\u0c28\u0c4d\u0c28\u0c3e\u0c28\u0c41.",

    "English + Hindi":
        "Aaj college mein assignment submit karna hai.",

    "English + Telugu":
        "Nenu today college ki velthunnanu.",

    "Hindi + Telugu":
    "\u0906\u091c \u0c28\u0c47\u0c28\u0c41 college \u0c15\u0c3f \u0c35\u0c46\u0c33\u0c4d\u0c24\u0c41\u0c28\u0c4d\u0c28\u0c3e\u0c28\u0c41.",

    "All three":
    "Today \u092e\u0948\u0902 college \u0c15\u0c3f \u0c35\u0c46\u0c33\u0c4d\u0c24\u0c41\u0c28\u0c4d\u0c28\u0c3e\u0c28\u0c41.",
}

print("\nTokenizer:", type(tokenizer).__name__)

for category, sentence in samples.items():

    tokens = tokenizer.tokenize(sentence)

    unknown_count = tokens.count(tokenizer.unk_token)

    print("\n" + "=" * 55)
    print("CATEGORY:", category)
    print("INPUT:", ascii(sentence))
    print("TOKENS:", [ascii(token) for token in tokens])
    print("TOTAL TOKENS:", len(tokens))
    print("UNKNOWN TOKENS:", unknown_count)

print("\nTokenization test completed!")
