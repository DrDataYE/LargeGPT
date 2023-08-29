import torch
from train import BigramLanguageModel
from utils import encode, decode, text_standardize
import torch
from rich.console import Console
import argparse

console = Console()

# Create an argument parser
parser = argparse.ArgumentParser(description='Generate Text using the Bigram Language Model')

# Add an argument for the input text
parser.add_argument('--input', type=str, required=True, help='Input text for text generation')

# Parse the command line arguments
args = parser.parse_args()
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
console.print("\n\nWelcome To LargeGPT v1\n\n", style="bold green",justify="center")
while True:
    user_input = console.input("[bold][green]>")
    if user_input.lower() == "quit":
        break

    generated_text = generate_text(user_input, max_tokens=200, temperature=0.5)

    console.print("Generated text",style="bold",justify="center")
    console.print(generated_text)
