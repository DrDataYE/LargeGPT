import torch
from train import BigramLanguageModel
from utils import encode, decode, text_standardize
import torch


# Define the BigramLanguageModel class and other necessary components as before

# Set hyperparameters
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Load the saved model from the binary file
model = BigramLanguageModel()
model.load_state_dict(torch.load(
    'trained_model.bin', map_location=device))
model.to(device)
model.eval()


def generate_text(prompt, max_tokens=200, temperature=0.7):
    encoded_prompt = torch.tensor(
        encode(prompt), dtype=torch.long, device=device).unsqueeze(0)
    generated_tensor = model.generate(
        encoded_prompt, max_new_tokens=max_tokens, temperature=temperature)[0]
    generated_text = decode(generated_tensor.tolist())
    return generated_text


while True:
    user_input = input(">")
    if user_input.lower() == "quit":
        break

    generated_text = generate_text(text_standardize(user_input), max_tokens=200, temperature=0.5)

    print("Generated text:")
    print(generated_text)
