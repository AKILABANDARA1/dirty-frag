import os
import socket

print("=== Identity ===")
os.system("id")

print("\n=== Kernel ===")
os.system("uname -a")

print("\n=== Capabilities ===")
os.system("capsh --print")

print("\n=== Seccomp ===")
os.system("grep Seccomp /proc/self/status")

print("\n=== Namespace Test ===")
ret = os.system("unshare -Urn true")
print(f"unshare return code: {ret}")

print("\n=== AF_RXRPC Test ===")
try:
    s = socket.socket(socket.AF_RXRPC, socket.SOCK_DGRAM)
    print("AF_RXRPC allowed")
except Exception as e:
    print(f"AF_RXRPC blocked: {e}")

print("\n=== AF_NETLINK Test ===")
try:
    s = socket.socket(socket.AF_NETLINK, socket.SOCK_RAW)
    print("AF_NETLINK allowed")
except Exception as e:
    print(f"AF_NETLINK blocked: {e}")

print("\n=== Loaded Modules ===")
os.system("lsmod | grep -E 'rxrpc|esp4|esp6'")
