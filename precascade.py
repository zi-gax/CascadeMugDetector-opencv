import os
import time
import requests
import hashlib
import xml.etree.ElementTree as ET
from playwright.sync_api import sync_playwright

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# --------- GOOGLE IMAGES SCRAPER ---------
def google_images_scraper():
    QUERY = input("🔹 Enter search query for Google Images: ")
    TARGET_COUNT = int(input("🔹 Enter number of images to download: "))

    SAVE_DIR = input("Enter folder to save images (default=image_downloaded): ") or "image_downloaded"
    os.makedirs(SAVE_DIR, exist_ok=True)

    SCROLL_PAUSE = 2
    SCROLL_STEP = 3000
    MAX_RETRIES = 5
    RETRY_WAIT = 10
    TIMEOUT = 20

    def downloaded_count():
        return len([f for f in os.listdir(SAVE_DIR) if f.endswith(".jpg")])

    def download_with_retry(url, path):
        for i in range(1, MAX_RETRIES + 1):
            try:
                r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "Mozilla/5.0"})
                r.raise_for_status()
                with open(path, "wb") as f:
                    f.write(r.content)
                return True
            except Exception as e:
                print(f"⚠️ retry {i}/{MAX_RETRIES} for {url} — {e}")
                time.sleep(RETRY_WAIT)
        return False

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            executable_path=CHROME_PATH,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.new_page()
        page.goto(f"https://www.google.com/search?q={QUERY}&tbm=isch&tbs=isz:l", timeout=60000)
        print("🔎 Google Images loaded")

        collected_urls = set()
        last_height = 0

        while downloaded_count() < TARGET_COUNT:
            imgs = page.query_selector_all("img")
            for img in imgs:
                try:
                    src = img.get_attribute("data-iurl") or img.get_attribute("data-src") or img.get_attribute("src")
                    if not src or not src.startswith("http") or src in collected_urls:
                        continue
                    collected_urls.add(src)
                    idx = downloaded_count() + 1
                    path = f"{SAVE_DIR}/{QUERY}_{idx}.jpg"
                    if os.path.exists(path):
                        continue
                    if download_with_retry(src, path):
                        print(f"✅ {idx}/{TARGET_COUNT}")
                    if downloaded_count() >= TARGET_COUNT:
                        break
                except:
                    continue

            page.mouse.wheel(0, SCROLL_STEP)
            time.sleep(SCROLL_PAUSE)
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                print("📌 No more new images loaded, stopping scroll")
                break
            last_height = new_height

        browser.close()
    print(f"🎉 Google download complete! Images saved in: {SAVE_DIR}")


# --------- PIXABAY SCRAPER ---------
def pixabay_scraper():
    API_KEY = input("🔹 Enter your Pixabay API key: ")
    QUERY = input("🔹 Enter search query for Pixabay: ")
    TOTAL_IMAGES = int(input("🔹 Enter number of images to download: "))
    PER_PAGE = 200

    SAVE_DIR = input("Enter folder to save images (default=image_downloaded): ") or "image_downloaded"
    os.makedirs(SAVE_DIR, exist_ok=True)

    existing_files = [f for f in os.listdir(SAVE_DIR) if f.endswith(".jpg")]
    downloaded = len(existing_files)
    page_num = downloaded // PER_PAGE + 1
    print(f"🔁 Resume from image {downloaded + 1}, page {page_num}")

    while downloaded < TOTAL_IMAGES:
        url = f"https://pixabay.com/api/?key={API_KEY}&q={QUERY}&image_type=photo&per_page={PER_PAGE}&page={page_num}"
        response = requests.get(url).json()
        hits = response.get("hits", [])

        if not hits:
            print("❌ Can't find more photos.")
            break

        for img in hits:
            if downloaded >= TOTAL_IMAGES:
                break
            file_path = os.path.join(SAVE_DIR, f"{QUERY}_{downloaded + 1}.jpg")
            if os.path.exists(file_path):
                downloaded += 1
                continue
            img_url = img["largeImageURL"]
            img_data = requests.get(img_url).content
            with open(file_path, "wb") as f:
                f.write(img_data)
            downloaded += 1
            print(f"✅ {downloaded}/{TOTAL_IMAGES}")

        page_num += 1
        time.sleep(1)
    print(f"🎉 Pixabay download complete! Images saved in: {SAVE_DIR}")


# --------- REMOVE DUPLICATES ---------
def remove_duplicates():
    folder_path = input("🔹 Enter folder path (default=image_downloaded): ") or "image_downloaded"
    DELETE = input("Delete duplicates? (y/n): ").lower() == "y"

    def hash_file(filepath):
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()

    hashes = {}
    duplicates = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                file_path = os.path.join(root, file)
                file_hash = hash_file(file_path)
                
                if file_hash in hashes:
                    duplicates.append(file_path)
                    if DELETE:
                        os.remove(file_path)
                        print(f"Deleted duplicate: {file_path}")
                else:
                    hashes[file_hash] = file_path

    if not DELETE:
        print("Duplicate images found:")
        for dup in duplicates:
            print(dup)
    print("✅ Duplicate check complete!")


