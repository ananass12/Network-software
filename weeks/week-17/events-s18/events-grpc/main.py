import os
from concurrent import futures

import grpc

import events_pb2 as pb2
import events_pb2_grpc as pb2_grpc


def _normalize_location(raw: str) -> str:
    return " ".join((raw or "").strip().split())


class EventsService(pb2_grpc.EventsServiceServicer):
    def ValidateLocation(self, request: pb2.ValidateLocationRequest, context):
        normalized = _normalize_location(request.location)
        if not normalized:
            return pb2.ValidateLocationResponse(
                ok=False, normalized="", message="location is required"
            )
        if len(normalized) > 128:
            return pb2.ValidateLocationResponse(
                ok=False, normalized="", message="location is too long"
            )
        return pb2.ValidateLocationResponse(ok=True, normalized=normalized, message="ok")


def serve() -> None:
    port = int(os.environ.get("GRPC_PORT", "50051"))
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_EventsServiceServicer_to_server(EventsService(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()

