import requests

def download_img(image_src):
    """
    Download img from image_src.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://tcgrepublic.com/",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8"
        }
        # set timeout to prevent indefinite request
        res = requests.get("https://" + image_src, timeout=10, headers=headers)

        # raise HTTPError for bad responses
        res.raise_for_status()

        # check that the response is an image
        if "image" not in res.headers.get("Content-Type", ""):
            raise ValueError("URL did not return an image.")
        return res.content
    except requests.exceptions.RequestException as e:
        print(f"Network error when downloading image from {image_src}: {e}")
    except Exception as e:
        print(f"Non-network error when downloading image from {image_src}: {e}")

def upload_img_to_s3(bucket, item, image_src):
    """
    Upload img to s3.
    """
    card_id = item["card_id"]
    set_name = item["set_name"]
    tcg_name = item["tcg_name"]
    key = f"card-images/{tcg_name}/{set_name}/{card_id}.jpg"
    
    img_data = download_img(image_src)
    if img_data:
        try:
            bucket.put_object(Body=img_data, Key=key, ContentType="image/jpeg")
            return key
        except Exception as e:
            print(f"Failed to upload to S3: {e}")
    return None