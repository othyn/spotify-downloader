"""
Module which contains the web server related function
FastAPI routes/classes etc.
"""

import asyncio
import logging
import mimetypes
import os
from argparse import Namespace
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    HTTPException,
    Query,
    Response,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.types import Scope
from uvicorn import Server

from spotdl._version import __version__
from spotdl.download.downloader import Downloader
from spotdl.download.progress_handler import ProgressHandler, SongTracker
from spotdl.types.options import (
    DownloaderOptionalOptions,
    DownloaderOptions,
    WebOptions,
)
from spotdl.types.song import Song
from spotdl.utils.config import (
    DOWNLOADER_OPTIONS,
    create_settings_type,
    get_spotdl_path,
)
from spotdl.utils.search import get_search_results

__all__ = [
    "ALLOWED_ORIGINS",
    "SPAStaticFiles",
    "Client",
    "ApplicationState",
    "router",
    "app_state",
    "get_current_state",
    "get_client",
    "websocket_endpoint",
    "song_from_url",
    "query_search",
    "download_url",
    "download_file",
    "get_settings",
    "update_settings",
    "fix_mime_types",
]

ALLOWED_ORIGINS = [
    "http://localhost:8800",
    "http://127.0.0.1:8800",
    "https://localhost:8800",
    "https://127.0.0.1:8800",
]


class SPAStaticFiles(StaticFiles):
    """
    Override the static files to serve the index.html and other assets.
    """

    async def get_response(self, path: str, scope: Scope) -> Response:
        """
        Serve static files from the SPA.

        ### Arguments
        - path: The path to the file.
        - scope: The scope of the request.

        ### Returns
        - returns the response.
        """

        response = await super().get_response(path, scope)
        if response.status_code == 404:
            response = await super().get_response(".", scope)

        return response


class Client:
    """
    Holds the client's state.
    """

    def __init__(
        self,
        websocket: WebSocket,
        client_id: str,
    ):
        """
        Initialize the WebSocket handler.
        ### Arguments
        - websocket: The WebSocket instance.
        - client_id: The client's ID.
        - downloader_settings: The downloader settings.
        """

        self.downloader_settings = DownloaderOptions(
            **create_settings_type(
                Namespace(config=False),
                dict(app_state.downloader_settings),
                DOWNLOADER_OPTIONS,
            )  # type: ignore
        )

        self.websocket = websocket
        self.client_id = client_id
        self.downloader = Downloader(
            settings=self.downloader_settings, loop=app_state.loop
        )

        self.downloader.progress_handler.web_ui = True

    async def connect(self):
        """
        Called when a new client connects to the websocket.
        """

        await self.websocket.accept()

        # Add the connection to the list of connections
        app_state.clients.append(self)
        app_state.logger.info("Client %s connected", self.client_id)

    async def send_update(self, update: Dict[str, Any]):
        """
        Send an update to the client.

        ### Arguments
        - update: The update to send.
        """

        await self.websocket.send_json(update)

    def song_update(self, progress_handler: SongTracker, message: str):
        """
        Called when a song updates.

        ### Arguments
        - progress_handler: The progress handler.
        - message: The message to send.
        """

        update_message = {
            "song": progress_handler.song.json,
            "progress": progress_handler.progress,
            "message": message,
        }

        asyncio.run_coroutine_threadsafe(
            self.send_update(update_message), app_state.loop
        )

    @classmethod
    def get_instance(cls, client_id: str) -> Optional["Client"]:
        """
        Get the WebSocket instance for a client.

        ### Arguments
        - client_id: The client's ID.

        ### Returns
        - returns the WebSocket instance.
        """

        for instance in app_state.clients:
            if instance.client_id == client_id:
                return instance

        app_state.logger.error("Client %s not found", client_id)

        return None


class ApplicationState:
    """
    Class that holds the application state.
    """

    api: FastAPI
    server: Server
    loop: asyncio.AbstractEventLoop
    web_settings: WebOptions
    downloader_settings: DownloaderOptions
    clients: List[Client] = []
    logger: logging.Logger


router = APIRouter()
app_state: ApplicationState = ApplicationState()


def get_current_state() -> ApplicationState:
    """
    Get the current state of the application.

    ### Returns
    - returns the application state.
    """

    return app_state


def get_client(client_id: Union[str, None] = Query(default=None)) -> Client:
    """
    Get the client's state.

    ### Arguments
    - client_id: The client's ID.

    ### Returns
    - returns the client's state.
    """

    if client_id is None:
        raise HTTPException(status_code=400, detail="client_id is required")

    instance = Client.get_instance(client_id)
    if instance is None:
        raise HTTPException(status_code=404, detail="client not found")

    return instance


