"""
Сравнение: 1000 unary REST (POST) vs 1000 unary gRPC (CreateLike).
Перед запуском: docker compose up -d (порты 8080 REST, 8174 gRPC).
"""
import time

import grpc
import requests
import service_pb2 as pb2
import service_pb2_grpc as pb2_grpc

REST_URL = "http://127.0.0.1:8080/api/likes"
GRPC_TARGET = "127.0.0.1:8174"
N = 1000


def benchmark_rest(n: int = N) -> float:
    session = requests.Session()
    payload = {"target": "post_123"}
    start = time.perf_counter()
    for _ in range(n):
        session.post(REST_URL, json=payload, timeout=30)
    return time.perf_counter() - start


def benchmark_grpc(n: int = N) -> float:
    channel = grpc.insecure_channel(GRPC_TARGET)
    stub = pb2_grpc.LikesServiceStub(channel)
    req = pb2.CreateLikeRequest(target="post_123")
    start = time.perf_counter()
    for _ in range(n):
        stub.CreateLike(req)
    channel.close()
    return time.perf_counter() - start


if __name__ == "__main__":
    t_rest = benchmark_rest()
    t_grpc = benchmark_grpc()
    print(f"REST {N} POST /api/likes: {t_rest:.3f} s")
    print(f"gRPC {N} CreateLike:        {t_grpc:.3f} s")