import sys

def main():
    country = input("Enter country name: ") if len(sys.argv) < 2 else sys.argv[1]
    print(f"Country: {country}")

if __name__ == "__main__":
    main()
