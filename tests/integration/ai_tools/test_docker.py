from pathlib import Path

from system_assistant.core.config import ROOT
from system_assistant.infrastructure.services.ai.tools.docker import (
    build_docker_image, run_docker_container, stop_docker_container
)


class TestDockerTools:
    dockerfile: str = 'Dockerfile.test'
    path: Path = ROOT
    tag: str = 'test-docker-tools'
    container_id: str

    def test_can_build_docker_image(self):
        result = build_docker_image(
            tag=self.tag, path=str(self.path), dockerfile=self.dockerfile,
        )
        assert isinstance(result, dict)
        assert 'image' in result
        assert self.tag in result['image']['tag'][0]

    def test_can_run_docker_container(self):
        name = f'name-{self.tag}'
        result = run_docker_container(image_name=self.tag, auto_remove=True, name=name)
        assert isinstance(result, dict)
        assert 'container' in result
        assert result['container']['name'] == name
        assert result['container']['id']

        self.__class__.container_id = result['container']['id']

    def test_can_stop_docker_container(self):
        result = stop_docker_container(self.container_id)
        assert isinstance(result, dict)
        assert result['success'] is True


class TestDockerComposeTools:
    ...
