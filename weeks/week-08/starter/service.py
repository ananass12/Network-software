import grpc
from concurrent import futures
import service_pb2 as pb2      
import service_pb2_grpc as pb2_grpc
from uuid import uuid4
import os
import time

likes_storage = {}

class LikesServiceImplementation(pb2_grpc.LikesServiceServicer):
    def CreateLike(self, request, context):
        like_id = str(uuid4())

        likes_storage[like_id] = {
            "target": request.target
        }

        print(f"Лайк для target='{request.target}' - ID={like_id}")
        
        return pb2.CreateLikeResponse(
            id=like_id,
            target=request.target
        )
    def GetLike(self, request, context):
        like_id = request.id
        print(f"Поиск лайка по ID: {like_id}")
        
        if like_id in likes_storage:
            data = likes_storage[like_id]

            return pb2.GetLikeResponse(
                id=like_id,
                target=data["target"]
            )
        else:
            print(f"Лайк {like_id} не найден")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Лайк {like_id} не найден")
            return pb2.GetLikeResponse()

    def SubscribeLikes(self, request, context):
        """Server streaming: несколько обновлений по подписке на target."""
        for i in range(10):
            yield pb2.LikeUpdate(
                like_id=f"like_{i}",
                target=request.target,
                timestamp=int(time.time() * 1000),
            )

def serve(port: int = 8174):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_LikesServiceServicer_to_server(
        LikesServiceImplementation(),
        server
    )
    server.add_insecure_port(f'[::]:{port}')
    print(f"likes-svc-s18 запущен на :{port}")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve(int(os.getenv("GRPC_PORT", "8174")))
