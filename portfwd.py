#!/usr/bin/env python3
"""portfwd - TCP port forwarder/proxy."""
import socket, threading, argparse, sys, time

def forward(src, dst, label=''):
    try:
        while True:
            data = src.recv(4096)
            if not data: break
            dst.sendall(data)
    except: pass
    try: src.close()
    except: pass
    try: dst.close()
    except: pass

def handle(client, remote_host, remote_port, connections):
    try:
        remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote.connect((remote_host, remote_port))
        connections['active'] += 1
        connections['total'] += 1
        
        t1 = threading.Thread(target=forward, args=(client, remote, '→'), daemon=True)
        t2 = threading.Thread(target=forward, args=(remote, client, '←'), daemon=True)
        t1.start(); t2.start()
        t1.join(); t2.join()
    except Exception as e:
        sys.stderr.write(f"  Error: {e}\n")
    finally:
        connections['active'] -= 1

def main():
    p = argparse.ArgumentParser(description='TCP port forwarder')
    p.add_argument('local_port', type=int, help='Local port to listen on')
    p.add_argument('remote', help='Remote host:port')
    p.add_argument('-b', '--bind', default='0.0.0.0')
    p.add_argument('-v', '--verbose', action='store_true')
    args = p.parse_args()

    parts = args.remote.split(':')
    remote_host = parts[0]
    remote_port = int(parts[1])

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((args.bind, args.local_port))
    server.listen(50)

    connections = {'active': 0, 'total': 0}
    print(f"Forwarding {args.bind}:{args.local_port} → {remote_host}:{remote_port}")

    try:
        while True:
            client, addr = server.accept()
            if args.verbose:
                print(f"  [{time.strftime('%H:%M:%S')}] Connection from {addr[0]}:{addr[1]} (active: {connections['active']+1})")
            t = threading.Thread(target=handle, args=(client, remote_host, remote_port, connections), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print(f"\nStopped. Total connections: {connections['total']}")
    server.close()

if __name__ == '__main__':
    main()
