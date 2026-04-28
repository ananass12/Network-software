import grpc
import service_pb2 as pb2
import service_pb2_grpc as pb2_grpc

def test_client():
    channel = grpc.insecure_channel('localhost:8174')
    stub = pb2_grpc.LikesServiceStub(channel)
    
    print("1. Создание лайка: ")
    request1 = pb2.CreateLikeRequest(target="post_12345")
    created_like_id = None

    try:
        response = stub.CreateLike(request1)
        created_like_id = response.id
        
        print(" Ответ получен:")
        print(f"   ID лайка: {response.id}")
        print(f"   Цель: {response.target}")
    except grpc.RpcError as e:
        print(f" Ошибка gRPC: {e.details()}")

    print("2. Получение лайка: ")
    request2 = pb2.GetLikeRequest(id=created_like_id)

    try:
        response2 = stub.GetLike(request2)
        
        print(" Ответ получен:")
        print(f"   ID лайка: {response2.id}")
        print(f"   Цель: {response2.target}")
    except grpc.RpcError as e:
        print(f" Ошибка gRPC: {e.details()}")

if __name__ == '__main__':
    test_client()
