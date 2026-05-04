import argparse
from pathlib import Path
from loader import fetch_all

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Live Sun observations")
    parser.add_argument(
        "--output_dir",
        default="./data",
        type=str,
        help="Path to output folder",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)

    observations = fetch_all(output_dir)
    print(observations)
