"""
CLI entry point to launch the Indic Speech-to-English translation server.
"""
import argparse
import uvicorn
from config import SERVER_HOST, SERVER_PORT


def main():
    parser = argparse.ArgumentParser(description="Start the Indic Speech-to-English Translation Server")
    parser.add_argument(
        "--host",
        type=str,
        default=SERVER_HOST,
        help=f"Host address to bind (default: {SERVER_HOST})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=SERVER_PORT,
        help=f"Port to bind (default: {SERVER_PORT})",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )
    args = parser.parse_args()

    print(f"Starting Speech Translation Server on http://{args.host}:{args.port}")
    uvicorn.run("server:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
