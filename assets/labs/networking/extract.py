import os
from pypdf import PdfReader

pdf_path = r'z:\github\assets\Networking Lab.pdf'
out_dir = r'z:\github\assets\labs\networking'

reader = PdfReader(pdf_path)

slugs = [
    "vmware-lan-network-config.png",
    "victim-apache-install.png",
    "suricata-wazuh-agent-install.png",
    "wazuh-suricata-nmap-alerts.png",
    "kali-gobuster-results.png",
    "wazuh-nmap-signature-alert.png",
]

img_idx = 0
for i, page in enumerate(reader.pages):
    imgs = getattr(page, 'images', None) or []
    for j, img in enumerate(imgs):
        slug = slugs[img_idx]
        out_path = os.path.join(out_dir, slug)
        with open(out_path, "wb") as f:
            f.write(img.data)
        print(f"Extracted page {i+1} image {j+1} -> {slug}")
        img_idx += 1

print(f"Total extracted: {img_idx}")
