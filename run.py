import socket
import subprocess
import re
import runpy

# 1. Global Termux DNS Fix Layer
_orig_getaddrinfo = socket.getaddrinfo
def custom_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    try:
        return _orig_getaddrinfo(host, port, family, type, proto, flags)
    except socket.gaierror as e:
        if e.errno == 7 or "No address" in str(e):
            try:
                # Routes the lookup through your working system shell tool
                proc = subprocess.Popen(["ping", "-c", "1", "-W", "2", host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, _ = proc.communicate()
                match = re.search(r"\(([\d\.]+)\)", stdout.decode(errors="ignore"))
                if match:
                    return _orig_getaddrinfo(match.group(1), port, family, type, proto, flags)
            except Exception:
                pass
        raise e

socket.getaddrinfo = custom_getaddrinfo

# 2. Launch your original framework with the patch globally active
if __name__ == "__main__":
    print("[SYSTEM] Global DNS Network Layer Armed Successfully.")
    runpy.run_path("main.py", run_name="__main__")
