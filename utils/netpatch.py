import os
import socket
import subprocess
import re

"""Optional network monkeypatch helper.

Enable by setting environment variable ENABLE_NETWORK_PATCH=1
This implements a limited fallback for systems with broken DNS lookups.
Use only for constrained environments - disabled by default.
"""

def enable_patch():
    # Small defensive guard: only enable when explicitly requested
    if os.environ.get("ENABLE_NETWORK_PATCH", "0") != "1":
        return

    _orig_getaddrinfo = socket.getaddrinfo

    def _custom_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        # Pass numeric IPs through instantly
        if host and isinstance(host, str) and re.match(r'^\d+\.\d+\.\d+\.\d+$', host):
            return [(socket.AF_INET, socket.SOCK_STREAM, proto, '', (host, int(port)))]

        try:
            return _orig_getaddrinfo(host, port, family, type, proto, flags)
        except socket.gaierror as e:
            # Try a shell ping lookup fallback (best-effort) for constrained mobile environments
            try:
                proc = subprocess.Popen(["ping", "-c", "1", "-W", "2", host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, _ = proc.communicate()
                match = re.search(r"\(([\n                    \d\.]+)\)", stdout.decode(errors='ignore')) if stdout else None
                if match:
                    return _orig_getaddrinfo(match.group(1), port, family, type, proto, flags)
            except Exception:
                pass
        # Re-raise the original error if fallback didn't work
        raise e

    socket.getaddrinfo = _custom_getaddrinfo