@router.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    Websocket endpoint.

    ### Arguments
    - websocket: The WebSocket instance.
    """

    await Client(websocket, client_id).connect()

    try:
        while True:
            await websocket.receive_json()
    except WebSocketDisconnect:
        instance = Client.get_instance(client_id)
        if instance:
            app_state.clients.remove(instance)

        if (
            len(app_state.clients) == 0
            and app_state.web_settings["keep_alive"] is False
        ):
            app_state.logger.debug(
                "No active connections, waiting 1s before shutting down"
            )

            await asyncio.sleep(1)

            # Wait 1 second before shutting down
            # This is to prevent the server from shutting down when a client
            # disconnects and reconnects quickly (e.g. when refreshing the page)
            if len(app_state.clients) == 0:
                # Perform a clean exit
                app_state.logger.info("Shutting down server, no active connections")
                app_state.server.force_exit = True
                app_state.server.should_exit = True
                await app_state.server.shutdown()


@router.get("/api/song/url", response_model=None)
def song_from_url(url: str) -> Song:
    """
    Search for a song on spotify using url.

    ### Arguments
    - url: The url to search.

    ### Returns
    - returns the first result as a Song object.
    """

    return Song.from_url(url)


@router.get("/api/songs/search", response_model=None)
def query_search(query: str) -> List[Song]:
    """
    Parse search term and return list of Song objects.

    ### Arguments
    - query: The query to parse.

    ### Returns
    - returns a list of Song objects.
    """

    return get_search_results(query)


@router.post("/api/download/url")
async def download_url(
    url: str,
    client: Client = Depends(get_client),
    state: ApplicationState = Depends(get_current_state),
) -> Optional[str]:
    """
    Download songs using Song url.

    ### Arguments
    - url: The url to download.

    ### Returns
    - returns the file path if the song was downloaded.
    """

    if state.web_settings.get("web_use_output_dir", False):
        client.downloader.settings["output"] = client.downloader_settings["output"]
    else:
        client.downloader.settings["output"] = str(
            (get_spotdl_path() / f"web/sessions/{client.client_id}").absolute()
        )

    client.downloader.progress_handler = ProgressHandler(
        simple_tui=True,
        update_callback=client.song_update,
    )

    try:
        # Fetch song metadata
        song = Song.from_url(url)

        # Download Song
        _, path = await client.downloader.pool_download(song)

        if path is None:
            state.logger.error(f"Failure downloading {song.name}")

            raise HTTPException(
                status_code=500, detail=f"Error downloading: {song.name}"
            )

        return str(path.absolute())

    except Exception as exception:
        state.logger.error(f"Error downloading! {exception}")

        raise HTTPException(
            status_code=500, detail=f"Error downloading: {exception}"
        ) from exception


@router.get("/api/download/file")
async def download_file(
    file: str,
    client: Client = Depends(get_client),
    state: ApplicationState = Depends(get_current_state),
):
    """
    Download file using path.

    ### Arguments
    - file: The file path.
    - client: The client's state.

    ### Returns
    - returns the file response, filename specified to return as attachment.
    """

    expected_path = str((get_spotdl_path() / "web/sessions").absolute())
    if state.web_settings.get("web_use_output_dir", False):
        expected_path = str(
            Path(client.downloader_settings["output"].split("{", 1)[0]).absolute()
        )

    if (not file.endswith(client.downloader_settings["format"])) or (
        not file.startswith(expected_path)
    ):
        raise HTTPException(status_code=400, detail="Invalid download path.")

    return FileResponse(
        file,
        filename=os.path.basename(file),
    )


@router.get("/api/settings")
def get_settings(
    client: Client = Depends(get_client),
) -> DownloaderOptions:
    """
    Get client settings.

    ### Arguments
    - client: The client's state.

    ### Returns
    - returns the settings.
    """

    return client.downloader_settings


@router.post("/api/settings/update")
def update_settings(
    settings: DownloaderOptionalOptions,
    client: Client = Depends(get_client),
    state: ApplicationState = Depends(get_current_state),
) -> DownloaderOptions:
    """
    Update client settings, and re-initialize downloader.

    ### Arguments
    - settings: The settings to change.
    - client: The client's state.
    - state: The application state.

    ### Returns
    - returns True if the settings were changed.
    """

    # Create shallow copy of settings
    settings_cpy = client.downloader_settings.copy()

    # Update settings with new settings that are not None
    settings_cpy.update({k: v for k, v in settings.items() if v is not None})  # type: ignore

    state.logger.info(f"Applying settings: {settings_cpy}")

    new_settings = DownloaderOptions(**settings_cpy)  # type: ignore

    # Re-initialize downloader
    client.downloader = Downloader(
        new_settings,
        loop=state.loop,
    )

    return new_settings


def fix_mime_types():
    """Fix incorrect entries in the `mimetypes` registry.
    On Windows, the Python standard library's `mimetypes` reads in
    mappings from file extension to MIME type from the Windows
    registry. Other applications can and do write incorrect values
    to this registry, which causes `mimetypes.guess_type` to return
    incorrect values, which causes spotDL to fail to render on
    the frontend.
    This method hard-codes the correct mappings for certain MIME
    types that are known to be either used by TensorBoard or
    problematic in general.
    """

    # Known to be problematic when Visual Studio is installed:
    # <https://github.com/tensorflow/tensorboard/issues/3120>
    # https://github.com/spotDL/spotify-downloader/issues/1540
    mimetypes.add_type("application/javascript", ".js")

    # Not known to be problematic, but used by spotDL:
    mimetypes.add_type("text/css", ".css")
    mimetypes.add_type("image/svg+xml", ".svg")
    mimetypes.add_type("text/html", ".html")
