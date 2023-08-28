# LargeGPT Project - An AI-Powered Chatbot

Welcome to the LargeGPT project! This project is an AI-powered chatbot built from scratch by DrDataYE, without utilizing any external API services.

## Installation

To use LargeGPT on your system, follow these steps:

1. Set up a virtual environment using your preferred environment manager (e.g., `virtualenv` or `conda`).
2. Activate the new environment.
3. Install dependencies using the following command:

```bash
pip install -r requirements.txt
```

## Usage

Once the dependencies are installed, you can easily run LargeGPT. Open the `main.py` file and execute the main script. The chatbot will respond to the text you input via the command-line interface.

```bash
python main.py
```





## Installation in colab

1. Clone the repository:
   ```bash
   git clone https://github.com/DrDataYE/LargeGPT.git
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Move the files from the LargeGPT directory to the root:
   ```bash
   mv -if LargeGPT/* .
   ```

## Training

To train the LargeGPT model, run the following command:
```bash
python train.py
```

## Usage

To use the trained LargeGPT model, run the following command:
```bash
python use.py
```

## Dataset

To download and set up the IMDb dataset, run the following commands:
```bash
pip install datasets
python dataset.py -n imdb -o ./data/
```


## Training (Optional)

If you're interested in training your own GPT model, you can follow these steps:

1. Access the OpenAI website and obtain access to their API.
2. Modify the `train.py` file to suit your training needs and strategies.
3. Run the program to start the training process:

```bash
python train.py
```

## Contribution

If you're interested in contributing to the development of LargeGPT, we welcome contributions at all levels! Open a new issue to discuss proposed changes or submit a pull request from relevant branches.

## License

This project is licensed under the [LIM License](). Refer to the [LICENSE](LICENSE) file for more details.

---

LargeGPT was developed by DrDataYE. For inquiries, please contact us at [drdataye@gmail.com](mailto:drdataye@gmail.com) or visit our website [https://www.cyber1101.com](https://www.cyber1101.com).
