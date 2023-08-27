import argparse
from datasets import load_dataset

def main():
    parser = argparse.ArgumentParser(description="Load a dataset using Hugging Face datasets library")
    parser.add_argument("-n", "--dataset_name", type=str, required=True, help="Name of the dataset")
    parser.add_argument("-o", "--output_path", type=str, required=True, help="Path to save the dataset")

    args = parser.parse_args()

    # تحميل مجموعة البيانات باستخدام اسم المجموعة الذي تم تحديده
    dataset = load_dataset(args.dataset_name)

    # حفظ مجموعة البيانات في المسار المحدد
    dataset.save_to_disk(args.output_path)

    print(f"Dataset {args.dataset_name} has been saved to {args.output_path}")

if __name__ == "__main__":
    main()