# --------- RENAME IMAGES ONLY  ---------
def rename_images():
    folder_path = input(f"🔹 Enter folder path (default=image_downloaded): ") or "image_downloaded"
    prefix = input("Prefix for new filenames: ") or "img_"
    start_index = int(input("Starting index: ") or 1)
    num_digits = int(input("Number of digits (e.g., 3 for 001): ") or 3)

    files = os.listdir(folder_path)
    files.sort()
    index = start_index

    for file_name in files:
        old_path = os.path.join(folder_path, file_name)
        if not os.path.isfile(old_path):
            continue

        name, ext = os.path.splitext(file_name)
       
        if ext.lower() not in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
            continue

        new_name = f"{prefix}{str(index).zfill(num_digits)}{ext}"
        new_path = os.path.join(folder_path, new_name)

        os.rename(old_path, new_path)
        print(f"Renamed: {file_name} -> {new_name}")

        index += 1
    print("✅ Rename images complete! Don't forget to rename XML files if needed.")

# --------- GENERATE POSITIVES.TXT ---------
def generate_positives_txt():
    folder = input("🔹 Enter folder path with XML files (default=image_downloaded): ") or "image_downloaded"
    output_file = input("Output file name (default=positives.txt): ") or "positives.txt"

    with open(output_file, "w") as f:
        for xml_file in os.listdir(folder):
            if not xml_file.endswith(".xml"):
                continue
            tree = ET.parse(os.path.join(folder, xml_file))
            root = tree.getroot()
            filename = root.find("filename").text
            img_path = os.path.join(folder, filename)

            objects = root.findall("object")
            if not objects:
                continue

            line = f"{img_path} {len(objects)}"
            for obj in objects:
                bndbox = obj.find("bndbox")
                xmin = int(bndbox.find("xmin").text)
                ymin = int(bndbox.find("ymin").text)
                xmax = int(bndbox.find("xmax").text)
                ymax = int(bndbox.find("ymax").text)

                w = xmax - xmin
                h = ymax - ymin

                line += f" {xmin} {ymin} {w} {h}"
            f.write(line + "\n")

    print(f"✅ {output_file} generated for OpenCV!")

# --------- GENERATE NEGATIVES.TXT ---------
def generate_negatives_txt():
    folder = input("🔹 Enter folder path with negative images (default=negative): ") or "negative"
    output_file = input("Output file name (default=negatives.txt): ") or "negatives.txt"

    with open(output_file, "w") as f:
        for file_name in os.listdir(folder):
            file_path = os.path.join(folder, file_name)
            if os.path.isfile(file_path) and file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                f.write(file_path + "\n")

    print(f"✅ {output_file} generated for OpenCV!")

# --------- SUGGEST WIDTH/HEIGHT FOR opencv_createsamples ---------
def suggest_sample_size():
    info_file = input("🔹 Enter positives.txt path (default=positives.txt): ") or "positives.txt"

    try:
        widths = []
        heights = []

        with open(info_file, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 2:
                    continue
                num_objects = int(parts[1])
                for i in range(num_objects):
                    x = int(parts[2 + i*4])
                    y = int(parts[3 + i*4])
                    w = int(parts[4 + i*4])
                    h = int(parts[5 + i*4])
                    widths.append(w)
                    heights.append(h)

        if not widths or not heights:
            print("❌ No bounding boxes found in the file.")
            return

        avg_w = sum(widths) / len(widths)
        avg_h = sum(heights) / len(heights)

        suggest_w = round(avg_w / 5)
        suggest_h = round(avg_h / 5)

        print(f"📏 Real mean bounding box: width={avg_w:.1f}, height={avg_h:.1f}")
        print(f"💡 Suggested size for opencv_createsamples: -w {suggest_w} -h {suggest_h}")

    except FileNotFoundError:
        print(f"❌ File not found: {info_file}")
    except Exception as e:
        print(f"❌ Error: {e}")

# --------- MAIN MENU ---------
def main_menu():
    while True:
        print("\n=== Image Manager Menu ===")
        print("1. Download images from Google")
        print("2. Download images from Pixabay")
        print("3. Remove duplicate images")
        print("4. Rename images + XML")
        print("5. Generate positives.txt from XMLs")
        print("6. Generate negatives.txt from negative images")
        print("7. Suggest size for opencv_createsamples")
        print("8. Exit")

        choice = input("Enter your choice (1-8): ")
        if choice == "1":
            google_images_scraper()
        elif choice == "2":
            pixabay_scraper()
        elif choice == "3":
            remove_duplicates()
        elif choice == "4":
            rename_images()
        elif choice == "5":
            generate_positives_txt()
        elif choice == "6":
            generate_negatives_txt()
        elif choice == "7":
            suggest_sample_size()
        elif choice == "8":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice, try again.")


if __name__ == "__main__":
    main_menu()