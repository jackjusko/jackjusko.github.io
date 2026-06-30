import os
from pypdf import PdfReader

pdf_path = r'z:\github\assets\brute force detection and response lab.pdf'
out_dir = r'z:\github\assets\labs\brute-force'

reader = PdfReader(pdf_path)

slugs = [
    "wazuh-events-count-spike.png",
    "wazuh-attck-credential-access.png",
    "wazuh-rule-filter-5710-5712.png",
    "wazuh-source-ip-event-logs.png",
    "wazuh-sshd-auth-failure-1.png",
    "wazuh-sshd-auth-failure-2.png",
    "hydra-log-pre-active-response.png",
    "wazuh-active-response-config.png",
    "wazuh-no-events-rule-5720.png",
    "wazuh-modified-rule-5551.png",
    "hydra-resume-session-failed.png",
    "wazuh-active-response-blocked.png",
    "wazuh-active-response-in-action.png",
    "wazuh-verification-no-prior-access.png"
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
