import abc


class GifFinderPort(abc.ABC):
    @abc.abstractmethod
    def find_gif(self, mood: str) -> str:
        pass
