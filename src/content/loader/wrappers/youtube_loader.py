from typing import List
from langchain_community.document_loaders import YoutubeLoader
from langchain_core.documents import Document


class YouTubeContentLoader:
    """
    Wrapper for loading YouTube video transcripts using LangChain's YoutubeLoader.

    Uses add_video_info=False to rely only on youtube-transcript-api,
    avoiding the unreliable pytube dependency.
    """

    def __init__(self, url: str):
        """
        Initialize YouTube content loader.

        Args:
            url: YouTube video URL
        """
        self.url = url
        # Use add_video_info=False to avoid pytube dependency
        # This uses only youtube-transcript-api which is more reliable
        self.loader = YoutubeLoader.from_youtube_url(
            url,
            add_video_info=False,
            language=["en", "en-US"],  # Prefer English transcripts
        )

    def load(self) -> List[Document]:
        """
        Load YouTube video transcript.

        Returns:
            List of Document objects containing the video transcript

        Raises:
            Exception: If transcript cannot be fetched
        """
        try:
            return self.loader.load()
        except Exception as e:
            raise Exception(
                f"Failed to fetch transcript from {self.url}: {str(e)}\n"
                f"Make sure the video has captions/subtitles available."
            ) from e
