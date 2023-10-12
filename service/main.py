import uvicorn

from service.common.api.config import api_server_config
from service.common.api.main import create_application

app = create_application()


if __name__ == "__main__":
    uvicorn.run(app, host=api_server_config.host, port=api_server_config.port)
