
from transformers import AutoConfig

MODEL_ID = "google/muril-base-cased"

print("Checking MuRIL model configuration...")

config = AutoConfig.from_pretrained(MODEL_ID)

print("\nMODEL DETAILS")
print("-------------------------")
print("Model ID:", MODEL_ID)
print("Model type:", config.model_type)
print("Architecture:", config.architectures)
print("Hidden size:", config.hidden_size)
print("Transformer layers:", config.num_hidden_layers)
print("Attention heads:", config.num_attention_heads)
print("Vocabulary size:", config.vocab_size)
print("Maximum sequence length:", config.max_position_embeddings)

assert config.model_type == "bert"
assert config.hidden_size > 0
assert config.num_hidden_layers > 0

print("\nMuRIL configuration verified successfully!")
