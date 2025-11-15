import requests
import time
import unicodedata
import os
import hashlib


VIRUSTOTAL_API_KEY = "5ba3b3678cedd28dd5fb041e8ee00801a8bd32a862870931c3331a4b4fa13bd5"

def normalize_filename(filename):
    return unicodedata.normalize("NFKD", filename).encode("ascii", "ignore").decode("ascii")

def scan_file_with_virustotal(file_path):

    upload_url = "https://www.virustotal.com/api/v3/files"
    headers = {"x-apikey": VIRUSTOTAL_API_KEY}

    original_name = os.path.basename(file_path)
    safe_name = normalize_filename(original_name) or "file.bin"

    print("== DOSYA YÜKLENİYOR ==")

    # ------------------------------------------------------
    # 1) FILE UPLOAD
    # ------------------------------------------------------
    with open(file_path, "rb") as f:
        files = {"file": (safe_name, f)}
        upload_json = requests.post(upload_url, headers=headers, files=files).json()

    print("UPLOAD JSON:", upload_json)

    if "data" not in upload_json:
        return False, {
            "error": "Upload hatası",
            "detail": upload_json
        }

    analysis_id = upload_json["data"]["id"]
    analysis_url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"

    print("== ANALIZ SORGULANIYOR ==")

    # ------------------------------------------------------
    # 2) ANALYSIS LOOP – COMPLETED OLAN KADAR BEKLE
    # ------------------------------------------------------
    for _ in range(25):  # 25 sn’ye kadar bekler
        resp = requests.get(analysis_url, headers=headers).json()
        print("ANALYSIS JSON:", resp)

        data = resp.get("data", {})
        attributes = data.get("attributes", {})
        status = attributes.get("status")

        # SHA256 her zaman meta altında geliyor
        sha256 = resp.get("meta", {}).get("file_info", {}).get("sha256")

        # QUEUED → beklemeye devam
        if status == "queued":
            time.sleep(1)
            continue

        # COMPLETED → sonuçları oku
        if status == "completed":

            stats = attributes.get("stats", {})
            is_malicious = stats.get("malicious", 0) > 0

            return is_malicious, {
                "sha256": sha256,
                "status": status,
                "stats": stats,
                "results": attributes.get("results", {})
            }

        time.sleep(1)

    # ------------------------------------------------------
    # 3) TIMEOUT – analiz bitmedi
    # ------------------------------------------------------
    return False, {
        "sha256": None,
        "status": "timeout",
        "stats": {},
        "results": {}
    }
import hashlib

def get_sha256(scan_result):
    """
    scan_result = {"sha256": "..."} veya {"data": {"attributes": {"sha256": "..."}}}
    şeklinde olabilir, hepsini karşılar.
    """
    if not scan_result:
        return ""

    # VirusTotal modern API formatı
    try:
        return scan_result["data"]["attributes"]["sha256"]
    except:
        pass

    # Eğer scan_result direkt sha256 içeriyorsa
    if "sha256" in scan_result:
        return scan_result["sha256"]

    # Eğer dosya hash’i yok, kendin hesaplamak istersen:
    if isinstance(scan_result, bytes):
        return hashlib.sha256(scan_result).hexdigest()

    return ""
